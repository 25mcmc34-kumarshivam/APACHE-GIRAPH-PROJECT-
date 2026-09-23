#!/usr/bin/env python3
"""Check source sequences, find exact SMALL answers, or try a greedy heuristic.

This is a local reference checker, not a Giraph/distributed implementation.
It reads our existing ``vertex neighbour:weight ...`` text format. Weights
are parsed but ignored because ordinary graph burning counts edges, not costs.
"""

import argparse
# deque is a first-in/first-out queue. BFS needs this queue to visit a
# vertex's neighbours before vertices that are farther away.
from collections import deque
from pathlib import Path


class SearchLimitReached(Exception):
    """The search stopped before it could prove an answer."""


def read_graph(path):
    """Read one .txt file or all .txt parts in a directory.

    Return {vertex_id: {neighbour_id, ...}}. Each vertex must have exactly
    one input line, even when the dataset is divided into several files.
    """
    # A directory is how our HDFS-style dataset is represented locally:
    # part-01.txt, part-02.txt, etc. Sorting makes the read order repeatable.
    files = sorted(path.glob("*.txt")) if path.is_dir() else [path]
    if not files:
        raise ValueError("No .txt graph files found")

    graph = {}  # Example: {1: {2, 3}, 2: {1}}
    for file_path in files:
        with file_path.open(encoding="utf-8") as stream:
            for line_number, raw in enumerate(stream, 1):
                line = raw.strip()  # Remove trailing newline/outer spaces.
                if not line or line.startswith("#"):
                    continue
                fields = line.split()  # "1 2:1 3:1" -> ["1", "2:1", "3:1"]
                try:
                    vertex = int(fields[0])
                except ValueError as error:
                    raise ValueError(
                        f"{file_path}:{line_number}: invalid vertex ID"
                    ) from error
                if vertex in graph:
                    raise ValueError(f"Vertex {vertex} is defined twice")
                neighbours = set()  # A set detects repeated edges.
                for field in fields[1:]:
                    try:
                        # "3:1" means neighbour ID 3 and edge weight 1.
                        # The weight is checked for syntax, then ignored:
                        # ordinary burning spreads one EDGE per round.
                        neighbour_text, weight_text = field.split(":", 1)
                        neighbour = int(neighbour_text)
                        float(weight_text)
                    except ValueError as error:
                        raise ValueError(
                            f"{file_path}:{line_number}: expected neighbour:weight, "
                            f"got {field!r}"
                        ) from error
                    if neighbour in neighbours:
                        raise ValueError(
                            f"{file_path}:{line_number}: repeated neighbour {neighbour}"
                        )
                    neighbours.add(neighbour)
                graph[vertex] = neighbours

    if not graph:
        raise ValueError("Graph is empty")
    # Check after reading every file, because a neighbour's own line may be
    # in a later part file. Undirected edges must appear in both directions.
    for vertex, neighbours in graph.items():
        for neighbour in neighbours:
            if neighbour not in graph:
                raise ValueError(f"Edge {vertex}->{neighbour} has no vertex line")
            if vertex not in graph[neighbour]:
                raise ValueError(
                    f"Edge {vertex}->{neighbour} is not listed in reverse; "
                    "this checker needs an undirected graph"
                )
    return graph


def distances_from(graph, source):
    """BFS: number of edges on a shortest route from source to each vertex.

    Disconnected vertices are absent from the returned dictionary, which
    later acts like an infinite distance: fire cannot cross between groups.
    """
    distances = {source: 0}
    queue = deque([source])
    while queue:  # Continue until there is no reachable vertex left to visit.
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in distances:  # First BFS visit is shortest.
                distances[neighbour] = distances[vertex] + 1
                queue.append(neighbour)
    return distances


def burn_rounds(graph, sequence):
    """Return each vertex's first burn round; None means not yet burned.

    Reject sources absent from the graph, repeated sources, and a source
    already burned BEFORE its chosen round. Arrival in the SAME round is
    allowed: it was unburned at the start of that round.
    """
    if not sequence:
        raise ValueError("Choose at least one source")
    # A source must be a real vertex, and one vertex cannot be selected twice.
    unknown = [source for source in sequence if source not in graph]
    if unknown:
        raise ValueError(f"Source {unknown[0]} is not a vertex in this graph")
    if len(set(sequence)) != len(sequence):
        raise ValueError("A source vertex was selected more than once")

    distances = {source: distances_from(graph, source) for source in sequence}
    for round_number, candidate in enumerate(sequence, 1):
        for earlier_round, source in enumerate(sequence[:round_number - 1], 1):
            # Fire from an earlier source reaches this candidate in round
            # earlier_round + distance. A strict '<' means arrival in the
            # SAME round as selection is still allowed.
            distance = distances[source].get(candidate, float("inf"))
            if distance < round_number - earlier_round:
                raise ValueError(
                    f"Source {candidate} was already burned before round "
                    f"{round_number} by source {source}"
                )

    result = {}
    for vertex in graph:
        # The earliest possible burn time is the minimum over all sources.
        # A disconnected source has no distance to this vertex, so it is
        # omitted from arrivals. If no source reaches it by the final round,
        # store None (printed as UNBURNED), not a huge floating-point value.
        arrivals = [
            round_number + distances[source][vertex]
            for round_number, source in enumerate(sequence, 1)
            if vertex in distances[source]
        ]
        earliest = min(arrivals, default=float("inf"))
        result[vertex] = earliest if earliest <= len(sequence) else None
    return result


def find_sequence(graph, max_states=500_000):
    """Try k=1,2,... and return the first complete valid source sequence.

    A source at round i covers vertices at distance at most k-i by the end
    of round k. A later source must not have burned *before* its own round.
    Search is exhaustive unless the explicit state budget is exceeded.
    """
    vertices = sorted(graph)  # Candidate IDs in a repeatable order.
    # A bit position represents one vertex. For vertices [1,2,3], bits
    # 001, 010, 100 mean that vertices 1, 2, 3 are covered, respectively.
    index = {vertex: position for position, vertex in enumerate(vertices)}
    # Precompute BFS distances from EVERY possible source. The search will
    # ask many distance questions; doing BFS once per source saves work.
    distances = {vertex: distances_from(graph, vertex) for vertex in vertices}
    # Example for three vertices: binary 111 means all three are burned.
    all_mask = (1 << len(vertices)) - 1
    states = 0  # Count guesses examined so we can stop a costly search.

    # Start at one round. The first possible length is the exact minimum,
    # because all shorter lengths have already been checked and rejected.
    for rounds in range(1, len(vertices) + 1):
        coverage = {}  # (round, source) -> vertices burned by final round.
        for round_number in range(1, rounds + 1):
            # If total rounds=3: source chosen in round 1 has 2 spreading
            # steps, source in round 2 has 1, and source in round 3 has 0.
            radius = rounds - round_number
            for vertex in vertices:
                coverage[round_number, vertex] = sum(
                    1 << index[other]
                    for other, distance in distances[vertex].items()
                    if distance <= radius
                )

        def search(round_number, chosen, covered):
            """Try each possible next source (depth-first/backtracking)."""
            nonlocal states
            states += 1
            if states > max_states:
                raise SearchLimitReached(
                    f"Stopped after {max_states} search states; "
                    "no exact answer was proved"
                )
            # We selected all sources. A sequence succeeds only if every
            # vertex's bit is now present in the covered mask.
            if round_number > rounds:
                return chosen if covered == all_mask else None

            for candidate in vertices:
                # Earlier fire can reach candidate during its own round, but
                # it must not have reached it in an earlier round.
                if any(
                    distances[source].get(candidate, float("inf"))
                    < round_number - source_round
                    for source_round, source in enumerate(chosen, 1)
                ):
                    continue
                # Add this source to the ordered sequence. Bitwise OR joins
                # its coverage to what previous sources already covered.
                result = search(
                    round_number + 1,
                    chosen + (candidate,),
                    covered | coverage[round_number, candidate],
                )
                if result is not None:  # A valid complete sequence was found.
                    return result
            return None  # This partial sequence cannot finish successfully.

        result = search(1, (), 0)
        if result is not None:
            return result, states

    raise AssertionError("No sequence found; every finite graph is burnable")


def greedy_sequence(graph):
    """Find a valid covering sequence quickly, without an optimality proof.

    Try a proposed total length k=1,2,... . At each round choose the legal
    source whose radius (k-round) reaches the most *new* vertices by round k.
    Ties use the smallest ID, making repeated runs deterministic. This is a
    heuristic: it may need more rounds than the exact minimum.
    """
    vertices = sorted(graph)
    distances = {vertex: distances_from(graph, vertex) for vertex in vertices}
    all_vertices = set(vertices)

    for total_rounds in range(1, len(vertices) + 1):
        # Rebuild the proposal from scratch for each proposed number of
        # rounds; the useful radius of a source changes with that number.
        chosen = []
        covered = set()
        for round_number in range(1, total_rounds + 1):
            radius = total_rounds - round_number
            best = None
            best_new = -1
            for candidate in vertices:
                # Ignore a source that fire reached in an earlier round.
                if any(
                    distances[source].get(candidate, float("inf"))
                    < round_number - earlier_round
                    for earlier_round, source in enumerate(chosen, 1)
                ):
                    continue
                would_cover = {
                    vertex for vertex, distance in distances[candidate].items()
                    if distance <= radius
                }
                new_count = len(would_cover - covered)
                # The sorted vertex order makes equal-score ties pick the
                # smallest ID; this is deterministic but not always best.
                if new_count > best_new:
                    best, best_new = candidate, new_count
            if best is None:
                break
            chosen.append(best)
            covered.update(
                vertex for vertex, distance in distances[best].items()
                if distance <= radius
            )
        if len(chosen) == total_rounds and covered == all_vertices:
            # This is a valid coverage witness. Greedy did NOT check every
            # source order, so this alone does not prove minimum rounds.
            return tuple(chosen)

    raise AssertionError("No greedy sequence found; check graph/search logic")


def main():
    """Read command-line arguments, run the checker, and explain its result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="one graph .txt file or folder of .txt parts")
    mode = parser.add_mutually_exclusive_group()
    # Default mode is exact search for <=10 vertices. These flags select a
    # faster heuristic or validate a human/Giraph source sequence instead.
    mode.add_argument(
        "--greedy", action="store_true",
        help="choose sources quickly; result is NOT guaranteed minimum",
    )
    mode.add_argument(
        "--check-sequence", metavar="IDS",
        help="validate a colon-separated sequence, e.g. 3:8:6",
    )
    parser.add_argument("--max-states", type=int, default=500_000)
    args = parser.parse_args()
    if args.max_states < 1:
        parser.error("--max-states must be positive")
    try:
        graph = read_graph(args.graph)
        if args.check_sequence:
            try:
                sequence = tuple(int(part) for part in args.check_sequence.split(":"))
            except ValueError as error:
                raise ValueError("Use colon-separated numeric source IDs") from error
            rounds = burn_rounds(graph, sequence)
        elif args.greedy:
            sequence = greedy_sequence(graph)
            rounds = burn_rounds(graph, sequence)
        else:
            # Exact exhaustive search is a teaching/reference tool only.
            if len(graph) > 10:
                raise ValueError(
                    "Exact search is limited to 10 vertices; use --greedy "
                    "for a larger graph"
                )
            sequence, states = find_sequence(graph, args.max_states)
            rounds = burn_rounds(graph, sequence)
    # Errors and a search-budget stop are NOT exact answers; exit nonzero.
    except (OSError, ValueError, SearchLimitReached) as error:
        parser.exit(2, f"ERROR: {error}\n")

    print(f"Vertices: {len(graph)}")
    if args.check_sequence:
        print(f"Checked rounds: {len(sequence)}")
    elif args.greedy:
        print(f"Heuristic rounds (NOT proven minimum): {len(sequence)}")
    else:
        print(f"Minimum rounds (exact for this small graph): {len(sequence)}")
    print("Source sequence: " + ":".join(str(vertex) for vertex in sequence))
    if not args.greedy and not args.check_sequence:
        print(f"Search states checked: {states}")
    print(f"Burned by final round: {sum(value is not None for value in rounds.values())}/{len(graph)}")
    for vertex in sorted(rounds):
        print(f"{vertex}\t{rounds[vertex] if rounds[vertex] is not None else 'UNBURNED'}")
    print("Use this sequence with the Giraph runner to check its burn rounds.")


if __name__ == "__main__":
    # Importing this file for tests should not launch the CLI automatically.
    main()

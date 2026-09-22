#!/usr/bin/env python3
"""Find an exact burning sequence for a SMALL undirected text graph.

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


def main():
    """Read command-line arguments, run the checker, and explain its result."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="one graph .txt file or folder of .txt parts")
    parser.add_argument("--max-states", type=int, default=500_000)
    args = parser.parse_args()
    if args.max_states < 1:
        parser.error("--max-states must be positive")
    try:
        graph = read_graph(args.graph)
        # This is a learning/reference tool, not a scalable implementation.
        if len(graph) > 10:
            raise ValueError(
                "This exact learning checker is limited to 10 vertices; "
                "use a heuristic for larger graphs"
            )
        sequence, states = find_sequence(graph, args.max_states)
    # Errors and a search-budget stop are NOT exact answers; exit nonzero.
    except (OSError, ValueError, SearchLimitReached) as error:
        parser.exit(2, f"ERROR: {error}\n")

    print(f"Vertices: {len(graph)}")
    print(f"Minimum rounds (exact for this small graph): {len(sequence)}")
    print("Source sequence: " + ":".join(str(vertex) for vertex in sequence))
    print(f"Search states checked: {states}")
    print("Use this sequence with the Giraph runner to check its burn rounds.")


if __name__ == "__main__":
    # Importing this file for tests should not launch the CLI automatically.
    main()

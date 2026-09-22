#!/usr/bin/env python3
"""Find an exact burning sequence for a SMALL undirected text graph.

This is a local reference checker, not a Giraph/distributed implementation.
It reads our existing ``vertex neighbour:weight ...`` text format. Weights
are parsed but ignored because ordinary graph burning counts edges, not costs.
"""

import argparse
from collections import deque
from pathlib import Path


class SearchLimitReached(Exception):
    """The search stopped before it could prove an answer."""


def read_graph(path):
    """Read one .txt file or all .txt parts in a directory."""
    files = sorted(path.glob("*.txt")) if path.is_dir() else [path]
    if not files:
        raise ValueError("No .txt graph files found")

    graph = {}
    for file_path in files:
        with file_path.open(encoding="utf-8") as stream:
            for line_number, raw in enumerate(stream, 1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                fields = line.split()
                try:
                    vertex = int(fields[0])
                except ValueError as error:
                    raise ValueError(
                        f"{file_path}:{line_number}: invalid vertex ID"
                    ) from error
                if vertex in graph:
                    raise ValueError(f"Vertex {vertex} is defined twice")
                neighbours = set()
                for field in fields[1:]:
                    try:
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
    """BFS: number of edges on a shortest route from source to each vertex."""
    distances = {source: 0}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in distances:
                distances[neighbour] = distances[vertex] + 1
                queue.append(neighbour)
    return distances


def find_sequence(graph, max_states=500_000):
    """Try k=1,2,... and return the first complete valid source sequence.

    A source at round i covers vertices at distance at most k-i by the end
    of round k. A later source must not have burned *before* its own round.
    Search is exhaustive unless the explicit state budget is exceeded.
    """
    vertices = sorted(graph)
    index = {vertex: position for position, vertex in enumerate(vertices)}
    distances = {vertex: distances_from(graph, vertex) for vertex in vertices}
    all_mask = (1 << len(vertices)) - 1
    states = 0

    for rounds in range(1, len(vertices) + 1):
        coverage = {}
        for round_number in range(1, rounds + 1):
            radius = rounds - round_number
            for vertex in vertices:
                coverage[round_number, vertex] = sum(
                    1 << index[other]
                    for other, distance in distances[vertex].items()
                    if distance <= radius
                )

        def search(round_number, chosen, covered):
            nonlocal states
            states += 1
            if states > max_states:
                raise SearchLimitReached(
                    f"Stopped after {max_states} search states; "
                    "no exact answer was proved"
                )
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
                result = search(
                    round_number + 1,
                    chosen + (candidate,),
                    covered | coverage[round_number, candidate],
                )
                if result is not None:
                    return result
            return None

        result = search(1, (), 0)
        if result is not None:
            return result, states

    raise AssertionError("No sequence found; every finite graph is burnable")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", type=Path, help="one graph .txt file or folder of .txt parts")
    parser.add_argument("--max-states", type=int, default=500_000)
    args = parser.parse_args()
    if args.max_states < 1:
        parser.error("--max-states must be positive")
    try:
        graph = read_graph(args.graph)
        if len(graph) > 10:
            raise ValueError(
                "This exact learning checker is limited to 10 vertices; "
                "use a heuristic for larger graphs"
            )
        sequence, states = find_sequence(graph, args.max_states)
    except (OSError, ValueError, SearchLimitReached) as error:
        parser.exit(2, f"ERROR: {error}\n")

    print(f"Vertices: {len(graph)}")
    print(f"Minimum rounds (exact for this small graph): {len(sequence)}")
    print("Source sequence: " + ":".join(str(vertex) for vertex in sequence))
    print(f"Search states checked: {states}")
    print("Use this sequence with the Giraph runner to check its burn rounds.")


if __name__ == "__main__":
    main()

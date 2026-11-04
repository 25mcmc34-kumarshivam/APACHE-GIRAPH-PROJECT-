#!/usr/bin/env python3
"""Convert a SNAP two-column edge list into Giraph adjacency-list parts.

SNAP files contain comment/header lines followed by ``source<TAB>target``.
This converter keeps only IDs below ``--max-node-id``, treats each retained
edge as undirected, removes self-loops/duplicates, keeps the largest
connected component, and writes the *unscheduled* format expected by
``prepare_random_burning_input.py``::

    vertex_id neighbour_id:1 neighbour_id:1 ...

It does not download data, choose sources, run Hadoop, or overwrite an
existing output directory. Run the random preparer afterwards to add the
source-round column required by Giraph's burning input reader.
"""

import argparse
from collections import deque
from pathlib import Path


def read_undirected_edges(path: Path, max_node_id: int):
    """Return an adjacency map for the selected SNAP ID range."""
    graph = {}
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line_number, raw in enumerate(stream, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) < 2:
                raise ValueError(f"{path}:{line_number}: expected two node IDs")
            try:
                left, right = int(fields[0]), int(fields[1])
            except ValueError as error:
                raise ValueError(f"{path}:{line_number}: non-integer edge") from error
            if left < 0 or right < 0:
                raise ValueError(f"{path}:{line_number}: node IDs must be non-negative")
            if left >= max_node_id or right >= max_node_id or left == right:
                continue
            graph.setdefault(left, set()).add(right)
            graph.setdefault(right, set()).add(left)
    if not graph:
        raise ValueError("no usable edges remained; increase --max-node-id")
    return graph


def largest_component(graph):
    """Return the largest connected component as a new adjacency map."""
    unseen = set(graph)
    best = set()
    while unseen:
        start = unseen.pop()
        component = {start}
        queue = deque([start])
        while queue:
            vertex = queue.popleft()
            for neighbour in graph[vertex]:
                if neighbour in unseen:
                    unseen.remove(neighbour)
                    component.add(neighbour)
                    queue.append(neighbour)
        if len(component) > len(best):
            best = component
    return {vertex: graph[vertex] & best for vertex in sorted(best)}


def write_parts(graph, output: Path, parts: int):
    """Write deterministic vertex-balanced unscheduled text parts."""
    vertices = sorted(graph)
    output.mkdir(parents=True)
    size, remainder = divmod(len(vertices), parts)
    offset = 0
    for part_number in range(1, parts + 1):
        count = size + (1 if part_number <= remainder else 0)
        selected = vertices[offset:offset + count]
        offset += count
        target = output / f"part-{part_number:02d}.txt"
        with target.open("w", encoding="utf-8", newline="\n") as stream:
            for vertex in selected:
                neighbours = " ".join(
                    f"{neighbour}:1" for neighbour in sorted(graph[vertex])
                )
                stream.write(f"{vertex}{(' ' + neighbours) if neighbours else ''}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="SNAP .txt edge-list file")
    parser.add_argument("output", type=Path, help="new directory for part-*.txt")
    parser.add_argument("--max-node-id", type=int, required=True,
                        help="keep IDs in [0, max-node-id); use a smaller value for a first test")
    parser.add_argument("--parts", type=int, default=4,
                        help="number of output parts (default: 4)")
    args = parser.parse_args()
    if args.max_node_id < 2 or args.parts < 1:
        parser.error("--max-node-id must be at least 2 and --parts at least 1")
    if not args.input.is_file():
        parser.error(f"input file does not exist: {args.input}")
    if args.output.exists():
        parser.error(f"output directory already exists: {args.output}")
    try:
        graph = largest_component(read_undirected_edges(args.input, args.max_node_id))
        write_parts(graph, args.output, args.parts)
    except (OSError, ValueError) as error:
        parser.exit(2, f"ERROR: {error}\n")
    edges = sum(map(len, graph.values())) // 2
    print(f"Vertices: {len(graph)} | undirected edges: {edges} | parts: {args.parts}")
    print(f"Saved unscheduled adjacency graph in {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create a reproducible undirected grid graph in split Giraph text files.

Rows and columns determine the topology; vertex IDs increase left-to-right,
top-to-bottom from 1. Each vertex connects only to its horizontal/vertical
grid neighbours. Every undirected edge is written at both endpoints with
weight 1. This script makes graph data; it does not choose burning sources.
"""

import argparse
import json
from pathlib import Path


def make_grid(rows, columns):
    """Return {vertex: sorted_neighbours} for a rectangular grid."""
    if rows < 2 or columns < 2:
        raise ValueError("rows and columns must both be at least 2")
    graph = {}
    for row in range(rows):
        for column in range(columns):
            vertex = row * columns + column + 1
            neighbours = []
            if row > 0:
                neighbours.append(vertex - columns)
            if row + 1 < rows:
                neighbours.append(vertex + columns)
            if column > 0:
                neighbours.append(vertex - 1)
            if column + 1 < columns:
                neighbours.append(vertex + 1)
            graph[vertex] = sorted(neighbours)
    return graph


def split_parts(graph, part_count):
    """Return ordered text parts, with each vertex defined exactly once."""
    if not 1 <= part_count <= len(graph):
        raise ValueError("parts must be between 1 and the number of vertices")
    vertices = sorted(graph)
    parts = []
    for index in range(part_count):
        start = index * len(vertices) // part_count
        end = (index + 1) * len(vertices) // part_count
        parts.append("".join(
            "{} {}\n".format(
                vertex, " ".join("{}:1".format(neighbour) for neighbour in graph[vertex])
            )
            for vertex in vertices[start:end]
        ))
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new directory for part-*.txt")
    parser.add_argument("--rows", type=int, required=True)
    parser.add_argument("--columns", type=int, required=True)
    parser.add_argument("--parts", type=int, required=True)
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("output path already exists; choose a new directory")
        graph = make_grid(args.rows, args.columns)
        parts = split_parts(graph, args.parts)
        args.output.mkdir(parents=True)
        for index, content in enumerate(parts, 1):
            (args.output / "part-{:02d}.txt".format(index)).write_text(
                content, encoding="utf-8"
            )
        edges = sum(map(len, graph.values())) // 2
        (args.output / "topology.json").write_text(
            json.dumps({"type": "undirected_grid", "rows": args.rows,
                        "columns": args.columns, "vertices": len(graph),
                        "undirected_edges": edges, "parts": args.parts}, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        parser.exit(2, "ERROR: {}\n".format(error))
    print("Grid: {} rows x {} columns | vertices: {} | undirected edges: {} | parts: {}".format(
        args.rows, args.columns, len(graph), edges, args.parts
    ))


if __name__ == "__main__":
    main()

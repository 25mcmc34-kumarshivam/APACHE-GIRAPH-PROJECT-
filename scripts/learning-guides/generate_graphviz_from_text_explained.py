#!/usr/bin/env python3
"""Teaching copy of scripts/generate_graphviz_from_text.py.

English: validate all text graph parts, calculate BFS levels, and generate a
Graphviz DOT diagram containing every directed edge.
Hinglish: saari part files ko ek graph maan kar check karta hai, BFS distance
nikalta hai, aur exact graph diagram ka DOT source banata hai.

Input line: vertex_id neighbor_id:weight neighbor_id:weight ...
This script uses only Python's standard library; Graphviz is needed later only
to convert the resulting .dot file to SVG/PNG.
"""

from __future__ import annotations  # Modern type hints on older Python versions.

import argparse  # Command-line arguments read karne ke liye.
from collections import deque  # Efficient FIFO queue used by BFS.
from pathlib import Path  # Safe, readable filesystem path operations.


def read_graph(input_dir: Path):
    """Read every .txt part and return graph data plus source-file evidence."""
    adjacency: dict[int, list[int]] = {}  # source vertex -> ordered neighbors
    weights: dict[tuple[int, int], float] = {}  # (source,target) -> weight
    defined_in: dict[int, str] = {}  # vertex -> part filename, useful in errors
    input_files = sorted(input_dir.glob("*.txt"))  # deterministic part order

    if not input_files:
        raise ValueError(f"No .txt files found in {input_dir}")

    for input_file in input_files:
        # enumerate starts at 1 so an error points to the editor's line number.
        for line_number, raw_line in enumerate(
            input_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line or line.startswith("#"):  # blank/comment lines ignored
                continue

            tokens = line.split()  # whitespace separates vertex/edge tokens
            try:
                vertex_id = int(tokens[0])
            except ValueError as exc:
                raise ValueError(
                    f"{input_file}:{line_number}: invalid vertex ID"
                ) from exc

            # Each vertex must be defined exactly once, even across part files.
            if vertex_id in adjacency:
                raise ValueError(
                    f"Duplicate vertex {vertex_id} in {input_file}:{line_number}; "
                    f"already defined in {defined_in[vertex_id]}"
                )

            adjacency[vertex_id] = []
            defined_in[vertex_id] = input_file.name

            for token in tokens[1:]:
                if ":" not in token:
                    raise ValueError(
                        f"{input_file}:{line_number}: edge '{token}' must be "
                        "neighbor_id:weight"
                    )
                neighbor_text, weight_text = token.split(":", 1)
                try:
                    neighbor = int(neighbor_text)
                    weight = float(weight_text)
                except ValueError as exc:
                    raise ValueError(
                        f"{input_file}:{line_number}: invalid edge '{token}'"
                    ) from exc
                adjacency[vertex_id].append(neighbor)
                weights[(vertex_id, neighbor)] = weight

    # A target may live in a different part, but it must be defined somewhere.
    referenced = {target for targets in adjacency.values() for target in targets}
    undefined = sorted(referenced.difference(adjacency))
    if undefined:
        raise ValueError(f"Referenced but undefined vertices: {undefined}")

    return adjacency, weights, defined_in, input_files


def bfs(adjacency: dict[int, list[int]], source: int):
    """Return minimum hop distances and one deterministic BFS parent tree."""
    if source not in adjacency:
        raise ValueError(f"Source vertex {source} is not defined")

    distance = {source: 0}  # Source se source ka hop distance zero.
    parent: dict[int, int] = {}  # First discover karne wala vertex.
    queue = deque([source])

    while queue:
        current = queue.popleft()  # Oldest queued vertex first = breadth-first.
        for neighbor in adjacency[current]:
            if neighbor not in distance:  # First visit gives minimum hop count.
                distance[neighbor] = distance[current] + 1
                parent[neighbor] = current
                queue.append(neighbor)

    return distance, parent


def dot_quote(text: str) -> str:
    """Escape characters that would otherwise break quoted DOT attributes."""
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_dot(adjacency, weights, defined_in, source: int) -> str:
    """Build DOT text; blue edges show one BFS tree, gray shows other edges."""
    distance, parent = bfs(adjacency, source)
    tree_edges = {(parent[v], v) for v in parent}
    edge_count = sum(len(targets) for targets in adjacency.values())
    unique_weights = sorted(set(weights.values()))
    show_weight_labels = len(unique_weights) != 1
    weight_summary = (
        "weights shown" if show_weight_labels else f"weights = {unique_weights[0]:g}"
    )

    lines = [
        "digraph GiraphGraph {", "  graph [rankdir=LR, bgcolor=\"#ffffff\",",
        "    pad=0.3, nodesep=0.45, ranksep=1.0, splines=polyline,",
        "    overlap=false, outputorder=edgesfirst, labelloc=\"t\", fontsize=18,",
        f"    label=\"{len(adjacency)} nodes | {edge_count} edges | BFS source {source}\\nBlue = BFS tree | Gray = other edges\\n{weight_summary}\"",
        "  ];",
        "  node [shape=circle, style=filled, fontname=\"Arial\", fontsize=10, width=0.75, height=0.75, fixedsize=true];",
        "  edge [color=\"#9ca3af\", arrowsize=0.55, penwidth=0.8];", "",
    ]

    for vertex in sorted(adjacency):
        if vertex == source:
            style = 'fillcolor="#fbbf24", color="#92400e", penwidth=2.4'
        elif vertex not in distance:
            style = 'fillcolor="#e5e7eb", color="#6b7280"'
        else:
            style = 'fillcolor="#dbeafe", color="#1d4ed8"'
        distance_text = str(distance[vertex]) if vertex in distance else "inf"
        tooltip = dot_quote(
            f"Vertex {vertex}; BFS distance {distance_text}; defined in {defined_in[vertex]}"
        )
        lines.append(
            f'  n{vertex} [label="{vertex}\\nd={distance_text}", {style}, tooltip="{tooltip}"];'
        )

    # Same-distance vertices get the same visual rank/column.
    for level in sorted(set(distance.values())):
        members = " ".join(
            f"n{v}" for v in sorted(distance) if distance[v] == level
        )
        lines.append(f"  {{ rank=same; {members}; }}")

    for start, targets in adjacency.items():
        for target in targets:
            weight = weights[(start, target)]
            label = f', label="{weight:g}", fontsize=9' if show_weight_labels else ""
            if (start, target) in tree_edges:
                attrs = f'color="#2563eb", penwidth=2.2{label}'
            else:
                attrs = f'color="#9ca3af80", penwidth=0.7, constraint=false{label}'
            lines.append(f"  n{start} -> n{target} [{attrs}];")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="directory of graph parts")
    parser.add_argument("output_dot", type=Path, help="Graphviz .dot output")
    parser.add_argument("--source", type=int, default=1, help="BFS source")
    args = parser.parse_args()

    adjacency, weights, defined_in, files = read_graph(args.input_dir)
    dot = build_dot(adjacency, weights, defined_in, args.source)
    args.output_dot.parent.mkdir(parents=True, exist_ok=True)
    args.output_dot.write_text(dot, encoding="utf-8", newline="\n")
    print(f"Input files: {len(files)}")
    print(f"Vertices: {len(adjacency)}")
    print(f"Directed edges: {sum(len(v) for v in adjacency.values())}")
    print(f"DOT written: {args.output_dot}")


if __name__ == "__main__":
    # Prevents main() from running when another Python file imports this module.
    main()

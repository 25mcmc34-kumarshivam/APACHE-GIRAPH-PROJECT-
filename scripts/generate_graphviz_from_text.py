#!/usr/bin/env python3
"""Generate an exact Graphviz diagram from Giraph text adjacency files.

Input record format:
    vertex_id neighbor_id:weight neighbor_id:weight ...

The generated diagram contains every directed edge.  It also highlights one
BFS discovery tree from the requested source while keeping all other edges in
the background.  Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
from collections import deque
from pathlib import Path


def read_graph(input_dir: Path):
    """Read all .txt parts and return adjacency, weights, and source files."""
    adjacency: dict[int, list[int]] = {}
    weights: dict[tuple[int, int], float] = {}
    defined_in: dict[int, str] = {}
    input_files = sorted(input_dir.glob("*.txt"))

    if not input_files:
        raise ValueError(f"No .txt files found in {input_dir}")

    for input_file in input_files:
        for line_number, raw_line in enumerate(
            input_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            tokens = line.split()
            try:
                vertex_id = int(tokens[0])
            except ValueError as exc:
                raise ValueError(
                    f"{input_file}:{line_number}: invalid vertex ID"
                ) from exc

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

    referenced = {target for targets in adjacency.values() for target in targets}
    undefined = sorted(referenced.difference(adjacency))
    if undefined:
        raise ValueError(f"Referenced but undefined vertices: {undefined}")

    return adjacency, weights, defined_in, input_files


def bfs(adjacency: dict[int, list[int]], source: int):
    """Return minimum hop distances and one deterministic BFS parent tree."""
    if source not in adjacency:
        raise ValueError(f"Source vertex {source} is not defined")

    distance = {source: 0}
    parent: dict[int, int] = {}
    queue = deque([source])

    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distance:
                distance[neighbor] = distance[current] + 1
                parent[neighbor] = current
                queue.append(neighbor)

    return distance, parent


def dot_quote(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def build_dot(
    adjacency: dict[int, list[int]],
    weights: dict[tuple[int, int], float],
    defined_in: dict[int, str],
    source: int,
) -> str:
    """Create Graphviz DOT with BFS ranks and all original graph edges."""
    distance, parent = bfs(adjacency, source)
    tree_edges = {(parent[vertex], vertex) for vertex in parent}
    edge_count = sum(len(targets) for targets in adjacency.values())
    unique_weights = sorted(set(weights.values()))
    if len(unique_weights) == 1:
        weight_summary = f"weights = {unique_weights[0]:g}"
        show_weight_labels = False
    else:
        weight_summary = "weights shown"
        show_weight_labels = True

    lines = [
        "digraph ThirtyNodeGraph {",
        "  graph [",
        "    rankdir=LR,",
        "    bgcolor=\"#ffffff\",",
        "    pad=0.3,",
        "    nodesep=0.45,",
        "    ranksep=1.0,",
        "    splines=polyline,",
        "    overlap=false,",
        "    outputorder=edgesfirst,",
        "    labelloc=\"t\",",
        "    fontsize=18,",
        f"    label=\"{len(adjacency)} nodes | {edge_count} edges | BFS source {source}\\nBlue = BFS tree | Gray = other edges\\n{weight_summary}\"",
        "  ];",
        "  node [shape=circle, style=filled, fillcolor=\"#dbeafe\", color=\"#1d4ed8\", fontname=\"Arial\", fontsize=10, width=0.75, height=0.75, fixedsize=true];",
        "  edge [color=\"#9ca3af\", arrowsize=0.55, penwidth=0.8];",
        "",
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

    lines.append("")
    for level in sorted(set(distance.values())):
        members = " ".join(
            f"n{vertex}" for vertex in sorted(distance) if distance[vertex] == level
        )
        lines.append(f"  {{ rank=same; {members}; }}")

    lines.extend(["", "  // Blue edges form one deterministic BFS discovery tree."])
    for start, targets in adjacency.items():
        for target in targets:
            weight = weights[(start, target)]
            tooltip = dot_quote(f"{start} -> {target}; weight {weight:g}")
            weight_label = (
                f', label="{weight:g}", fontsize=9, fontname="Arial", '
                'fontcolor="#374151"'
                if show_weight_labels else ""
            )
            if (start, target) in tree_edges:
                attributes = (
                    'color="#2563eb", penwidth=2.2, arrowsize=0.7, '
                    f'tooltip="{tooltip}"{weight_label}'
                )
            else:
                attributes = (
                    'color="#9ca3af80", penwidth=0.7, arrowsize=0.5, '
                    f'constraint=false, tooltip="{tooltip}"{weight_label}'
                )
            lines.append(f"  n{start} -> n{target} [{attributes}];")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="directory of graph part files")
    parser.add_argument("output_dot", type=Path, help="Graphviz .dot output path")
    parser.add_argument("--source", type=int, default=1, help="BFS source vertex")
    args = parser.parse_args()

    adjacency, weights, defined_in, input_files = read_graph(args.input_dir)
    dot = build_dot(adjacency, weights, defined_in, args.source)
    args.output_dot.parent.mkdir(parents=True, exist_ok=True)
    args.output_dot.write_text(dot, encoding="utf-8", newline="\n")

    print(f"Input files: {len(input_files)}")
    print(f"Vertices: {len(adjacency)}")
    print(f"Directed edges: {sum(len(v) for v in adjacency.values())}")
    print(f"DOT written: {args.output_dot}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Preview every round of an input-driven Graph Burning job.

Input is the SAME vertex file/directory accepted by Giraph's
BurningScheduleTextInputFormat: ``vertex_id source_round neighbour:weight ...``.
No source-selection or optimisation happens here. Round 1 burns only its
source; in later rounds the previous round's newly burned vertices spread
one edge while that round's new source ignites.

The text preview and expected.tsv need only Python's standard library.
Use --networkx to also save each round's burned induced subgraph as GraphML;
add --png to draw the full graph with the current burned nodes highlighted.
"""

import argparse
from pathlib import Path
import sys

from validate_burning_schedule import parse_lines, predicted_rounds


def load_input(path):
    """Combine all .txt parts, just as Giraph combines an HDFS directory."""
    files = sorted(path.glob("*.txt")) if path.is_dir() else [path]
    if not files or any(not file.is_file() for file in files):
        raise ValueError("input must be a readable .txt file or directory of .txt parts")

    def lines():
        for file in files:
            with file.open(encoding="utf-8") as stream:
                yield from stream

    return parse_lines(lines())


def simulate_rounds(graph, sources):
    """Return (round, source, newly burned, all burned, induced edges).

    ``frontier`` is the set that caught fire in the PREVIOUS round. It may
    spread now, but vertices first burning in this round cannot spread until
    the next round. This is the one-edge-per-round rule used by Giraph.
    """
    burned = {}  # vertex -> first burn round
    frontier = set()
    history = []
    for round_number in range(1, max(sources) + 1):
        source = sources[round_number]
        reached_from_old_fire = set().union(
            *(graph[vertex] for vertex in frontier)
        ) if frontier else set()
        newly = (reached_from_old_fire | {source}) - burned.keys()
        burned.update({vertex: round_number for vertex in newly})
        frontier = newly
        cumulative = set(burned)
        edges = sorted({
            (min(vertex, neighbour), max(vertex, neighbour))
            for vertex in cumulative
            for neighbour in graph[vertex]
            if neighbour in cumulative
        })
        history.append((round_number, source, sorted(newly), sorted(cumulative), edges))

    expected = predicted_rounds(graph, sources)
    actual = {vertex: burned.get(vertex, -1) for vertex in graph}
    if actual != expected:
        raise AssertionError("iterative preview disagrees with distance-based prediction")
    return history, actual


def write_text_files(output_dir, graph, sources, history, first_burn):
    """Save the final Giraph-comparable rows and per-round graph state."""
    (output_dir / "expected.tsv").write_text(
        "".join(
            "{}\t{}\t{}\n".format(v, "B" if first_burn[v] > 0 else "NB", first_burn[v])
            for v in sorted(graph)
        ), encoding="utf-8"
    )
    for round_number, source, newly, cumulative, edges in history:
        stem = "round-{:02d}".format(round_number)
        (output_dir / (stem + "-nodes.tsv")).write_text(
            "vertex\tstate\tfirst_burn_round\tnew_this_round\n" +
            "".join(
                "{}\t{}\t{}\t{}\n".format(
                    vertex,
                    "B" if vertex in cumulative else "NB",
                    first_burn[vertex] if vertex in cumulative else -1,
                    "yes" if vertex in newly else "no",
                )
                for vertex in sorted(graph)
            ), encoding="utf-8"
        )
        (output_dir / (stem + "-burned-edges.tsv")).write_text(
            "from\tto\n" + "".join("{}\t{}\n".format(*edge) for edge in edges),
            encoding="utf-8"
        )


def write_networkx_files(output_dir, graph, sources, history, first_burn, png):
    """Export induced subgraphs; optionally draw stable full-graph snapshots."""
    try:
        import networkx as nx
    except ImportError as error:
        raise ValueError("--networkx needs NetworkX: python3 -m pip install networkx") from error
    if png:
        try:
            import matplotlib
            matplotlib.use("Agg")  # Save images without requiring a desktop display.
            import matplotlib.pyplot as plt
        except ImportError as error:
            raise ValueError("--png needs Matplotlib: python3 -m pip install matplotlib") from error

    full = nx.Graph()
    full.add_nodes_from(sorted(graph))
    full.add_edges_from(
        (u, v) for u in graph for v in graph[u] if u < v
    )
    positions = nx.spring_layout(full, seed=42) if png else None

    for round_number, source, newly, cumulative, _ in history:
        stem = "round-{:02d}".format(round_number)
        burned_set = set(cumulative)
        subgraph = full.subgraph(cumulative).copy()
        for vertex in subgraph:
            subgraph.nodes[vertex]["first_burn_round"] = first_burn[vertex]
            subgraph.nodes[vertex]["source_round"] = next(
                (r for r, s in sources.items() if s == vertex), 0
            )
        nx.write_graphml(subgraph, output_dir / (stem + "-burned.graphml"))

        if png:
            figure, axis = plt.subplots(figsize=(9, 6))
            colors = [
                "#2563eb" if vertex == source else
                "#f97316" if vertex in newly else
                "#facc15" if vertex in burned_set else "#d1d5db"
                for vertex in full
            ]
            nx.draw_networkx(
                full, pos=positions, ax=axis, node_color=colors,
                edge_color=[
                    "#374151" if u in burned_set and v in burned_set else "#d1d5db"
                    for u, v in full.edges
                ], with_labels=True, node_size=750, font_size=10,
            )
            axis.set_title("Round {}: source {} | new {} | burned {}/{}".format(
                round_number, source, len(newly), len(cumulative), len(graph)
            ))
            axis.axis("off")
            figure.tight_layout()
            figure.savefig(output_dir / (stem + ".png"), dpi=160)
            plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="scheduled graph .txt file or directory")
    parser.add_argument("--output-dir", type=Path, help="new directory for expected output and round states")
    parser.add_argument("--networkx", action="store_true", help="save a GraphML burned subgraph per round")
    parser.add_argument("--png", action="store_true", help="also save a full-graph PNG per round")
    args = parser.parse_args()
    if (args.networkx or args.png) and args.output_dir is None:
        parser.error("--networkx/--png require --output-dir")

    try:
        graph, sources = load_input(args.input)
        history, first_burn = simulate_rounds(graph, sources)
        if args.output_dir is not None:
            if args.output_dir.exists() and any(args.output_dir.iterdir()):
                raise ValueError("output directory is not empty; choose a new path")
            # Check optional packages BEFORE creating output files.
            if args.networkx or args.png:
                import networkx  # noqa: F401
            if args.png:
                import matplotlib  # noqa: F401
            args.output_dir.mkdir(parents=True, exist_ok=True)
            write_text_files(args.output_dir, graph, sources, history, first_burn)
            if args.networkx or args.png:
                write_networkx_files(
                    args.output_dir, graph, sources, history, first_burn, args.png
                )
    except (OSError, ValueError, ImportError) as error:
        parser.exit(2, "ERROR: {}\n".format(error))

    print("Vertices: {} | rounds: {} | sequence: {}".format(
        len(graph), len(history), ":".join(str(sources[r]) for r in sorted(sources))
    ))
    for round_number, source, newly, cumulative, edges in history:
        print("Round {}: source {}; newly burned {}; burned so far {}; unburned {}".format(
            round_number, source, newly, cumulative, sorted(set(graph) - set(cumulative))
        ))
        print("  Burned induced subgraph edges: {}".format(edges))
    print("Expected final output (vertex, B/NB, first burn round):")
    for vertex in sorted(graph):
        round_number = first_burn[vertex]
        print("{}\t{}\t{}".format(
            vertex, "B" if round_number > 0 else "NB", round_number
        ))
    if args.output_dir is not None:
        print("Saved round states and expected.tsv in {}".format(args.output_dir))


if __name__ == "__main__":
    main()

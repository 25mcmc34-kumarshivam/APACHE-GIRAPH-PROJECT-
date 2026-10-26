#!/usr/bin/env python3
"""Add reproducibly random source-round markers to an unscheduled graph.

Input: one text file or a directory of part-*.txt files containing lines
``vertex_id neighbour:weight ...``. Output: the same graph split into the
same parts, with a source-round column inserted after each vertex ID.

This is NOT an optimizer. At each round it chooses uniformly from vertices
that have not burned in an earlier round. The seed makes the experiment
repeatable. No Giraph or Hadoop job runs here.
"""

import argparse
import json
from pathlib import Path
import random

from find_small_graph_burning_sequence import read_graph
from validate_burning_schedule import distances_from, parse_lines


def select_sources(graph, rounds, seed):
    """Return {round: vertex} using random eligible choices, not scoring."""
    if rounds < 1:
        raise ValueError("rounds must be at least 1")
    rng = random.Random(seed)
    chosen = {}
    distances = {}
    for round_number in range(1, rounds + 1):
        eligible = [
            vertex for vertex in sorted(graph)
            if vertex not in chosen.values()
            and all(
                previous_round + distances[previous_source].get(vertex, float("inf"))
                >= round_number
                for previous_round, previous_source in chosen.items()
            )
        ]
        if not eligible:
            raise ValueError("no unburned source is available for round {}".format(round_number))
        source = rng.choice(eligible)
        chosen[round_number] = source
        distances[source] = distances_from(graph, source)
    return chosen


def prepare_parts(input_path, graph, chosen):
    """Return {filename: scheduled text}; validate everything before writing."""
    files = sorted(input_path.glob("*.txt")) if input_path.is_dir() else [input_path]
    source_round = {vertex: round_number for round_number, vertex in chosen.items()}
    parts = {}
    for file in files:
        lines = []
        for raw in file.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            vertex = int(fields[0])
            lines.append(" ".join([fields[0], str(source_round.get(vertex, 0))] + fields[1:]))
        parts[file.name] = "\n".join(lines) + "\n"
    parsed_graph, parsed_sources = parse_lines(
        line for content in parts.values() for line in content.splitlines()
    )
    if parsed_graph != graph or parsed_sources != chosen:
        raise AssertionError("scheduled graph differs from the original graph or choices")
    return parts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="unscheduled graph .txt file or directory")
    parser.add_argument("output", type=Path, help="new directory for scheduled parts")
    parser.add_argument("--rounds", type=int, required=True, help="number of ignition rounds")
    parser.add_argument("--seed", type=int, required=True, help="integer random seed")
    args = parser.parse_args()
    try:
        if args.output.exists():
            raise ValueError("output path already exists; choose a new directory")
        graph = read_graph(args.input)  # Parser only; no search/greedy function called.
        chosen = select_sources(graph, args.rounds, args.seed)
        parts = prepare_parts(args.input, graph, chosen)
        args.output.mkdir(parents=True)
        for name, content in parts.items():
            (args.output / name).write_text(content, encoding="utf-8")
        (args.output / "selection.json").write_text(
            json.dumps({"seed": args.seed, "rounds": args.rounds,
                        "sources": [chosen[r] for r in sorted(chosen)]}, indent=2) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError) as error:
        parser.exit(2, "ERROR: {}\n".format(error))
    print("Vertices: {} | rounds: {} | seed: {} | sources: {}".format(
        len(graph), args.rounds, args.seed,
        ":".join(str(chosen[r]) for r in sorted(chosen)),
    ))
    print("Saved scheduled graph in {}".format(args.output))


if __name__ == "__main__":
    main()

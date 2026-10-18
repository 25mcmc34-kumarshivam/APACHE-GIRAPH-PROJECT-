#!/usr/bin/env python3
"""Teach a SOURCE-ONLY, limited-neighbour burning rule on a local text graph.

This is not the standard graph-burning process and does not run Giraph.
For k selected sources, round r lets the source ignite itself and at most
k-r explicitly named adjacent vertices. Earlier fires do not spread again.
"""

import argparse
import math
from pathlib import Path


def read_graph(path):
    """Read 'vertex neighbour:weight ...' from one file or split .txt parts."""
    files = sorted(path.glob("*.txt")) if path.is_dir() else [path]
    if not files or any(not file.is_file() for file in files):
        raise ValueError("graph path has no readable .txt files")

    graph = {}  # vertex ID -> set of directly adjacent vertex IDs
    for file in files:
        with file.open(encoding="utf-8") as stream:
            for line_number, raw in enumerate(stream, 1):
                line = raw.split("#", 1)[0].strip()  # Allow explanatory comments.
                if not line:
                    continue
                fields = line.split()
                location = "{}:{}".format(file, line_number)
                try:
                    vertex = int(fields[0])
                except ValueError as error:
                    raise ValueError("{}: vertex ID must be an integer".format(location)) from error
                if vertex in graph:
                    raise ValueError("{}: vertex {} is defined twice".format(location, vertex))

                neighbours = set()
                for field in fields[1:]:
                    try:
                        neighbour_text, weight_text = field.split(":", 1)
                        neighbour = int(neighbour_text)
                        weight = float(weight_text)
                    except ValueError as error:
                        raise ValueError(
                            "{}: expected neighbour:weight, got {!r}".format(location, field)
                        ) from error
                    if not math.isfinite(weight):
                        raise ValueError("{}: edge weight must be finite".format(location))
                    if neighbour == vertex or neighbour in neighbours:
                        raise ValueError(
                            "{}: self-loop or repeated neighbour {}".format(location, neighbour)
                        )
                    neighbours.add(neighbour)
                graph[vertex] = neighbours

    if not graph:
        raise ValueError("graph is empty")
    for vertex, neighbours in graph.items():
        for neighbour in neighbours:
            if neighbour not in graph:
                raise ValueError("{} refers to undefined vertex {}".format(vertex, neighbour))
            if vertex not in graph[neighbour]:
                raise ValueError(
                    "edge {}-{} is missing its reverse entry; use an undirected graph".format(
                        vertex, neighbour
                    )
                )
    return graph


def read_schedule(path):
    """Read 'round source neighbour ...' with '-' for no chosen neighbours."""
    schedule = []  # One (source, chosen_neighbours) pair for each round.
    with path.open(encoding="utf-8") as stream:
        for line_number, raw in enumerate(stream, 1):
            line = raw.split("#", 1)[0].strip()
            if not line:
                continue
            fields = line.split()
            try:
                round_number = int(fields[0])
                source = int(fields[1])
                chosen = [] if fields[2:] == ["-"] else [int(x) for x in fields[2:]]
            except (IndexError, ValueError) as error:
                raise ValueError(
                    "{}:{}: expected 'round source neighbour ...' or 'round source -'".format(
                        path, line_number
                    )
                ) from error
            if not fields[2:]:
                raise ValueError("{}:{}: write '-' when choosing no neighbours".format(path, line_number))
            if round_number != len(schedule) + 1:
                raise ValueError("schedule rounds must be consecutive, starting with 1")
            if len(chosen) != len(set(chosen)):
                raise ValueError("round {} repeats a chosen neighbour".format(round_number))
            schedule.append((source, chosen))
    if not schedule:
        raise ValueError("schedule needs at least one round")
    return schedule


def simulate(graph, schedule):
    """Return first-burn rounds and a trace; -1 means still unburned."""
    first_burn = {vertex: -1 for vertex in graph}
    trace = []
    used_sources = set()
    total_rounds = len(schedule)

    for round_number, (source, chosen) in enumerate(schedule, 1):
        budget = total_rounds - round_number  # Example: k=3 -> 2, 1, 0.
        if source not in graph:
            raise ValueError("round {}: source {} is not in the graph".format(round_number, source))
        if source in used_sources:
            raise ValueError("round {}: source {} was selected before".format(round_number, source))
        if first_burn[source] != -1:
            raise ValueError("round {}: source {} is already burned".format(round_number, source))
        if len(chosen) > budget:
            raise ValueError(
                "round {}: selected {} neighbours but limit is {}".format(
                    round_number, len(chosen), budget
                )
            )
        for neighbour in chosen:
            if neighbour not in graph[source]:
                raise ValueError(
                    "round {}: {} is not directly adjacent to source {}".format(
                        round_number, neighbour, source
                    )
                )
            if first_burn[neighbour] != -1:
                raise ValueError(
                    "round {}: neighbour {} is already burned".format(round_number, neighbour)
                )

        # Only the selected source and its named neighbours ignite this round.
        # A vertex burned in an earlier round does NOT spread on its own.
        newly_burned = [source] + chosen
        for vertex in newly_burned:
            first_burn[vertex] = round_number
        used_sources.add(source)
        trace.append((round_number, source, budget, newly_burned[:], sum(
            burn_round != -1 for burn_round in first_burn.values()
        )))
    return first_burn, trace


def result_lines(first_burn):
    """Make the same readable columns as our earlier experiments."""
    return [
        "{}\t{}\t{}".format(vertex, "B" if first_burn[vertex] > 0 else "NB", first_burn[vertex])
        for vertex in sorted(first_burn)
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True, type=Path, help="one graph file or directory of .txt parts")
    parser.add_argument("--schedule", required=True, type=Path, help="chosen sources and exact neighbours")
    parser.add_argument("--output", type=Path, help="new result file; never overwrites an existing file")
    args = parser.parse_args()
    try:
        graph = read_graph(args.graph)
        schedule = read_schedule(args.schedule)
        first_burn, trace = simulate(graph, schedule)
        lines = result_lines(first_burn)
        if args.output:
            # Exclusive creation protects an earlier experiment from accidental replacement.
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write("\n".join(lines) + "\n")
    except (OSError, ValueError) as error:
        parser.exit(2, "ERROR: {}\n".format(error))

    print("Vertices: {}; rounds: {}".format(len(graph), len(schedule)))
    for round_number, source, budget, new, total in trace:
        print("Round {}: source={} neighbour limit={} newly burned={} total burned={}".format(
            round_number, source, budget, ",".join(map(str, new)), total
        ))
    print("vertex\tstatus\tfirst_burn_round")
    print("\n".join(lines))
    if args.output:
        print("Result saved to: {}".format(args.output))


if __name__ == "__main__":
    main()

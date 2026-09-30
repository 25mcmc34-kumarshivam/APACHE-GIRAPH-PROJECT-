#!/usr/bin/env python3
"""Validate the input-driven burning format and report its final round.

Input record: vertex_id source_round neighbour_id:weight ...
source_round=0 means this vertex is not selected as a new source.
The normal command reads one file or all .txt files in a directory. The
runner uses --stdin because its graph lives in HDFS, not the local disk.
"""

import argparse
from collections import deque
import math
from pathlib import Path
import sys


def parse_lines(lines):
    """Return (adjacency, sources_by_round), rejecting malformed records."""
    graph = {}
    sources = {}
    for line_number, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        fields = line.split()
        if len(fields) < 2:
            raise ValueError("line {} needs vertex ID and source round".format(line_number))
        try:
            vertex = int(fields[0])
            round_number = int(fields[1])
        except ValueError as error:
            raise ValueError("line {} has a non-integer ID/round".format(line_number)) from error
        if round_number < 0:
            raise ValueError("line {} has a negative source round".format(line_number))
        if vertex in graph:
            raise ValueError("vertex {} is defined twice".format(vertex))
        if round_number:
            if round_number in sources:
                raise ValueError(
                    "round {} selects both {} and {}; choose one source per round".format(
                        round_number, sources[round_number], vertex
                    )
                )
            sources[round_number] = vertex

        neighbours = set()
        for field in fields[2:]:
            try:
                neighbour_text, weight_text = field.split(":", 1)
                neighbour = int(neighbour_text)
                weight = float(weight_text)
            except ValueError as error:
                raise ValueError(
                    "line {} needs neighbour:weight, got {!r}".format(line_number, field)
                ) from error
            if not math.isfinite(weight):
                raise ValueError("line {} has a non-finite edge weight".format(line_number))
            if neighbour in neighbours:
                raise ValueError("vertex {} repeats neighbour {}".format(vertex, neighbour))
            neighbours.add(neighbour)
        graph[vertex] = neighbours

    if not graph or not sources:
        raise ValueError("graph and at least one scheduled source are required")
    total_rounds = max(sources)
    missing = set(range(1, total_rounds + 1)) - set(sources)
    if missing:
        raise ValueError("no source is selected in round {}".format(min(missing)))
    for vertex, neighbours in graph.items():
        for neighbour in neighbours:
            if neighbour not in graph:
                raise ValueError("{} points to undefined vertex {}".format(vertex, neighbour))
            if vertex not in graph[neighbour]:
                raise ValueError(
                    "{} -> {} lacks a reverse edge; this experiment uses an undirected graph".format(
                        vertex, neighbour
                    )
                )

    # A valid new source must not have burned BEFORE its scheduled round.
    # Fire arriving in the same round is allowed, as in the earlier star test.
    distances = {source: distances_from(graph, source) for source in sources.values()}
    for round_number in range(1, total_rounds + 1):
        candidate = sources[round_number]
        for earlier_round in range(1, round_number):
            earlier_source = sources[earlier_round]
            distance = distances[earlier_source].get(candidate, math.inf)
            if earlier_round + distance < round_number:
                raise ValueError(
                    "source {} is already burned before round {}".format(
                        candidate, round_number
                    )
                )
    return graph, sources


def distances_from(graph, source):
    """Shortest unweighted hop distances for validation and prediction."""
    distances = {source: 0}
    queue = deque([source])
    while queue:
        vertex = queue.popleft()
        for neighbour in graph[vertex]:
            if neighbour not in distances:
                distances[neighbour] = distances[vertex] + 1
                queue.append(neighbour)
    return distances


def predicted_rounds(graph, sources):
    """Return first-burn round, or -1 for a vertex left unburned."""
    total_rounds = max(sources)
    distances = {source: distances_from(graph, source) for source in sources.values()}
    result = {}
    for vertex in graph:
        arrivals = [
            round_number + distances[source][vertex]
            for round_number, source in sources.items()
            if vertex in distances[source]
        ]
        first = min(arrivals, default=math.inf)
        result[vertex] = int(first) if first <= total_rounds else -1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, help="one .txt file or directory")
    parser.add_argument("--stdin", action="store_true", help="read graph from stdin")
    parser.add_argument("--rounds-only", action="store_true", help="print only maximum scheduled round")
    args = parser.parse_args()
    if args.stdin == (args.path is not None):
        parser.error("choose exactly one of PATH or --stdin")
    try:
        if args.stdin:
            graph, sources = parse_lines(sys.stdin)
        else:
            files = sorted(args.path.glob("*.txt")) if args.path.is_dir() else [args.path]
            if not files:
                raise ValueError("no .txt input files found")
            def input_lines():
                for file in files:
                    with file.open(encoding="utf-8") as stream:
                        yield from stream
            graph, sources = parse_lines(input_lines())
    except (OSError, ValueError) as error:
        parser.exit(2, "ERROR: {}\n".format(error))

    if args.rounds_only:
        print(max(sources))
    else:
        print("Vertices: {}".format(len(graph)))
        print("Undirected connections: {}".format(sum(map(len, graph.values())) // 2))
        print("Scheduled rounds: {}".format(max(sources)))
        print("Sources: " + ":".join(str(sources[round_number]) for round_number in sorted(sources)))
        for vertex, round_number in sorted(predicted_rounds(graph, sources).items()):
            print("{}\t{}\t{}".format(
                vertex, "B" if round_number > 0 else "NB", round_number
            ))


if __name__ == "__main__":
    main()

# Apache Giraph Project

This repository records the implementation and evaluation of graph algorithms with Apache Giraph on a single-node Ubuntu/Hadoop lab server. Inputs, operational code, measured outputs, weekly work records and separate study notes have distinct locations.

| Start here | Purpose |
|---|---|
| [Experiment index](docs/EXPERIMENT-INDEX.md) | Map each input dataset to its program, result, and verification status. |
| [Datasets](datasets/README.md) / [results](results/README.md) | Find graph parts, output files and per-round evidence. |
| [Weekly work reports](weekly-reports/README.md) | Chronology, commands, file transfers, problems and outcomes. |
| [Study material](study-material/README.md) | Separate technical explanations and team learning notes. |
| [Setup](setup/) | Installation and startup instructions for a new machine or the shared lab server. |

The latest [Week 15 report](weekly-reports/2026-10-29-week-15.md) records fresh 30-node and 120-node input-driven Graph Burning jobs. Python and Giraph agreed on every final row (`diff` exit 0). For the 120-node grid, 119 vertices burned in eight rounds; vertex 85 remained `NB -1`. Sources were selected by seeded random eligible choice, **not** an optimizer. The actual 120-node HDFS TSV still needs to be copied into this repository; the lab comparison and eight round pictures are recorded.

## Verified environment

- Ubuntu 22.04 LTS
- OpenJDK 8
- Apache Hadoop 2.7.7
- Apache Giraph 1.4.0-SNAPSHOT
- HDFS and YARN in pseudo-distributed mode
- Giraph source owned and built by `mca2025`
- Hadoop services operated by `hduser`

## Completed work

- PageRank
- Out-degree calculation
- In-degree calculation
- Breadth-first search (BFS)
- Single-source shortest paths
- Graph Burning simulation for supplied source sequences, with local Python source checking
- Giraph/Hadoop Guava compatibility repair using a shaded JAR

## Repository layout

- `datasets/` contains graph inputs, including split text datasets and the 120-node grid.
- `src/` contains the custom Giraph computation classes.
- `scripts/` contains reusable job scripts.
- `results/` contains saved lab outputs where available, Python predictions and visual evidence, labelled by provenance.
- `diagrams/` contains exact graph visualizations and editable Graphviz source.
- `docs/` contains project, experiment, installation and operating references.
- `weekly-reports/` contains factual work records; `study-material/` contains separate explanations.

For a new Ubuntu 22.04 machine, choose the [one-account laptop guide](setup/UBUNTU-22.04-SINGLE-ACCOUNT.md) or the [two-account shared-server guide](setup/UBUNTU-22.04-FROM-SCRATCH.md). The one-account guide follows the isolated second-PC validation; the two-account procedure still needs a full blank-laptop trial. The older [`docs/INSTALLATION.md`](docs/INSTALLATION.md) records the lab setup but is not the clean-machine checklist.

For structured study from basic Linux through distributed computing, Hadoop, Giraph, graph algorithms, and research work, follow [`docs/STUDY-ROADMAP.md`](docs/STUDY-ROADMAP.md). The shorter [`docs/LEARNING-GUIDE.md`](docs/LEARNING-GUIDE.md) explains the algorithms used in the completed lab.

Project administration and reporting are recorded in [`docs/PROJECT-OVERVIEW.md`](docs/PROJECT-OVERVIEW.md), [`docs/WEEKLY-TIMELINE.md`](docs/WEEKLY-TIMELINE.md), and the reusable [`docs/WEEKLY-REPORT-TEMPLATE.md`](docs/WEEKLY-REPORT-TEMPLATE.md).

Top-level indexes are available in [`setup/`](setup/), [`study-material/`](study-material/), and [`weekly-reports/`](weekly-reports/).

For theory, command meanings, algorithm walkthroughs, exercises, and the weekly study plan, use [`docs/LEARNING-GUIDE.md`](docs/LEARNING-GUIDE.md).

## Five-node directed graph

The example graph contains these weighted directed edges:

`1→2, 2→3, 3→2, 3→4, 4→3, 5→3`

Every edge has weight `1`. The JSON input format is:

```text
[vertex_id, initial_value, [[target_vertex_id, edge_weight], ...]]
```

## Important

This repository does not contain passwords, SSH keys, Hadoop data directories, logs, Maven `target/` directories, or generated JAR files. Build the shaded Giraph JAR on the Ubuntu server before running the scripts.

The detailed installation manual is maintained separately in Google Docs. This repository stores the code, datasets, results, and concise reproducibility notes.

## Thirty-node distributed-input experiment

[`datasets/thirty-node-text/`](datasets/thirty-node-text/) contains a 30-vertex,
79-edge directed graph divided into three text files. Hadoop/Giraph reads the
directory as one logical dataset. The accompanying source includes a commented
plain-text reader and BFS, in-degree, and out-degree computations.

The verified 30-node BFS result is explained level by level in
[`docs/BFS-THIRTY-NODE-WALKTHROUGH.md`](docs/BFS-THIRTY-NODE-WALKTHROUGH.md).
The complete 30-node, 79-edge directed topology is available in
[`diagrams/`](diagrams/).

The focused [`weighted BFS comparison dataset`](datasets/weighted-bfs-comparison/)
demonstrates why the fewest-hop route can differ from the route with the lowest
total edge weight. Use
[`scripts/run_text_graph_algorithm.sh`](scripts/run_text_graph_algorithm.sh)
to run any of the five current algorithms without retyping the long Giraph
command.

The verified comparison outputs are stored in
[`results/weighted-bfs-comparison/`](results/weighted-bfs-comparison/).

## Graph Burning work

The [Giraph Graph Burning computation](src/LearningGraphBurningComputation.java)
simulates a supplied sequence such as `3:8:6`; it reports each vertex's
first burn round. Lab-verified runs cover a nine-node path, a seven-node star,
two sequences on a disconnected six-node graph, and a six-node cycle.
Their outputs are in [`results/`](results/).

The [local Python source selector](scripts/find_small_graph_burning_sequence.py)
can validate a supplied sequence, search exactly on up to ten vertices, or
propose a greedy sequence for a larger teaching graph. Its greedy mode is
not generally an optimality proof. We made a separate
[undirected version of the 30-node graph](datasets/thirty-node-undirected-burning/)
for this experiment; the original directed graph is unchanged. The proposed
four-round sequence `1:18:3:8` was [verified in Giraph](results/graph-burning-30-undirected/),
with all 30 values matching the local prediction. Start with
the [Graph Burning study note](study-material/graph-burning-source-selection-30.md)
and the [Hinglish Python code guide](study-material/hinglish-code-guide/find-small-graph-burning-sequence-Hinglish.md).

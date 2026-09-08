# Apache Giraph Project

This repository records the Apache Hadoop and Apache Giraph learning work completed on the single-node Ubuntu lab server.

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
- Single-source shortest paths
- Giraph/Hadoop Guava compatibility repair using a shaded JAR

## Repository layout

- `datasets/` contains small graph inputs that can be checked manually.
- `src/` contains the custom Giraph computation classes.
- `scripts/` contains reusable job scripts.
- `results/` contains verified outputs from the lab server.
- `docs/` contains the installation guide, lab record, and operating notes.

Start with [`docs/INSTALLATION.md`](docs/INSTALLATION.md) when preparing a new Ubuntu machine. After installation, run `scripts/check_environment.sh` to check the commands, versions, HDFS, and YARN before submitting a graph job.

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

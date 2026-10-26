# Study Material Index

Study in this order:

1. [Complete study roadmap](../docs/STUDY-ROADMAP.md) — 24-week sequence from Linux basics to research work.
2. [Learning guide](../docs/LEARNING-GUIDE.md) — explanations of Hadoop, Giraph, degree, PageRank, and shortest paths.
3. [Installation guide](../docs/INSTALLATION.md) — practical environment and command reference.
4. [Five-node dataset](../datasets/five_node_graph.json) — graph used for manual and Giraph calculations.
5. [Verified results](../results/) — answers used to check understanding and program correctness.
6. [Hinglish Java guide](hinglish-java-guide/) — team-only learning companion explaining the degree, text-reader, and BFS programs line by line. It is not used for compilation.
7. [Thirty-node BFS walkthrough](../docs/BFS-THIRTY-NODE-WALKTHROUGH.md) — explains the output, manual levels, Giraph supersteps, example routes, and BFS versus weighted shortest path.
8. [Graph Burning and diffusion models](graph-burning-and-diffusion-models.md) — explains GB, ICM, LTM and SIR, distinguishes them from BFS, and gives the Giraph implementation roadmap.
9. [Maven build workflow](maven-build-workflow.md) — explains why we repeatedly build, every part of the command, the JAR check, and how to decide whether a new build is needed.
10. [Week 14 limited-neighbour burning study sheet](../docs/WEEK-14-LIMITED-NEIGHBOUR-BURNING-STUDY.md) — one place to read the new Python-only rule, split graph files, hand-written schedule, step-by-step code, exact commands, tests, measured lab output, and the difference from standard Graph Burning.
11. [Round-by-round burning Python guide (Hinglish)](hinglish-code-guide/show-burning-rounds-Hinglish.md) — separate beginner-level explanation of the current standard-burning preview, its helper validator, NetworkX pictures, Giraph comparison and exact lab commands. Start here for the Week 15 practical; do not mix it with item 10's different model.
12. The same Hinglish guide's last section explains the [30-node random schedule preparer](../scripts/prepare_random_burning_input.py), its eligibility check, seed, generated input and verified Giraph comparison.
13. [120-node grid experiment (Hinglish)](hinglish-code-guide/grid-120-experiment-Hinglish.md) — explains the generator, 10×12 topology, four split files, random schedule, Python prediction and verified Giraph comparison. Follow the [Week 15 file map](../weekly-reports/2026-10-29-week-15.md) to open every relevant source and result.

The roadmap includes websites, books, Wikipedia pages, research papers, YouTube channels, exercises, and completion checkboxes.

Future subject notes should be added in this folder using names such as:

- `01-linux-notes.md`
- `02-java-notes.md`
- `03-big-data-notes.md`
- `04-graph-theory-notes.md`
- `05-distributed-computing-notes.md`
- `06-hadoop-notes.md`
- `07-giraph-notes.md`
- `08-research-methods-notes.md`

Write notes in the team's own words and include a source link and date accessed for externally learned material.

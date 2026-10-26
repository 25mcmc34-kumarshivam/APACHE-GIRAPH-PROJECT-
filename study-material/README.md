# Study Material Index

## Choose the right kind of file

| Purpose | Open | What belongs there |
|---|---|---|
| Work history and commands | [Weekly reports](../weekly-reports/README.md) and [master timeline](../docs/WEEKLY-TIMELINE.md) | What was done, by which account, transfers, evidence, errors and result; not the long teaching narrative. |
| Code with many comments | [Week 15 commented-code track](week-15/CODE-WITH-COMMENTS.md), older [explained script copies](../scripts/learning-guides/README.md), and [Hinglish Java guides](hinglish-java-guide/README.md) | Variables, expressions and program flow. The tested operational source stays under `scripts/` and `src/`. |
| Baby-level understanding | [Week 15 Hinglish lesson](week-15/BABY-LEVEL-HINGLISH.md) and the earlier guides below | Start from node/edge and explain why each stage exists, without requiring code fluency. |
| Explain to faculty | [Week 15 faculty brief](week-15/FACULTY-BRIEF.md) | Concise method, result, limitations and demonstration links; not private learning notes. |

## Learning material by week

| Week | Work record | Dedicated learning material |
|---|---|---|
| 1–9 | [Weekly-report index](../weekly-reports/README.md) | [Foundations learning guide](../docs/LEARNING-GUIDE.md), [roadmap](../docs/STUDY-ROADMAP.md), [Maven build explanation](maven-build-workflow.md), and [Java guides](hinglish-java-guide/README.md). Some early weeks do not yet have an individual lesson; use their report for factual history. |
| 10 | [Week 10 report](../weekly-reports/2026-09-24-week-10.md) | [Self-contained Graph Burning study sheet](../docs/WEEK-10-GRAPH-BURNING-SELF-CONTAINED-STUDY.md). |
| 11 | [Week 11 report](../weekly-reports/2026-10-01-week-11.md) | [Input-driven Burning study sheet](../docs/WEEK-11-INPUT-DRIVEN-BURNING-SELF-CONTAINED-STUDY.md) and [runner Hinglish guide](hinglish-code-guide/run-graph-burning-script-Hinglish.md). |
| 12–13 | [Weekly-report index](../weekly-reports/README.md) | [Graph Burning and diffusion models](graph-burning-and-diffusion-models.md), [small-graph source search](hinglish-code-guide/find-small-graph-burning-sequence-Hinglish.md). These are subject guides, not automatically a claim that each topic was completed in both weeks. |
| 14 | [Week 14 report](../weekly-reports/2026-10-22-week-14.md) | [Limited-neighbour Python lesson](../docs/WEEK-14-LIMITED-NEIGHBOUR-BURNING-STUDY.md). This is a different model from standard burning. |
| 15 | [Week 15 report](../weekly-reports/2026-10-29-week-15.md) | [Week 15 hub](week-15/README.md): [commented code](week-15/CODE-WITH-COMMENTS.md), [baby-level Hinglish](week-15/BABY-LEVEL-HINGLISH.md), [faculty brief](week-15/FACULTY-BRIEF.md). |

The older study sheets remain at their original paths so existing GitHub and teammate links do not break. New week-specific learning pages go under `study-material/week-N/`; the factual weekly entry stays under `weekly-reports/`.

## General subject reading order

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
13. [120-node grid experiment (Hinglish)](hinglish-code-guide/grid-120-experiment-Hinglish.md) — extra topology and lab commands; the [Week 15 hub](week-15/README.md) is the primary three-track learning entry. Follow the [Week 15 file map](../weekly-reports/2026-10-29-week-15.md) to open every relevant source and result.

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

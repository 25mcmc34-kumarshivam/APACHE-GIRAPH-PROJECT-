# Experiment results

Start at the [experiment index](../docs/EXPERIMENT-INDEX.md) to find the **input dataset for each result** and distinguish a Giraph job from a local Python simulation. Every result subdirectory has its own README with the source sequence, output meaning and evidence status.

| Result group | Records |
|---|---|
| [Five-node JSON input](../datasets/five_node_graph.json) | Root [PageRank](pagerank.txt), [out-degree](outdegree.txt), [in-degree](indegree.txt), [shortest from 1](shortest-path-from-1.txt) and [shortest from 5](shortest-path-from-5.txt). |
| [30-node text algorithms](thirty-node-text/README.md) | PageRank, both degrees, BFS and shortest path on one three-part directed text input. |
| [Weighted BFS comparison](weighted-bfs-comparison/README.md) | BFS hops and weighted shortest-path costs on the same six-node input. |
| [Earlier Graph Burning](graph-burning-path-9/README.md) | Numeric-format examples on path, cycle, star, disconnected and undirected 30-node graphs; follow the [central map](../docs/EXPERIMENT-INDEX.md) for exact pairings. |
| [Input-driven Graph Burning](graph-burning-path-9-scheduled/README.md) | `B`/`NB` examples on the nine-node path and its two-round/hand-picked variants. |
| [Week 15: random 30-node input](graph-burning-30-random-seed-20261026/README.md) | Saved actual Giraph TSV, local/lab Python predictions, four PNG/GraphML previews. |
| [Week 15: random 120-node grid](grid-120-random-burning-seed-20261026/README.md) | Saved Python prediction and eight lab previews; lab Giraph comparison succeeded but actual HDFS TSV transfer is pending. |
| [Limited-neighbour demo](limited-neighbour-burning-demo/README.md) | Local Python-only simulation, **not** Giraph output. |

For per-round Week 15 PNG, GraphML and TSV links, open the corresponding result README or the [Week 15 report](../weekly-reports/2026-10-29-week-15.md). The result folders preserve old filenames rather than renaming historical evidence; this avoids breaking existing citations.

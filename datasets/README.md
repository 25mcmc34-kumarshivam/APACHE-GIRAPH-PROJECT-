# Input datasets

Use the [experiment index](../docs/EXPERIMENT-INDEX.md) to select a dataset and find its **corresponding result**. The folders below contain input records; `results/` contains outputs. When a dataset is split into `part-01.txt`, `part-02.txt`, etc., upload the parts to **one HDFS directory**. Giraph treats them as one graph. Never upload README files, `selection.json`, `topology.json`, PNGs or previous outputs as graph records.

| Dataset family | Input directories | Where its output is mapped |
|---|---|---|
| Earlier JSON and text algorithms | [Five-node JSON](five_node_graph.json), [30-node directed text](thirty-node-text/), [weighted six-node text](weighted-bfs-comparison/) | [Algorithm mapping](../docs/EXPERIMENT-INDEX.md#graph-algorithms-before-graph-burning) |
| Earlier supplied-sequence Graph Burning | [Path 9](graph-burning-path-9/), [cycle 6](graph-burning-cycle-6/), [star 7](graph-burning-star-7/), [disconnected 6](graph-burning-disconnected-6/), [undirected 30](thirty-node-undirected-burning/) | [Burning mapping](../docs/EXPERIMENT-INDEX.md#graph-burning-experiments) |
| Source-rounds stored inside graph input | [Path 9 complete](graph-burning-path-9-scheduled/), [path 9 two-round](graph-burning-path-9-two-round-scheduled/), [path 9 hand-picked](graph-burning-path-9-hand-picked/), [30-node random](thirty-node-random-burning-seed-20261026/), [120-node random](grid-120-random-burning-seed-20261026/) | [Burning mapping](../docs/EXPERIMENT-INDEX.md#graph-burning-experiments) |
| Intermediate/source-only cases | [120-node unscheduled grid](grid-120-unscheduled/), [limited-neighbour Python demo](limited-neighbour-burning-demo/) | Their dataset README and [experiment index](../docs/EXPERIMENT-INDEX.md) explain which program used them. |

The plain-text formats are **not interchangeable**: `vertex neighbour:weight ...` has no ignition column; `vertex sourceRound neighbour:weight ...` is for the input-driven burning reader. The original JSON graph requires its JSON input format. Choose the reader and runner that match the dataset; renaming a file from `.json` to `.txt` does not convert its contents.

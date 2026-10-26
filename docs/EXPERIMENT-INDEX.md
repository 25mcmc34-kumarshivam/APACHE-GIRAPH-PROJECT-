# Experiment index: input → program → output

This page is the repository's central map. A directory of `part-*.txt` files is **one graph dataset**, not one graph per file. Unless a result row says “local Python only”, Giraph read the input from HDFS and produced the recorded output on the lab setup. The `datasets/` copy is source data; the `results/` copy is evidence, not another input.

## Graph algorithms before Graph Burning

| Input dataset | Format and task | Saved output | Status |
|---|---|---|---|
| [Five-node JSON graph](../datasets/five_node_graph.json) | Original Giraph JSON; PageRank, in/out-degree and shortest-path examples | [PageRank](../results/pagerank.txt), [out-degree](../results/outdegree.txt), [in-degree](../results/indegree.txt), [shortest path from 1](../results/shortest-path-from-1.txt), [shortest path from 5](../results/shortest-path-from-5.txt) | Earlier lab outputs; see [learning guide](LEARNING-GUIDE.md) for interpretation. |
| [Thirty-node directed text graph](../datasets/thirty-node-text/README.md), three parts | Plain-text adjacency list; PageRank, degree, BFS and shortest path | [Five saved results](../results/thirty-node-text/README.md) | Giraph-verified on the common three-part HDFS input. |
| [Weighted six-node graph](../datasets/weighted-bfs-comparison/README.md) | Plain text; compare BFS hops with weighted shortest-path cost | [BFS and weighted result](../results/weighted-bfs-comparison/README.md) | Giraph-verified; two different questions on the same graph. |

## Graph Burning experiments

| Input dataset | Source selection / model | Saved result | Status |
|---|---|---|---|
| [Nine-node path](../datasets/graph-burning-path-9/README.md), three parts | Earlier runner; supplied sequence `3:8:6` typed as an argument | [Burn rounds](../results/graph-burning-path-9/README.md) | Giraph result, numeric earlier format. |
| [Six-node cycle](../datasets/graph-burning-cycle-6/README.md) | Earlier runner; `1:3:4` | [Burn rounds](../results/graph-burning-cycle-6/README.md) | Giraph result. |
| [Seven-node star](../datasets/graph-burning-star-7/README.md) | Earlier runner; `1:2` | [Burn rounds](../results/graph-burning-star-7/README.md) | Giraph result. |
| [Two disconnected paths](../datasets/graph-burning-disconnected-6/README.md) | Earlier runner; two- and three-round supplied sequences | [Both outputs](../results/graph-burning-disconnected-6/README.md) | Giraph results; old numeric unburned sentinel. |
| [Thirty-node undirected derivative](../datasets/thirty-node-undirected-burning/README.md), three parts | Earlier runner; `1:18:3:8` supplied by local heuristic | [Burn rounds](../results/graph-burning-30-undirected/README.md) | Giraph result; this graph is **not** the directed 30-node graph above. |
| [Nine-node path with source rounds in input](../datasets/graph-burning-path-9-scheduled/README.md), three parts | Input-driven reader; `3:8:6` in second column | [Giraph result and later Python preview](../results/graph-burning-path-9-scheduled/README.md) | Saved Giraph output; Week 15 preview matched (`diff` 0). |
| [Same path, two source rounds](../datasets/graph-burning-path-9-two-round-scheduled/README.md), three parts | Input-driven; `2:8` | [Result with `NB -1`](../results/graph-burning-path-9-two-round-scheduled/README.md) | Giraph-verified incomplete burn. |
| [Hand-picked path schedule](../datasets/graph-burning-path-9-hand-picked/README.md), three parts | Input-driven; `1:9:5`, not optimized | [Result with unburned nodes](../results/graph-burning-path-9-hand-picked/README.md) | Giraph-verified. |
| [Thirty-node undirected graph with random source rounds](../datasets/thirty-node-random-burning-seed-20261026/README.md), three parts | Input-driven; seeded random eligible `4:27:12:15`, not optimized | [Actual Giraph TSV and four-round previews](../results/graph-burning-30-random-seed-20261026/README.md) | Fresh Giraph vs Python: all 30 rows match (`diff` 0); 24 `B`, six `NB -1`. |
| [120-node 10×12 unscheduled grid](../datasets/grid-120-unscheduled/README.md), four parts | Deterministic synthetic graph generated before source rounds were inserted | [Scheduled derivative](../datasets/grid-120-random-burning-seed-20261026/README.md) | Intermediate source dataset, **not** sent directly to the scheduled Giraph job. |
| [120-node scheduled grid](../datasets/grid-120-random-burning-seed-20261026/README.md), four parts | Input-driven; seeded random eligible `15:104:35:101:41:111:83:86`, not optimized | [Python expected output and eight lab round previews](../results/grid-120-random-burning-seed-20261026/README.md) | Fresh Giraph vs Python: all 120 rows match on lab (`diff` 0); 119 `B`, node 85 `NB -1`. **Actual HDFS TSV copy into GitHub pending.** |
| [Limited-neighbour graph and separate schedule](../datasets/limited-neighbour-burning-demo/README.md), two graph parts | Different source-only neighbour-cap teaching rule | [Local Python output](../results/limited-neighbour-burning-demo/README.md) | **Not** Giraph/YARN; do not compare its rule to standard Graph Burning. |

## Find the exact file, not just the folder

- Each dataset folder's `README.md` gives its format and source method. Only `part-*.txt` graph records go into the corresponding HDFS input directory. A `selection.json`, `topology.json`, README, diagram or PNG is **metadata/output**, not a vertex record.
- Each result folder's `README.md` says whether the output is actual Giraph, Python prediction, visual preview, or local Python-only simulation. For Week 15, the [weekly report](../weekly-reports/2026-10-29-week-15.md) also lists each round's saved TSV, PNG and GraphML.
- [Operational scripts](../scripts/README.md) run jobs; [Java input reader and computation](../src/) are compiled into the shaded JAR. The [Week 15 report](../weekly-reports/2026-10-29-week-15.md#repeat-the-120-node-practical-yourself) gives exact account roles and transfer/run/compare commands.
- [Weekly reports](../weekly-reports/README.md) record chronology and evidence. [Study material](../study-material/README.md) is separate background reading.

## Output conventions and provenance

The input-driven runner formats each final row as `vertex<TAB>B-or-NB<TAB>first-burn-round`. `NB -1` means the node was not burned **within the configured rounds**. Earlier Graph Burning experiments used numeric values and may show `Double.MAX_VALUE` instead. PageRank, degree, BFS and shortest-path outputs have different meanings—consult their result README rather than interpreting them as burning rounds.

Python's `expected.tsv` is a **prediction**. `giraph-actual.tsv` or `part-00000.txt` is an actual saved result only where its result README says so. For 120 nodes, the HDFS result exists at `/user/mca2025/giraph_learning/graph_burning_grid120_random_20261026_output/part-00000`, and the lab comparison returned exit code 0; the raw TSV has not yet been transferred into this repository. Do not substitute the expected file and call it actual.

## Convention for the next experiment

1. Put only input records under a named `datasets/<experiment>/` folder. Its README states graph size, directed/undirected status, format, source-selection method, and which `part-*.txt` files form the logical dataset.
2. Put the tested program in `scripts/` or `src/`, and put any self-learning explanation under `study-material/`. Do not turn the weekly work report into a code tutorial.
3. Put saved outputs under the matching `results/<experiment>/` folder. Label each file **actual Giraph**, **Python prediction**, **lab preview**, or **local Python-only**. Record the HDFS paths and `diff` status. Never create an “actual” file from a prediction merely because they are expected to match.
4. Add one row to this index, update [datasets](../datasets/README.md) and [results](../results/README.md) navigation when a new family appears, and link the experiment from its [weekly report](../weekly-reports/README.md).
5. Keep JARs, Hadoop runtime directories, logs, passwords, keys, `.env` and temporary transfer folders out of Git.

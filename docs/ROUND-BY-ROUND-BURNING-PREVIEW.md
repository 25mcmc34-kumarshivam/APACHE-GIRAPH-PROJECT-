# Graph Burning: what the graph looks like after each round

This is the rule Sir described for a **supplied** sequence. We are not
searching for the best sequence yet. The earlier source-only,
limited-neighbour Python exercise was a different interpretation; do not
use its output as the answer to this experiment.

## The rule, with no shortcut

Suppose the chosen sources are `1, 4, 6` for rounds 1, 2, and 3.

1. Round 1: only vertex 1 catches fire. Its neighbours do **not** burn yet.
2. Round 2: fire from 1 reaches its direct neighbours; vertex 4 also catches
   fire as this round's new source.
3. Round 3: vertices that first burned in round 2 spread to their direct
   neighbours; vertex 6 also catches fire as the new source. A vertex that
   burns in round 3 cannot spread further because the run ends after round 3.

A vertex's result is its **first** burn round. If fire reaches the same
vertex by two routes in one round, it still appears only once. A vertex not
reached by the final round is `NB -1`. With three rounds, the first source
can reach distance 2, the second distance 1, and the third distance 0.
These are hop distances, **not** caps on how many individual neighbours may
burn.

## What the user supplies

Use the existing Giraph-compatible text format. Each vertex appears once:

```text
vertex_id source_round neighbour_id:weight neighbour_id:weight ...
```

`source_round=0` means the vertex is not a manually chosen source. A
positive number means it ignites in that round. Exactly one source must be
given for every round from 1 through the final round. For example, the
record `1 1 2:1 3:1` makes vertex 1 the round-1 source; `4 2 5:1` makes
vertex 4 the round-2 source. An undirected edge must appear on both endpoint
lines. Burning ignores the `:1` weight; the input reader requires that field.
The graph may be one `.txt` file or a directory of `.txt` parts.

The existing [`BurningScheduleTextInputFormat.java`](../src/BurningScheduleTextInputFormat.java)
reads this file for Giraph. The existing
[`LearningGraphBurningFromInputComputation.java`](../src/LearningGraphBurningFromInputComputation.java)
already uses the source-then-next-round-spread rule. It was **not** changed
for this preview.

## Python preview before the Giraph job

From the repository root, with the committed nine-node example:

```bash
python3 scripts/show_burning_rounds.py datasets/graph-burning-path-9-scheduled \
  --output-dir /tmp/burning-preview-path9
```

The program checks the same schedule as Giraph's runner and prints the new
source, newly burned vertices, all burned vertices, still-unburned vertices,
and the burned subgraph's edges **for each round**. It saves:

- `expected.tsv`: final `vertex B/NB first_round` rows, ready to compare with
  Giraph's readable output;
- `round-01-nodes.tsv`, `round-02-nodes.tsv`, etc.: every vertex's state
  immediately **after** that round, including whether it was newly burned;
- `round-01-burned-edges.tsv`, etc.: edges whose two endpoints have both
  burned by that round.

The burned **induced subgraph** contains all burned vertices and every
original edge between them. Its edges show the graph structure at that
round; they do not claim that fire travelled along every displayed edge.
Python independently simulates the rounds and checks its result against the
existing shortest-hop prediction.

For the nine-node path with sources `3, 8, 6`, the newly burned vertices are:

```text
round 1: 3
round 2: 2, 4, 8
round 3: 1, 5, 6, 7, 9
```

Notice that round 1 has **only** source 3. Vertices 2 and 4 are not counted
until round 2. That is the timing correction discussed with Sir.

## NetworkX subgraph and pictures (optional)

The text preview above uses only Python. To create a NetworkX GraphML
subgraph for each round and a PNG picture of the whole graph with burned
nodes highlighted, first install `networkx` and `matplotlib` in your Python
environment. Then use:

```bash
python3 scripts/show_burning_rounds.py datasets/graph-burning-path-9-scheduled \
  --output-dir /tmp/burning-preview-with-pictures --networkx --png
```

The `round-01-burned.graphml` file has one vertex (source 3) and no edge.
The `round-02-burned.graphml` file has vertices 2, 3, 4, 8 and edges
`2--3` and `3--4`. The PNG uses grey for unburned nodes, yellow for
previously burned nodes, orange for newly burned nodes, and blue for the
current source. Node positions stay the same across all pictures, so the
change from one round to the next is easy to see. NetworkX's
[`Graph.subgraph`](https://networkx.org/documentation/stable/reference/generated/networkx.classes.function.subgraph.html)
defines an induced subgraph; the pictures use NetworkX's
[`draw_networkx`](https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw_networkx.html).

## Compare with the actual Giraph result

The preview is a **prediction**, not evidence that a new Giraph job ran.
Upload the **same scheduled input** to HDFS, run the existing
[`run_graph_burning_from_input.sh`](../scripts/run_graph_burning_from_input.sh),
then compare the result. Example on the lab computer, using fresh HDFS paths:

```bash
hdfs dfs -mkdir -p /user/mca2025/giraph_learning/my_burning_input
hdfs dfs -put /path/to/my-input/part-*.txt /user/mca2025/giraph_learning/my_burning_input/
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/my_burning_input \
  /user/mca2025/giraph_learning/my_burning_output
hdfs dfs -cat /user/mca2025/giraph_learning/my_burning_output/part-00000 \
  > /tmp/my-burning-actual.tsv
diff -u /tmp/burning-preview-path9/expected.tsv /tmp/my-burning-actual.tsv
```

For the `diff` to be meaningful, replace the example preview and HDFS paths
with paths for the **same** graph and schedule. No output from `diff` means
the files match. A non-zero exit code means they differ or could not be read.
The runner refuses to overwrite an existing HDFS output path; use a new
name for each run.

## Verified lab preview

By 26 October, this preview was run on the lab computer against the
three-part HDFS input above. We installed NetworkX 3.4.2 and Matplotlib
3.10.9 for `mca2025` with `python3 -m pip install --user networkx matplotlib`.
The Python `expected.tsv` matched the **previously completed** Giraph
`part-00000` (`diff` exit 0). We did not submit another Giraph job for this
check. The actual [PNG, GraphML and TSV files](../results/graph-burning-path-9-scheduled/round-preview/)
are in the repository. A [Hinglish code walkthrough](../study-material/hinglish-code-guide/show-burning-rounds-Hinglish.md)
is separate from this concise experiment reference.

The same preview was subsequently used for the [30-node, four-round
random-source practical](../results/graph-burning-30-random-seed-20261026/).
Its **fresh** Giraph result matched the Python final rows (`diff` exit 0),
including six `NB -1` vertices. Four lab-generated PNG/GraphML snapshots
are saved with that result. This is a reproducible non-optimized sequence,
not a source-selection optimum.

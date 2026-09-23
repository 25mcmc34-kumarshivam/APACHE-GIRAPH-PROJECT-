# Verified 30-node Graph Burning run

Giraph read three HDFS part files from
`/user/mca2025/giraph_learning/graph_burning_30_undirected_input` and ran
the source sequence `1:18:3:8`. This input is the explicit
[undirected derivative](../../datasets/thirty-node-undirected-burning/) of
the original directed 30-node dataset; do not mix their results.

The [actual Giraph output](burn-rounds-1-18-3-8.txt) contains 30 vertex
records, with no unburned marker. Each of the 30 first-burn rounds matched
the local Python `--check-sequence 1:18:3:8` prediction exactly.

```text
Round 1:  1 vertex
Round 2:  5 vertices
Round 3: 13 vertices
Round 4: 11 vertices
Total:   30 vertices
```

The sequence was proposed by a **local greedy heuristic**, not chosen by
Giraph. For this particular undirected graph, four rounds is also minimum:
any three-round sequence could cover at most 15 vertices from its first
source, 5 from its second and 1 from its third, a total of 21 < 30 even
without overlap. The [source-selection note](../../study-material/graph-burning-source-selection-30.md)
explains the bound. This does not make the greedy heuristic optimal in
general.

Command used as `mca2025`:

```bash
bash "$HOME/giraph/run_graph_burning.sh" \
  /user/mca2025/giraph_learning/graph_burning_30_undirected_input \
  /user/mca2025/giraph_learning/graph_burning_30_undirected_output \
  1:18:3:8
```

# Undirected teaching version of the 30-node graph

This graph was derived from [`thirty-node-text`](../thirty-node-text/), which
has 30 vertices and 79 **directed** edge records. Classical Graph Burning
is normally studied on an **undirected** graph, so we made an explicit
undirected teaching version rather than silently changing the original.

For each original edge `u -> v`, this new dataset contains **both** `u -> v`
and `v -> u`. If the reverse edge was already present, we keep one copy,
not two. The result has 30 vertex lines, 55 undirected connections (110
directed adjacency entries), divided into three files of ten lines each.
Every weight stays `1`; the burning algorithm ignores weights.

Example: the original graph has `1 -> 2`, while the new graph has both
`1 -> 2` and `2 -> 1`. This matters because otherwise fire could travel
one direction along an edge but not back. **Do not describe results on this
new graph as results on the original directed graph.**

The greedy local checker can propose a sequence:

```bash
python3 scripts/find_small_graph_burning_sequence.py \
  datasets/thirty-node-undirected-burning --greedy
```

`--greedy` is a fast source-selection heuristic. It does not prove the
minimum number of rounds. The exact default mode intentionally rejects
graphs with more than ten vertices. A future Giraph run must separately
verify the proposed sequence on HDFS; local output is not a cluster result.

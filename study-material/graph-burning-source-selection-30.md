# Graph Burning source choice on the 30-node teaching graph

## Which graph did we use?

The earlier [`thirty-node-text`](../datasets/thirty-node-text/) input has
directed edges. Our current teaching version of classical Graph Burning
uses undirected edges. We therefore created a separate
[`thirty-node-undirected-burning`](../datasets/thirty-node-undirected-burning/)
dataset. Each original arrow now has a reverse arrow too. The result has 30
vertices and 55 undirected connections (110 adjacency entries) in three
text files. The original directed files were not changed.

## What did the local program find?

```bash
python3 scripts/find_small_graph_burning_sequence.py \
  datasets/thirty-node-undirected-burning --greedy
```

It chose `1:18:3:8`: source 1 in round 1, 18 in round 2, 3 in round 3,
and 8 in round 4. Its local BFS calculation predicted all 30 vertices
burning by the end of round 4. This is a **local Python prediction**, not a
completed Hadoop/Giraph job. The older PageRank, degree and BFS results
used the original **directed** dataset and must not be mixed with this one.

## Why can we say four is minimum for this particular graph?

Greedy alone cannot prove it. A separate counting argument can:

1. In three rounds, the first source can reach distance at most 2 by the
   final round. The biggest distance-2 neighbourhood in this graph has 15
   vertices.
2. The second source can reach distance at most 1. The biggest such
   neighbourhood has 5 vertices.
3. The third source covers at most itself: 1 vertex.
4. Even imagining no overlaps, `15 + 5 + 1 = 21`, which is less than 30.
   Therefore three rounds cannot cover this particular graph.
5. The local checker predicts `1:18:3:8` covers all vertices in four rounds.
   Together these establish minimum four **for this dataset**, subject to
   checking the input and local calculation.

This reasoning uses undirected edge-count distances. It does not prove
that the greedy method always finds a minimum on other graphs.

## What still needs a lab run?

Copy the three undirected part files to `mca2025`; upload them to a **new**
HDFS input directory, not the original directed one. Check that it has 30
vertex lines, check one real NodeManager, then run the existing Graph Burning
script with `1:18:3:8` and a new output path. Compare all 30 Giraph results
against local predicted burn rounds. Only then call it a verified cluster
result. If YARN is unhealthy, use the
[daily startup guide](../docs/DAILY-LAB-STARTUP.md).

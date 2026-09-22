# Seven-vertex star for Graph Burning validation

Vertex 1 is the centre; vertices 2–7 are leaves. Every edge is listed in
both directions because the graph is undirected. Edge weights are `1` to fit
our shared text input format, though Graph Burning ignores weights.

```text
       2
       |
   3 --1-- 4
     / | \
    5  6  7
```

The drawing is schematic. The authoritative connections are the seven lines
in `graph.txt`: the centre connects to each leaf, and each leaf connects only
to the centre.

Simple manual test: source sequence `1:2`. Round 1 lights the centre (1).
Round 2 spreads from 1 to all six leaves; 2 is also the scheduled new source.
Thus the expected first-burn rounds are `1 -> 1.0` and `2–7 -> 2.0`.

This tests simultaneous spreading to several neighbours. The centre cannot
cover every vertex in just one round, but it covers the star in two. The
second source is a leaf that was unburned *before* round 2; fire reaches it
in the same round it is selected. The simulator records its first burn round
as 2, regardless of which of those two simultaneous events we name first.

# Verified star-graph burning test

The Giraph job completed on the seven-vertex star stored in
[`datasets/graph-burning-star-7/`](../../datasets/graph-burning-star-7/).
The source sequence was `1:2`: ignite vertex 1 in round 1, then vertex 2
in round 2. The HDFS output directory was
`/user/mca2025/giraph_learning/graph_burning_star7_output`.

The [actual output](burn-rounds-1-2.txt) matches the manual prediction:
the centre (vertex 1) first burns in round 1 and all leaves (2–7) first
burn in round 2. A leaf adjacent to the centre receives fire in round 2;
selecting vertex 2 as the new source in that same round does not change
its recorded first-burn round.

This tests a *branching* fire spread: one vertex reaches six neighbours at
once. It does not yet test disconnected components or automatic selection
of a source sequence.

Command used as `mca2025`:

```bash
bash "$HOME/giraph/run_graph_burning.sh" \
  /user/mca2025/giraph_learning/graph_burning_star7_input \
  /user/mca2025/giraph_learning/graph_burning_star7_output \
  1:2
```

# Verified Graph Burning run on a six-vertex cycle

The lab Giraph job ran on the undirected cycle in
[`datasets/graph-burning-cycle-6/`](../../datasets/graph-burning-cycle-6/)
with source sequence `1:3:4`. The HDFS output directory was
`/user/mca2025/giraph_learning/graph_burning_cycle6_output`.

The [actual output](burn-rounds-1-3-4.txt) matches the manual prediction:

- Round 1: source 1 burns.
- Round 2: fire from 1 burns 2 and 6; source 3 burns.
- Round 3: fire reaches 4 and 5; 4 is also the third source.

All six vertices burned within three rounds. The local exact checker also
found that two rounds cannot cover this graph: first source covers at most
itself and its two neighbours by round 2 (three vertices), and the second
source at most itself (one more), fewer than six. This proof is specific to
this cycle; the Giraph run only evaluates the supplied sequence.

# Two-round Graph Burning test on disconnected paths

The six-vertex input is two separate paths:

```text
1 -- 2 -- 3       4 -- 5 -- 6
```

We ran the existing Giraph simulator with source sequence `2:4` and HDFS
output path
`/user/mca2025/giraph_learning/graph_burning_disconnected6_two_round_output`.
The [actual output](burn-rounds-2-4.txt) matched the manual prediction.

Think of the blank space as **no road for fire to travel**. In round 1 we
light vertex 2. In round 2 its fire reaches 1 and 3, while we light vertex
4 in the other group. Fire from 4 could reach 5 only in round 3. Thus 5 and
6 are still unburned when this two-round experiment stops.

The large value `1.7976931348623157E308` is the Java program's
`Double.MAX_VALUE` marker for **unburned**. It is not a real burn time or
distance. A successful Giraph job only means the computation ran; it does
not mean the chosen sources covered the graph.

This test shows that the computation does not invent an edge between separate
input components. It does not prove any minimum burning number or test source
selection automatically. A three-round follow-up with sources `2:5:4`
should cover both paths; that prediction has not yet been verified by a job.

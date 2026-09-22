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
selection automatically.

## Three-round follow-up: both groups covered

We then ran source sequence `2:5:4` with HDFS output path
`/user/mca2025/giraph_learning/graph_burning_disconnected6_three_round_output`.
The [actual output](burn-rounds-2-5-4.txt) was:

| Round | What first burns |
|---:|---|
| 1 | Vertex 2 (first source). |
| 2 | Vertices 1 and 3 from vertex 2; vertex 5 as the second source. |
| 3 | Vertices 4 and 6 from vertex 5; vertex 4 is also the third source. |

All six vertices have finite burn rounds, so this supplied sequence covers
the graph within three rounds. Notice that selecting vertex 4 in round 3
does not make it burn earlier: fire from 5 reaches it in that same round.
This is a coverage result, **not** proof that three rounds are the smallest
possible number for a disconnected graph.

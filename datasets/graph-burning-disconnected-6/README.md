# Six vertices in two disconnected groups

The graph contains two short paths with **no edge between them**:

```text
1 -- 2 -- 3       4 -- 5 -- 6
   group A           group B
```

Each undirected edge is written twice in `graph.txt`, once from each end.
The `:1` is an edge weight required by our shared text reader; the Graph
Burning program ignores weights.

Our first proposed test is `2:4` (two rounds):

- Round 1: choose source 2; vertex 2 burns.
- Round 2: fire from 2 reaches 1 and 3; choose source 4 in the other group.
- Result: 1, 3 and 4 first burn in round 2; 5 and 6 remain unburned.

This shows that fire cannot jump across the blank space between the groups.
To cover group B, we must select a source there and allow enough rounds for
its fire to spread.

Later we can try `2:5:4` (three rounds): by the end of round 3, both groups
should be burned. We will record actual results only after running them.

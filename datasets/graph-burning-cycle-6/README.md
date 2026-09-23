# Six-vertex cycle

```text
1 -- 2 -- 3
|         |
6 -- 5 -- 4
```

Unlike a path, there are two directions around this loop. Every vertex has
two neighbours. Each undirected edge appears in both directions in the input
file. Graph Burning ignores the `:1` weights.

Before running Giraph, we can test the graph with the local exact checker.
It should need three rounds: with only two rounds, the first source reaches
at most itself and its two neighbours, and the second source adds at most
itself. Four covered vertices cannot cover all six.

An example three-round sequence is `1:3:4`: round 1 lights 1; round 2
spreads to 2 and 6 and lights 3; round 3 spreads to 4 and 5, while 4 is
also the third source. Expected first-burn rounds: `1 -> 1`, `2,3,6 -> 2`,
`4,5 -> 3`. This is a manual prediction until a Giraph run verifies it.

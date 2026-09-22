# Nine-Vertex Path for Graph Burning

This undirected path is split across three files to verify that Giraph treats
an HDFS input directory as one graph.

```text
1 -- 2 -- 3 -- 4 -- 5 -- 6 -- 7 -- 8 -- 9
```

Each undirected connection appears in both vertices' adjacency lists. Edge
weight 1 is present because the shared text reader requires weighted edge
tokens, but Graph Burning ignores the weight.

## Source sequence

```text
3:8:6
```

## Manual calculation

| Round | New source | Other vertices reached by spreading | Burned so far |
|---:|---:|---|---|
| 1 | 3 | none | 3 |
| 2 | 8 | 2, 4 | 2, 3, 4, 8 |
| 3 | 6 | 1, 5, 7, 9 | all vertices |

Expected output (`vertex burnRound`):

```text
1  3.0
2  2.0
3  1.0
4  2.0
5  3.0
6  3.0
7  3.0
8  2.0
9  3.0
```

The graph burns completely in three rounds. This agrees with the known path
formula `b(P_n) = ceil(sqrt(n))`, which gives `b(P_9) = 3`.

The colon is deliberate: Giraph's `-ca` option splits settings at commas. A
comma-separated source sequence would be misread as multiple settings.

# Verified Weighted BFS Comparison

These results were produced by Giraph on 16 September 2026 using the dataset
in [`../../datasets/weighted-bfs-comparison/`](../../datasets/weighted-bfs-comparison/).
Both algorithms started from vertex 1.

## Main result

For vertex 6, BFS returned `2.0` because it minimized the number of edges:

```text
1 -> 2 -> 6
```

That route uses two hops but has total weight `10 + 1 = 11`.

Weighted shortest path returned `4.0` because it minimized total edge weight:

```text
1 -> 3 -> 4 -> 5 -> 6
```

That route uses four hops but costs only `1 + 1 + 1 + 1 = 4`.

The saved results were compared with `diff`. Exit code `1` was expected and
confirmed that the outputs differ. The changed values were:

```diff
-2    1.0
+2    10.0
-6    2.0
+6    4.0
```

Vertex 2 also differs because BFS records one hop while weighted shortest path
records the edge cost 10. Vertices 1, 3, 4 and 5 have matching numeric values
only because all edges on their selected routes have weight 1.

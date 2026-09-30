# Nine-node path with ignition rounds inside the input

This is the same undirected path `1--2--3--4--5--6--7--8--9` used in the
earlier Graph Burning experiment, but now the second column tells Giraph
when a vertex should be selected as a new source.

```text
vertexId sourceRound neighbourId:weight ...
3        1           2:1 4:1
8        2           7:1 9:1
6        3           5:1 7:1
```

The other vertices have `sourceRound=0`: they are not manually ignited,
but may burn when fire reaches them. Exactly one vertex is marked for each
round 1, 2 and 3. The input is split across three files to show that the
schedule and graph work across an HDFS input directory. Each undirected
connection is written once on each endpoint's line. Weights are `1` to
fit the reader; Graph Burning ignores them.

Expected result with the new `B`/`NB` output format:

```text
1  B  3
2  B  2
3  B  1
4  B  2
5  B  3
6  B  3
7  B  3
8  B  2
9  B  3
```

The lab Giraph job completed on 30 September 2026; its actual nine rows
match this prediction exactly. The saved run is under
`results/graph-burning-path-9-scheduled/`. This complete-coverage run
does not exercise the `NB -1` branch; a separate incomplete schedule will.

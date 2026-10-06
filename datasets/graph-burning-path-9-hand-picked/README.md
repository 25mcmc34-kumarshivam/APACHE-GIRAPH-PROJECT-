# Nine-node path with hand-picked, non-optimized sources

This is the same undirected path `1--2--3--4--5--6--7--8--9`, split into
three text files. We deliberately chose vertices **1**, **9**, and **5**
for rounds 1, 2, and 3 by hand. No greedy, exact-search, or other Python
source-selection program chose them. This is an arbitrary reproducible
schedule, **not** a claim that it was statistically random or optimal.

Each line is `vertexId sourceRound neighbour:weight...`. A `0` in the
second column means no manual ignition at that vertex. The weights are
written as `1` to match the text input format; ordinary Graph Burning
spreads one edge per round and does not use weighted distances.

Prediction made by following the fire round by round:

| Round | New source | Other vertices newly reached |
|---:|---:|---|
| 1 | 1 | none |
| 2 | 9 | 2 (from 1) |
| 3 | 5 | 3 (from 2), 8 (from 9) |

Output predicted before the run and **confirmed by Giraph on 6 October
2026**:

```text
1  B   1
2  B   2
3  B   3
4  NB -1
5  B   3
6  NB -1
7  NB -1
8  B   3
9  B   2
```

The actual output is saved under `results/graph-burning-path-9-hand-picked/`.
This makes an important point for the supervisor: picking arbitrary legal
sources does not guarantee that every vertex burns within three rounds.
The experiment tests the Giraph simulation without solving the source
optimization problem. If every vertex must burn, we either need more
rounds or a different schedule; that is a separate question.

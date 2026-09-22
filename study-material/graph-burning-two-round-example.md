# Graph Burning: our two-round experiment, explained from zero

We tested Graph Burning on a path of nine vertices. A **vertex** is a point;
an **edge** is a connection between two points. The input graph is:

```text
1 -- 2 -- 3 -- 4 -- 5 -- 6 -- 7 -- 8 -- 9
```

In this experiment, a burning vertex can pass fire to its neighbour **in the
next round**. We also choose **one new source** (a vertex that we light
directly) in each round. We gave the program the sequence `2:8`: light vertex
2 in round 1, then light vertex 8 in round 2. The colon separates the two IDs;
it is not an edge or a mathematical operation.

## Watch the rounds like a story

**Before round 1:** Nothing has burned.

**Round 1:** We light vertex 2. Only vertex 2 is burned so far. Its fire is
sent toward vertices 1 and 3, but it arrives in the *next* round.

```text
1 -- [2] -- 3 -- 4 -- 5 -- 6 -- 7 -- 8 -- 9
      ^ newly burned in round 1
```

**Round 2:** Fire from 2 reaches vertices 1 and 3. We also light the second
source, vertex 8. Thus four vertices have burned by the end of round 2:
`1, 2, 3, 8`.

```text
[1] -- [2] -- [3] -- 4 -- 5 -- 6 -- 7 -- [8] -- 9
 ^       ^       ^                        ^
 r2      r1      r2                       r2
```

We scheduled only **two rounds**, so we stop here. Vertex 9 is beside 8, but
8 was lit *during* round 2. Its fire would arrive at 9 in round 3, which this
experiment does not include. Similarly, fire from 3 would reach 4 in round 3.

## How to read the output

The left column is the vertex ID. The right column says **the first round in
which that vertex burned**. For example, `3  2.0` means vertex 3 first burned
in round 2. The `.0` appears because the Java program stores its vertex value
as a `DoubleWritable` number; the result is still a whole-number round.

| Vertex | Output | Read it as |
|---:|---:|---|
| 1 | 2.0 | Fire from 2 reached it in round 2. |
| 2 | 1.0 | We selected it as the first source. |
| 3 | 2.0 | Fire from 2 reached it in round 2. |
| 4–7 | `1.7976931348623157E308` | Not burned by the end of round 2. |
| 8 | 2.0 | We selected it as the second source. |
| 9 | `1.7976931348623157E308` | Not burned by the end of round 2. |

That huge number is Java's `Double.MAX_VALUE`. Our code uses it as an
**unburned marker** (similar to “infinity”). It is **not** a measured distance,
a probability, or a real burn round. The exact output copied from the lab is
in [burn-rounds-2-8.txt](../results/graph-burning-path-9/burn-rounds-2-8.txt).

The job saying **“completed successfully”** means Giraph ran without an
execution error. It does **not** mean our two-source sequence burned every
vertex. To check a burning sequence, look for any unburned markers. If even
one remains, the graph was not completely burned in the scheduled rounds.

## Why this test matters

Earlier we tested `3:8:6` on the same path and all nine vertices burned by
round 3. Now `2:8` leaves five vertices unburned after round 2. Together,
these tests show that we must distinguish **a program that runs** from **a
source sequence that covers the graph**. Our Giraph program currently
evaluates a sequence we provide; it does not automatically choose the best
sources or print a separate `UNBURNED` label.

To repeat this test from the `mca2025` account, use a new HDFS output path
because Hadoop refuses to overwrite an existing job output:

```bash
bash "$HOME/giraph/run_graph_burning.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_input \
  /user/mca2025/giraph_learning/graph_burning_path9_two_round_output_NEW \
  2:8
```

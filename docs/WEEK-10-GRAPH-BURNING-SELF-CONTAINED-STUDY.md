# Week 10 study sheet — Graph Burning, 18–24 September 2026

Read **only this page** to prepare for the 24 September meeting. It contains the actual data, actual outputs, calculations, code ideas, checks, and honest limitations. File names are included so we can point to evidence if Sir asks, but understanding the work does not require opening another file. The separate test-PC installation is not part of this week's research report.

## What to tell Sir first

> Last week we had PageRank, degree, BFS, and shortest-path results on a 30-vertex directed graph stored in three text files. This week, following your Graph Burning direction, we studied the burning rule and added a Giraph Java computation that **simulates a supplied sequence of fire sources**. We first predicted results by hand on small graphs, then ran Giraph and compared every vertex's first-burn round. We also wrote a separate local Python checker: it validates sequences, searches exhaustively for small graphs, and gives a greedy suggestion for larger ones. On a nine-node path, a seven-node star, two disconnected paths, a six-node cycle, and a separate undirected 30-node graph, the saved Giraph outputs match our predictions. For the undirected 30-node graph, sources `1:18:3:8` cover all nodes in four rounds, and a counting lower bound shows three rounds cannot work on this graph. The Giraph program does not yet choose sources automatically. We have studied ICM, LTM, and SIR conceptually, but not implemented them.

The laboratory is **one Ubuntu computer** running Hadoop in pseudo-distributed mode. Three input files are three pieces of one graph, **not** three computers. `hduser` starts Hadoop services; `mca2025` builds/submits Giraph jobs.

## 1. The idea, as if explaining it to a beginner

A *graph* has vertices (people/places/computers) and edges (connections). Imagine information or fire starting at one chosen vertex. In Graph Burning, time is split into rounds:

1. Select one new source vertex in each round.
2. Fire from vertices burning in the previous round moves across one connection to their neighbours.
3. A burned vertex stays burned. Record **the first round** in which it burned.

For classical undirected Graph Burning, fire can travel either way along a connection. Our text files therefore show both directions: if `2` lists `3`, then `3` also lists `2`. The `:1` after a neighbour is an edge weight demanded by our shared input reader; burning **does not use** the weight. The *burning number* is the smallest number of rounds for which some valid choice of sources burns every vertex. Simulating one chosen sequence is easier than finding the best sequence; these are different tasks. This follows the standard source-and-spread definition of Graph Burning (e.g. the research survey “A survey of graph burning,” arXiv:2009.10642).

One useful calculation lets us predict the answer without Giraph. Suppose source `s` is selected in round `r`, and vertex `v` is `d` edges away from it. Fire from `s` can first reach `v` in round **`r + d`**. With several sources, take the earliest arrival. If that arrival is after the last configured round, `v` is still unburned. For example, on `1--2--3--4--5`, source 3 in round 1 reaches vertex 5 in round `1+2=3`.

Do not confuse the outputs:

| BFS from one fixed source | Graph Burning with several sources |
|---|---|
| Source has distance **0**. | First source burns in round **1**. |
| Answer is minimum number of **hops**. | Answer is **first burn round**. |
| No new sources later. | One scheduled new source per round. |
| On a directed graph, follows outgoing arrows. | For our classical tests, each undirected connection is written both ways. |

The huge output value `1.7976931348623157E308` is Java `Double.MAX_VALUE`. Our Java program uses it as a marker meaning **not burned by the end of the supplied sequence**. It is not a real round number and does not mean Giraph failed.

## 2. Exactly what the input line means

All this week's graph files are plain-text adjacency lists. One line defines one vertex:

```text
2 1:1 3:1
```

`2` is the vertex ID. `1:1` says it has an outgoing connection to vertex 1 with stored weight 1. `3:1` likewise points to vertex 3. A line with only `6` means vertex 6 exists but has no outgoing connections. **Line direction matters to the computer**, even if our intended graph is undirected. For an undirected `2--3`, there must be `3:1` on vertex 2's line **and** `2:1` on vertex 3's line.

The files are local repo files under `datasets/`. They were copied to a matching HDFS input directory. When a dataset has `part-01.txt`, `part-02.txt`, `part-03.txt`, we pass the HDFS **directory** to Giraph; Hadoop reads all three as one graph. A vertex in part 1 can refer to a vertex in part 3. The reader class `LongDoubleFloatTextInputFormat` turns a text line into a Giraph vertex: `LongWritable` ID, `DoubleWritable` vertex value (starting at zero), and `FloatWritable` edge weights. We explicitly select it with `-vif`; renaming a JSON file to `.txt` would not work.

Giraph writes a new HDFS output directory containing `part-m-*` files. The chosen output formatter writes `vertexID<TAB>value`. For this job the value is first burn round. We saved sorted copies under `results/`. An HDFS output directory must be new for each run; Hadoop will not overwrite an old result. Do not mix the input file name `part-01.txt` with an output file name `part-m-*`.

## 3. Every small graph, input and output together

### A. Nine-vertex path, stored in three files

This graph is `1--2--3--4--5--6--7--8--9`. It is divided into three physical files, each with three vertex lines. **The boundary between files does not cut an edge.**

`datasets/graph-burning-path-9/part-01.txt`:

```text
1 2:1
2 1:1 3:1
3 2:1 4:1
```

`part-02.txt`:

```text
4 3:1 5:1
5 4:1 6:1
6 5:1 7:1
```

`part-03.txt`:

```text
7 6:1 8:1
8 7:1 9:1
9 8:1
```

First run: source sequence **`3:8:6`**. The colons mean “3 in round 1, 8 in round 2, 6 in round 3.”

| Round | New source | Spread from an earlier burning round | Newly burned this round |
|---:|---:|---|---|
| 1 | 3 | None yet | 3 |
| 2 | 8 | From 3 to 2 and 4 | 2, 4, 8 |
| 3 | 6 | From 2 to 1; 4 to 5; 8 to 7 and 9 | 1, 5, 6, 7, 9 |

Actual Giraph output, saved as `results/graph-burning-path-9/burn-rounds-3-8-6.txt`:

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

So every vertex burns within 3 rounds. Two rounds cannot burn all nine vertices on this path: the first source covers at most itself and its two neighbours by round 2 (3 vertices); the second source adds at most itself (1 vertex), for at most 4. Therefore **3 is minimum** for this graph, not merely a successful sequence.

Second run: **`2:8`**, intentionally only two rounds. Round 1 burns 2. Round 2 spreads to 1 and 3 while source 8 burns. Actual saved output `results/graph-burning-path-9/burn-rounds-2-8.txt` is `1→2, 2→1, 3→2, 8→2`, and 4,5,6,7,9 have the huge unburned marker. This shows that “job completed” and “graph fully burned” are different statements.

### B. Seven-vertex star

Vertex 1 is the centre; 2–7 are leaves. All input is one file, `datasets/graph-burning-star-7/graph.txt`:

```text
1 2:1 3:1 4:1 5:1 6:1 7:1
2 1:1
3 1:1
4 1:1
5 1:1
6 1:1
7 1:1
```

Sources **`1:2`**. Round 1 burns centre 1. In round 2 its fire reaches **all six leaves simultaneously**; node 2 is also the scheduled second source in that same round. The saved Giraph output `results/graph-burning-star-7/burn-rounds-1-2.txt` is `1→1.0` and `2,3,4,5,6,7→2.0`. One round can burn only the selected source, so 2 rounds is minimum for this star. Selecting a node that fire reaches in the *same* round is accepted by our local validator; it was unburned before that round began.

### C. Two disconnected three-node paths

This is `1--2--3` and, separately, `4--5--6`. There is **no** edge between the groups. The one input file `datasets/graph-burning-disconnected-6/graph.txt` contains:

```text
1 2:1
2 1:1 3:1
3 2:1
4 5:1
5 4:1 6:1
6 5:1
```

With sources **`2:4`**: round 1 burns 2; round 2 spreads to 1 and 3 and ignites 4. Actual output: `1→2, 2→1, 3→2, 4→2`, while 5 and 6 stay unburned. Saved as `results/graph-burning-disconnected-6/burn-rounds-2-4.txt`.

With **`2:5:4`**: round 1 burns 2; round 2 burns 1 and 3 through spread and 5 as a new source; round 3 burns 4 and 6 through spread from 5. Node 4 is also the third scheduled source, but its first-burn round is still 3. Actual output, `results/graph-burning-disconnected-6/burn-rounds-2-5-4.txt`:

```text
1  2.0
2  1.0
3  2.0
4  3.0
5  2.0
6  3.0
```

The exhaustive local checker found no complete two-round sequence, so the minimum is 3 for this particular disconnected graph. It also demonstrates that fire cannot magically cross between components; a source must be placed in the other component.

### D. Six-vertex cycle

Input `datasets/graph-burning-cycle-6/graph.txt` describes `1--2--3--4--5--6--1`:

```text
1 2:1 6:1
2 1:1 3:1
3 2:1 4:1
4 3:1 5:1
5 4:1 6:1
6 5:1 1:1
```

Sources **`1:3:4`**: round 1 burns 1; round 2 burns 2 and 6 by spread plus source 3; round 3 burns 4 and 5. Giraph output, saved in `results/graph-burning-cycle-6/burn-rounds-1-3-4.txt`, is `1→1, 2→2, 3→2, 4→3, 5→3, 6→2`. Two rounds cover at most 3 vertices from the first source plus 1 second source, fewer than 6, so minimum is 3 here.

## 4. The 30-node Graph Burning experiment

The earlier PageRank/BFS graph had 30 vertices, **79 directed edges**. Classical Graph Burning is normally explained on **undirected** graphs, so we made a **separate** dataset, `datasets/thirty-node-undirected-burning/`. For each original connection, it includes both directions and deduplicates repeats. It contains 30 vertices, 55 undirected connections, and 110 adjacency entries. It is split into three files of ten vertex records each. The original directed files were not changed, and **old PageRank/BFS numbers must not be described as results on this new undirected graph**.

Here is the complete Graph Burning input. Blank lines below mark file boundaries; the real files are `part-01.txt` (1–10), `part-02.txt` (11–20), and `part-03.txt` (21–30):

```text
1 2:1 5:1 6:1 30:1
2 1:1 3:1 7:1
3 2:1 4:1 8:1
4 3:1 5:1 9:1
5 1:1 4:1 10:1 11:1
6 1:1 7:1 10:1 12:1
7 2:1 6:1 8:1
8 3:1 7:1 9:1 13:1
9 4:1 8:1 10:1
10 5:1 6:1 9:1 15:1

11 5:1 12:1 15:1 16:1
12 6:1 11:1 13:1 17:1
13 8:1 12:1 14:1 18:1
14 13:1 15:1 19:1
15 10:1 11:1 14:1 20:1
16 11:1 17:1 20:1 21:1
17 12:1 16:1 18:1 22:1
18 13:1 17:1 19:1 23:1
19 14:1 18:1 20:1 24:1
20 15:1 16:1 19:1 25:1

21 16:1 22:1 25:1 26:1
22 17:1 21:1 23:1 27:1
23 18:1 22:1 24:1 28:1
24 19:1 23:1 25:1 29:1
25 20:1 21:1 24:1 30:1
26 21:1 27:1 30:1
27 22:1 26:1 28:1
28 23:1 27:1 29:1
29 24:1 28:1 30:1
30 1:1 25:1 26:1 29:1
```

The local Python greedy method proposed sources **`1:18:3:8`**, one per round. The same sequence was run in Giraph on the three-file HDFS directory. Actual output (`results/graph-burning-30-undirected/burn-rounds-1-18-3-8.txt`):

```text
1 1.0    2 2.0    3 3.0    4 3.0    5 2.0
6 2.0    7 3.0    8 4.0    9 4.0   10 3.0
11 3.0  12 3.0   13 3.0   14 4.0   15 4.0
16 4.0  17 3.0   18 2.0   19 3.0   20 4.0
21 4.0  22 4.0   23 3.0   24 4.0   25 3.0
26 3.0  27 4.0   28 4.0   29 3.0   30 2.0
```

Read one entry as “vertex 18 first burned in round 2,” not “vertex 18 is two edges from vertex 1.” There are 1 vertex at round 1, 5 at round 2, 13 at round 3, and 11 at round 4: `1+5+13+11=30`. No unburned markers remain. All 30 Giraph values matched the Python prediction.

Why is 4 **minimum** for *this* graph? In a hypothetical three-round schedule, the round-1 source has radius at most 2 by the end; the largest radius-2 neighbourhood in this input contains 15 vertices. The round-2 source has radius at most 1, with at most 5 vertices. The round-3 source contributes at most itself, 1 vertex. Even pretending these sets do not overlap, `15+5+1=21`, which is less than 30. Thus 3 rounds cannot cover it; our 4-round sequence does. The greedy Python program did not prove this by itself—the **separate counting argument** supplies the lower bound. Greedy is not guaranteed optimal on other graphs.

## 5. How the Java program works, piece by piece

The project file is `src/LearningGraphBurningComputation.java`. Its core class extends:

```java
BasicComputation<LongWritable, DoubleWritable, FloatWritable, DoubleWritable>
```

Read the four types in order: vertex ID (whole number), value stored at a vertex (its first burn round), value stored on an edge (weight; ignored for burning), and message sent between vertices (the next burn round). Hadoop's `Writable` wrappers make values transferable/serializable in the Giraph job.

`SOURCE_SEQUENCE` defines the user-supplied setting `LearningGraphBurning.sourceSequence`. `getSources()` reads a string such as `3:8:6`, splits at colons, converts each token to a `long`, and returns an ordered array. We deliberately do **not** use commas: Giraph treats a comma inside `-ca` as a boundary between different settings. The first `3,8,6` attempt produced “Unable to parse custom argument: 8” **before** the YARN job started. We fixed the parser/runner to use colons, rebuilt, and reran.

Giraph calls `compute(vertex, messages)` separately for each active vertex in each *superstep*. The vertex can see its own ID/value/edges and incoming messages, not the entire graph as one in-memory object. `getSuperstep()` starts at 0, while our visible burning rounds start at 1, so `currentRound = superstep + 1`. At superstep 0, every vertex value is set to `Double.MAX_VALUE` (not burned). `earliestRound` starts from the stored value. The `for (message : messages)` loop takes the minimum of all fire-arrival messages, because a vertex should remember its **first** burn.

The code checks whether this vertex ID equals the scheduled source ID for the current round. If so, it also considers `currentRound` as a possible first-burn time. `newlyBurned` is true only when this is earlier than the stored value. Only then do we save the round and send `(earliestRound + 1)` to each outgoing neighbour, to arrive in Giraph's next superstep. We do not send past the final configured round. Previously burned vertices do not repeatedly send fire. The program calls `voteToHalt()` only at the end of the final round; if it halted early, a future scheduled source with no incoming message might never be activated.

The Java computation **simulates** a sequence. It does not find the minimum sequence and does not enforce that every proposed source exists, is distinct, or was unburned before its round. That is why we use the local Python validator before treating a sequence as valid. Giraph output also does not include “source/not source” flags; it has only vertex ID and first-burn round.

`src/LongDoubleFloatTextInputFormat.java` is a commented learning copy of the text reader already included in our Giraph build. Its reader splits the line into tokens; the first token becomes the vertex ID; each `neighbour:weight` token becomes an outgoing `Edge`; it initializes a `DoubleWritable` vertex value. The runner names this class with `-vif`, so all the Java type choices line up. We did not write a new custom graph storage system this week.

## 6. How the Python checker works, piece by piece

The project file is `scripts/find_small_graph_burning_sequence.py`. **It runs locally in Python, not inside Hadoop/Giraph.** It is a reference calculation and source-selection aid.

| Function or variable | What it does in simple terms |
|---|---|
| `read_graph(path)` | Reads one `.txt` file or every `.txt` part in a folder. Makes a dictionary like `{1: {2, 3}}`. Rejects duplicate vertex lines, malformed `neighbour:weight`, undefined neighbours, and missing reverse edges because this checker expects an undirected graph. It parses weights for validity but ignores them for burning. |
| `distances_from(graph, source)` | Uses a FIFO `deque` queue to run ordinary BFS and find the number of edges from one source to every reachable vertex. Vertices in another disconnected component are absent (treated as infinitely far). |
| `burn_rounds(graph, sequence)` | Rejects nonexistent, repeated, or already-burned-before-its-round sources. For each vertex computes earliest `chosen round + BFS distance`. If earliest is after the number of scheduled rounds, marks it `UNBURNED`. Same-round arrival and source selection are allowed. |
| `find_sequence(graph, max_states)` | Exact small-graph search: tries total lengths `k=1,2,...`; for each length, tries legal source orders by backtracking. A source selected in round `i` can cover a radius of `k-i` by the end. Bit masks track covered vertices efficiently. The first complete length is minimum **only if the search finishes**. It has a state budget and the command limits exact mode to at most 10 vertices. |
| `greedy_sequence(graph)` | A faster heuristic. For a proposed total length, each round chooses a legal source whose allowed radius covers the most *new* vertices; ties use the smallest ID. It can find a covering sequence, but it does **not** examine every source order, so cannot prove optimality by itself. |
| `main()` | Reads command-line arguments, chooses exact / `--greedy` / `--check-sequence` mode, prints source order, coverage count, and each first-burn round. It exits with an error rather than claiming an exact answer when the search budget is exhausted. |

Examples (run locally from the repository root):

```bash
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-path-9
python3 scripts/find_small_graph_burning_sequence.py datasets/thirty-node-undirected-burning --greedy
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-path-9 --check-sequence 3:8:6
python3 -m unittest discover -s tests -p 'test_small_graph_burning_search.py'
```

The exact checker returned minimum round counts **path 9 = 3, star 7 = 2, disconnected 6 = 3, cycle 6 = 3**. The 30-node graph used `--greedy`, not exact mode. `tests/test_small_graph_burning_search.py` contains **11 passing tests**, including those four counts, greedy coverage, invalid source rejection, reverse-edge/duplicate-line rejection, and search-limit behavior. This is software testing of the local checker; matching Giraph output is a separate experiment.

## 7. The shell runner and Maven build: what we actually typed and why

`scripts/run_graph_burning.sh` takes three arguments: HDFS input directory, **new** HDFS output directory, and colon-separated source sequence. A representative run is:

```bash
bash "$HOME/giraph/run_graph_burning.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_input \
  /user/mca2025/giraph_learning/graph_burning_path9_output \
  3:8:6
```

The script sets/uses Java 8 and Hadoop paths, checks the shaded Giraph JAR, checks that HDFS input exists and output does not, checks for a `RUNNING` YARN NodeManager, then runs `hadoop jar` with `GiraphRunner` and `LearningGraphBurningComputation`. Important options:

| Option | Meaning |
|---|---|
| `-vif LongDoubleFloatTextInputFormat` | How to parse text graph lines. |
| `-vip INPUT` | HDFS input file or directory. |
| `-vof IdWithValueTextOutputFormat` | Print vertex ID and its calculated value. |
| `-op OUTPUT` | New HDFS output directory. |
| `-w 1` | One Giraph worker on this single-node lab setup. |
| `-ca mapred.job.tracker=yarn` | Use YARN rather than accidentally using the local job runner in this setup. |
| `-ca LearningGraphBurning.sourceSequence=3:8:6` | Supply the ignition order to every worker. |

The script finally reads `part-m-*` output and sorts rows numerically for easier checking. It does not change the HDFS results. When the Java source changed, we copied it into the server's Giraph examples package and rebuilt with Maven. Maven compiles the code into `.class` files and assembles the `giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar`; the shading resolves the earlier Guava/Hadoop version conflict. `jar tf ... | grep LearningGraphBurningComputation.class` showed that the new class was packaged. **Maven BUILD SUCCESS means compilation/packaging succeeded; it does not prove the algorithm is correct.** The manual predictions, Giraph outputs, and Python tests are the correctness evidence.

We still sometimes see NodeManager disappear or a stale YARN registration after a job. That is an environment reliability problem, separate from burning logic. We check the real NodeManager process, active applications, and node list, and perform a clean YARN restart as `hduser` when needed. A permanent cause/fix is **not** established, so do not promise uninterrupted runs or quote performance timings from these teaching experiments.

## 8. Models Sir mentioned, and what we did not do yet

Graph Burning (GB) is the deterministic source-and-spread task implemented this week. **Independent Cascade Model (ICM)** instead uses activation probabilities: a newly active vertex gets a chance to activate neighbours. **Linear Threshold Model (LTM)** activates a vertex when accumulated weighted influence from active neighbours crosses its threshold. **SIR** tracks susceptible, infected, and recovered states; infected vertices may infect neighbours and later recover. The important distinction is that these are **different diffusion rules and research questions**, not other names for our Graph Burning Java class. We have notes on them but **no verified Giraph jobs/results for ICM, LTM, or SIR**. The original IC/LT comparison is developed in Kempe, Kleinberg & Tardos, “Maximizing the Spread of Influence through a Social Network”; it is background reading, not evidence of an implementation here.

## 9. What has been proved, what has only been tested, and what remains

- **Verified Giraph simulations:** all saved output rows for path, star, disconnected paths, cycle, and the undirected 30-node graph matched the manual/local prediction for the specified sequence.
- **Minimum-round conclusions for these particular graphs:** path 9 = 3, star 7 = 2, disconnected 6 = 3, cycle 6 = 3, and the undirected 30-node derivative = 4. Small counts were checked by exact local search and/or simple bounds; the 30-node result uses the separate `15+5+1<30` lower bound plus four-round coverage.
- **Not proved:** that the greedy selector always finds an optimum; that the Java class chooses optimal sources; that the same results hold on a much larger real social-network dataset; or that the job scales across multiple physical machines.
- **Next decisions to ask Sir:** Should we first make source selection distributed inside Giraph, move to a substantially larger real dataset, or implement one of ICM/LTM/SIR? What inputs/parameters and evaluation measurements does he expect? Separately, stabilize NodeManager so repeated experiments are reliable.

For the meeting, show one hand calculation (`3:8:6` on the path), one example of a successful-but-incomplete job (`2:8`), the 30-node four-round result and its lower bound, and the Java/Python division of work. That demonstrates understanding rather than only showing terminal screenshots.

# Complete project brief for the 24 September 2026 meeting

This is the one file to read before speaking to Sir. It covers the **shared lab project**, its actual input files, programs, outputs, checks, problems, and remaining work. The separate installation experiment on another PC is intentionally excluded. The links below point to the evidence in this repository; where an older README still describes a future plan, the saved result and the current weekly report take precedence.

If you want **only this week's Graph Burning work without opening any evidence links**, read the [self-contained Week 10 study sheet](WEEK-10-GRAPH-BURNING-SELF-CONTAINED-STUDY.md) instead. It puts the full graph inputs, outputs, and code explanation directly on one page.

## 1. A two-minute opening you can say aloud

> Our project is *Implementation of Distributed Graph Algorithms for Social Network Problems using Apache Giraph Framework*. We began by learning Linux, graph concepts, parallel/distributed computing, Hadoop, Pregel, and Giraph. On the SCIS lab computer we set up Java 8, Hadoop 2.7.7, Giraph, HDFS, and YARN. We then ran PageRank, in-degree, out-degree, BFS, and weighted shortest path. Sir asked us to move beyond a very small JSON graph, so we made a 30-vertex, 79-directed-edge text dataset split into three input files. Giraph reads that directory as one graph. We verified all five computations and compared BFS with weighted shortest path on a separate example where their answers differ. This week, after Sir's Graph Burning direction, we implemented a Giraph simulation for a supplied ignition sequence. We tested path, star, disconnected, cycle, and 30-vertex undirected graphs. A local Python program validates/selects sequences; Giraph runs the actual burning simulation. We have evidence for the results, but distributed source selection and a permanent YARN reliability fix remain future work.

Do **not** say we implemented ICM, LTM, or SIR: so far we have studied their meanings, not built them. Do **not** say the 30-node run used 30 computers: it was one lab machine with a single-node, pseudo-distributed Hadoop setup.

## 2. What runs where

| Part | Meaning in this project |
|---|---|
| Lab Linux machine | The computer provided in the SCIS CI Lab. We reach it by SSH. Its IP can change. |
| `hduser` | Account used to start HDFS and YARN services. |
| `mca2025` | Account used for Giraph source/builds and submitting graph jobs. |
| HDFS | Stores graph input directories and job output directories. This is not the same as a normal Linux folder. |
| YARN | Allocates resources to the submitted Giraph/MapReduce job. It needs a healthy NodeManager. |
| Giraph | Runs a vertex-centric computation: each vertex holds a value, examines its outgoing edges, receives messages from the previous *superstep*, and may send messages for the next one. |
| Maven | Compiles Java and packages classes/dependencies into the shaded examples JAR. It is a **build** step, not a graph calculation. |
| `hadoop jar ... GiraphRunner ...` | Submits an already-built computation class to Hadoop/YARN. The shell scripts save us from repeatedly typing this long command. |

Normal workflow: write or update local `src/*.java` → copy it into the matching package of the server's Giraph source tree → Maven build if Java changed → confirm the `.class` is in the JAR → put data in HDFS → run a script as `mca2025` → inspect HDFS `part-m-*` output → copy verified results into `results/`. A new dataset or a different source ID normally does **not** require a rebuild; a changed Java class does. To begin a fresh lab session, start HDFS/YARN as `hduser`, check one `RUNNING` node, then submit as `mca2025`. The exact service checks are in [daily lab startup](DAILY-LAB-STARTUP.md).

## 3. The three input/output ideas to understand first

### Old JSON graph

The [five-node JSON file](../datasets/five_node_graph.json) has one vertex per line, for example:

```text
[3,0,[[2,1],[4,1]]]
```

This means vertex ID `3`, initial vertex value `0`, and outgoing edges `3 → 2` and `3 → 4`, both weight `1`. The five lines define six **directed** edges: `1→2`, `2→3`, `3→2`, `3→4`, `4→3`, `5→3`. The original PageRank and shortest-path scripts select `JsonLongDoubleFloatDoubleVertexInputFormat` to read this structure.

### New plain-text adjacency lists

The [30-node text graph](../datasets/thirty-node-text/README.md) uses one vertex per line too, but in a simpler form:

```text
5 1:1 10:1 11:1
```

This means vertex `5` has outgoing edges to `1`, `10`, and `11`, each with weight `1`. A line containing only `6` defines vertex `6` with no outgoing edges. The `.txt` extension alone does not tell Giraph how to parse it. The run command explicitly selects `LongDoubleFloatTextInputFormat` with `-vif`. That reader converts numeric IDs to `LongWritable`, vertex values to `DoubleWritable` (initially zero), and edge weights to `FloatWritable`. Our [annotated reader copy](../src/LongDoubleFloatTextInputFormat.java) explains this; the matching reader already exists in the Giraph source/JAR.

For the 30-node graph, `part-01.txt`, `part-02.txt`, and `part-03.txt` have ten vertex lines each. We upload all three under **one HDFS input directory** and pass the directory as `-vip`. Giraph/Hadoop consumes all the files as one logical graph; an edge may point to a vertex defined in another part. We checked there are 30 unique vertex IDs, 79 directed edges, and no undefined endpoints. Three input files show partitioned input, **not** three machines or three workers.

### Output is a new HDFS directory

The output format `IdWithValueTextOutputFormat` writes `vertexID<TAB>value`, for example `8<TAB>0.04154556808415233`. It writes under a newly named HDFS output directory; `part-m-*` are the output files. The meaning of `value` depends on the algorithm: PageRank score, degree count, hops, weighted cost, or first burn round. Giraph refuses to overwrite an existing output path. Saved copies in `results/` are the meeting evidence, not live HDFS paths. `1.7976931348623157E308` is Java `Double.MAX_VALUE`: interpret it as **unreachable/unburned**, not a genuine distance or time.

## 4. Every computation we have run

| Algorithm | Question answered | Main code | How it works | Important result |
|---|---|---|---|---|
| PageRank | Which vertices receive more importance through incoming links? | Giraph's `SimplePageRankComputation` | In repeated supersteps, vertices distribute score along outgoing links and update from received contributions. | On five nodes, vertex 3 is highest (`0.458138...`). On the 30-node directed graph, vertex 8 is highest (`0.041545...`), followed by 6. This is a relative score, not a degree count. |
| Out-degree | How many outgoing directed edges leave each vertex? | [LearningOutDegreeComputation.java](../src/LearningOutDegreeComputation.java) | `getNumEdges()` already knows the local outgoing list; write that count and halt. No messages needed. | On the 30-node graph, counts sum to `79`. |
| In-degree | How many incoming directed edges reach each vertex? | [LearningInDegreeComputation.java](../src/LearningInDegreeComputation.java) | In superstep 0, send one marker on every outgoing edge. In superstep 1, each vertex counts markers it received and halts. | On the 30-node graph, counts also sum to `79`. Example: original node 1 has out-degree 2 but in-degree 3. |
| BFS | What is the fewest **number of edges/hops** from one source? | [LearningBfsComputation.java](../src/LearningBfsComputation.java) | Set source distance 0 and others to infinity; a vertex with a better distance sends distance+1 to its outgoing neighbours. Edge weights are ignored. | From 1 on the 30-node directed graph: 30 reachable vertices; maximum distance 8 hops (vertices 26 and 30). |
| Weighted shortest path | What is the least **sum of edge weights** from one source? | Giraph's `SimpleShortestPathsComputation` | Propagate proposed distance plus each edge's weight, keeping the smallest candidate. | On the 30-node graph it equals BFS because every weight is 1; the separate six-node weighted graph shows the difference. |
| Graph Burning | With one supplied new source per round and fire moving one edge per round, when does each vertex first burn? | [LearningGraphBurningComputation.java](../src/LearningGraphBurningComputation.java) | At each Giraph superstep, ignite the scheduled source and process fire messages from the previous round; newly burned vertices send fire to outgoing neighbours for the next round. | Saved results on five graph shapes; details below. The Java class evaluates a supplied sequence—it does **not** discover an optimal sequence. |

The four generic types in our `BasicComputation<LongWritable, DoubleWritable, FloatWritable, DoubleWritable>` are, in order: vertex ID, mutable vertex value, edge value/weight, and message value. `vertex.voteToHalt()` stops a vertex until a new message wakes it; the burning class deliberately keeps vertices active until the final scheduled round so that a later source can ignite even without a message. Giraph supersteps start at `0`; Graph Burning rounds shown to people start at `1`.

### Exact small-graph values worth knowing

The five-node results are [PageRank](../results/pagerank.txt), [out-degree](../results/outdegree.txt), [in-degree](../results/indegree.txt), and [shortest path from 1](../results/shortest-path-from-1.txt) / [from 5](../results/shortest-path-from-5.txt). Node 3 has out-degree 2 and in-degree 3. From node 1, distances are `1:0, 2:1, 3:2, 4:3`, while node 5 is unreachable (there is no directed route to it). From node 5, distances are `5:0, 3:1, 2:2, 4:2`, while node 1 is unreachable. This is why arrow direction matters.

On the 30-node graph, all five [saved outputs](../results/thirty-node-text/README.md) contain 30 rows. The BFS/shortest-path equality was checked with a file comparison, not guessed. [This walkthrough](BFS-THIRTY-NODE-WALKTHROUGH.md) explains each BFS level, and the [full graph diagram](../diagrams/thirty-node-full-graph.svg) shows every edge; its blue edges are **one** BFS discovery tree, not the only possible routes.

### The six-node example that separates BFS and weighted shortest path

The [weighted input](../datasets/weighted-bfs-comparison/graph.txt) includes `1 2:10 3:1`, followed by `2→6` cost 1 and `3→4→5→6` cost 1 per edge. From source 1 to node 6:

- BFS picks the two-edge route `1→2→6`, so it reports **2 hops**; it does not care that this route costs 11.
- Weighted shortest path picks `1→3→4→5→6`, so it reports **cost 4**; node 2's own cheapest cost is 10.

Compare the [BFS output](../results/weighted-bfs-comparison/bfs-from-1.txt) with the [weighted output](../results/weighted-bfs-comparison/shortest-path-from-1.txt). This answers the common question “why do we need two algorithms?”

## 5. This week's Graph Burning work

Graph Burning is a **deterministic** spreading problem here. In round 1 choose one source. In every later round, choose another source and let fire from previously burning vertices move across one edge. A vertex's output is the **first round** in which it burns, not a BFS distance. For the classical undirected teaching graphs, each connection is written in both directions in the text files; otherwise Giraph's outgoing-edge messages would only travel one way. The `:1` weights satisfy the shared text reader but burning ignores their numeric value.

| Dataset and input file(s) | Sources supplied in round order | Actual result and interpretation |
|---|---|---|
| [Nine-node path](../datasets/graph-burning-path-9/) `1--2--...--9`, split into three files | `3:8:6` | All 9 burned by round 3. Node 3 burns in round 1; 2,4,8 in round 2; 1,5,6,7,9 in round 3. [Saved output](../results/graph-burning-path-9/burn-rounds-3-8-6.txt). For a nine-node path, the minimum is 3. |
| Same nine-node path | `2:8` | Only 1,2,3,8 burn by round 2; five values remain the unburned marker. A successful job does **not** imply full coverage. [Saved output](../results/graph-burning-path-9/burn-rounds-2-8.txt). |
| [Seven-node star](../datasets/graph-burning-star-7/graph.txt), centre 1 with six leaves | `1:2` | Centre 1 burns in round 1; leaves 2–7 burn in round 2. [Saved output](../results/graph-burning-star-7/burn-rounds-1-2.txt). |
| [Two disconnected three-node paths](../datasets/graph-burning-disconnected-6/graph.txt), `1--2--3` and `4--5--6` | `2:4`, then `2:5:4` | First test leaves 5 and 6 unburned after two rounds. Second burns all six by round 3. Fire cannot cross between components. [Two-round](../results/graph-burning-disconnected-6/burn-rounds-2-4.txt) / [three-round](../results/graph-burning-disconnected-6/burn-rounds-2-5-4.txt) outputs. |
| [Six-node cycle](../datasets/graph-burning-cycle-6/graph.txt) | `1:3:4` | Round 1: 1; round 2: 2,3,6; round 3: 4,5. Two rounds cannot cover all six here. [Saved output](../results/graph-burning-cycle-6/burn-rounds-1-3-4.txt). |
| [Thirty-node **undirected derivative**](../datasets/thirty-node-undirected-burning/) in three files | `1:18:3:8` | All 30 burn in four rounds: 1 in round 1, 5 in round 2, 13 in round 3, 11 in round 4. Every row agreed with the local Python prediction. [Saved output](../results/graph-burning-30-undirected/burn-rounds-1-18-3-8.txt). |

The 30-node burning dataset is **not** the original directed 30-node PageRank/BFS dataset. We added missing reverse edges and removed duplicate connections to make 55 undirected connections (110 adjacency entries). For *this graph*, three rounds cannot suffice: the largest radius-2 neighbourhood has 15 vertices, the largest radius-1 neighbourhood has 5, and the last source covers 1; even without overlap, `15+5+1=21<30`. Since `1:18:3:8` covers it in four, its burning number is exactly **4**. This is a graph-specific proof; the greedy algorithm is **not** guaranteed optimal in general.

An initial burning submission used `3,8,6` and failed before YARN because Giraph interprets commas inside `-ca` as separators between different settings. We changed both parser and run argument to **colon-separated** `3:8:6`, rebuilt, and the run succeeded. The Java simulator currently does **not** reject nonexistent, repeated, or already-burned source IDs; the Python checker does, so validate sequences there before interpreting them as legitimate source choices.

## 6. What each project code file is for

| File | Read it for this idea |
|---|---|
| [LearningOutDegreeComputation.java](../src/LearningOutDegreeComputation.java) | Simplest Giraph computation: read `getNumEdges()`, save count, halt. |
| [LearningInDegreeComputation.java](../src/LearningInDegreeComputation.java) | Two supersteps: outgoing-edge marker messages become incoming-edge counts at destinations. |
| [LearningBfsComputation.java](../src/LearningBfsComputation.java) | Configured source ID, infinity initialization, `Math.min` on candidate distances, one-hop messages, reactivation. |
| [LearningGraphBurningComputation.java](../src/LearningGraphBurningComputation.java) | Colon-separated source list, one scheduled source per round, next-round fire messages, first-burn value, final-round halt. |
| [LongDoubleFloatTextInputFormat.java](../src/LongDoubleFloatTextInputFormat.java) | How a text record becomes a Giraph vertex plus weighted outgoing edges. It is a learning copy of the reader already present in our Giraph build. |
| [find_small_graph_burning_sequence.py](../scripts/find_small_graph_burning_sequence.py) | **Local**, not distributed: parse and validate undirected input; BFS distances; calculate first-burn rounds for a supplied sequence; exact backtracking for at most 10 vertices with a search-state limit; greedy candidate choice for larger graphs. |
| [generate_graphviz_from_text.py](../scripts/generate_graphviz_from_text.py) | **Local visualization**: parse all text parts, reject duplicate/undefined vertices, run a local BFS solely to highlight one discovery tree, and write Graphviz DOT. It is not the source of the saved Giraph algorithm outputs. |
| [test_small_graph_burning_search.py](../tests/test_small_graph_burning_search.py) | Eleven Python regression tests for exact small-graph counts, greedy coverage, source validation, reverse-edge/duplicate checks, and search-limit behavior. |

In the burning Python code, `read_graph()` builds `{vertex: neighbours}` and checks both directions; `distances_from()` is BFS with a queue; `burn_rounds()` computes, for each vertex, the earliest `sourceRound + hopDistance` that fits in the requested number of rounds; `find_sequence()` tries all legal source orders for small inputs, starting with one round; `greedy_sequence()` chooses locally promising sources but does not exhaust all combinations. This division matters: **Python proposes/checks; the Giraph Java class simulates the chosen sequence across its graph input.** Neither current component is a general scalable exact solver.

The four operational shell scripts are [text-algorithm runner](../scripts/run_text_graph_algorithm.sh) (PageRank, degrees, BFS, weighted shortest path on text), [Graph Burning runner](../scripts/run_graph_burning.sh), [earlier JSON PageRank runner](../scripts/run_pagerank.sh), and [earlier JSON shortest-path runner](../scripts/run_shortest_path.sh). [Environment checker](../scripts/check_environment.sh) reports commands/services. The runners set Java/Hadoop paths, check that the JAR and HDFS input exist, reject an existing output directory, check YARN, select computation/input/output classes, and print results. Key flags: `-vif` input parser; `-vip` HDFS input path; `-vof` output formatter; `-op` new HDFS output path; `-w 1` one Giraph worker; `-ca` a configuration key/value; `-mc` and `-wc` PageRank master/worker context. [Commented teaching copies](../scripts/learning-guides/README.md) explain shell/Python syntax in English and Hinglish; use them to learn, not as separate experimental results.

## 7. Checks, limitations, and questions Sir may ask

**How do we know the three text files form one dataset?** Each vertex is defined exactly once, links can cross parts, one HDFS *directory* was supplied as input, and outputs contain all 30 IDs. The sum of out-degrees and in-degrees is `79`, matching the 79 directed edges. This is an input-splitting demonstration on one machine, not a multi-node scalability benchmark.

**Why JSON first and text later?** JSON matched the first working Giraph example; plain text is easier to read/edit/split. We did not simply rename a file: text needed the matching input-format class. Both formats still represent vertices plus outgoing edges.

**Why does BFS differ from shortest path?** BFS minimizes hops, weighted shortest path minimizes total weights. They match when all weights are 1; the six-node example proves they can differ.

**Is Graph Burning the same as BFS?** No. BFS begins at one fixed source and reports zero-based hops. Burning introduces a new source every round while old fires spread; its output is one-based first-burn round. There may be several sources, and source *order* matters.

**Did Giraph choose the best burning sources?** No. We supplied the sequence. The Python exact checker proved minimum rounds on the small tests when its exhaustive search completed; for 30 nodes a greedy heuristic proposed a sequence, and a separate counting lower bound plus Giraph coverage proved four is minimum **for that undirected graph**. Do not generalize the greedy method's optimality.

**What about ICM, LTM, SIR?** These are distinct diffusion models: ICM gives a newly activated vertex probabilistic attempts to activate neighbours; LTM activates when combined incoming influence reaches a threshold; SIR moves entities through susceptible, infected, recovered states. We have a [study note](../study-material/graph-burning-and-diffusion-models.md), but **no verified Giraph implementations** of these yet. Ask which one Sir wants next and what assumptions/parameters to use.

**What is still technically weak?** NodeManager has repeatedly stopped or left stale YARN registrations after runs. We recovered by checking active applications/processes and cleanly restarting YARN, but have not established a permanent root-cause fix. Also, no multi-machine performance study, no real large social-network benchmark, no distributed source-selection method, and no ICM/LTM/SIR results yet. The 30-node graph is larger than the toy examples, but still a teaching dataset.

## 8. What to open in front of Sir, in order

1. This brief and the [weekly timeline](WEEKLY-TIMELINE.md) for the journey from July. The [current week report](../weekly-reports/2026-09-24-week-10.md) records this week's actual work.
2. The [30-node text input README](../datasets/thirty-node-text/README.md) plus any two different `part-*.txt` files; explain one logical graph across files.
3. [30-node results](../results/thirty-node-text/README.md) and [BFS walkthrough](BFS-THIRTY-NODE-WALKTHROUGH.md); show degree sums and equal BFS/shortest values.
4. [Weighted comparison](../results/weighted-bfs-comparison/README.md); explain node 6's `2` hops versus `4` total cost.
5. [Graph Burning path input](../datasets/graph-burning-path-9/README.md), [path result](../results/graph-burning-path-9/README.md), and [first-burn explanation](../study-material/graph-burning-two-round-example.md).
6. [30-node undirected burning result](../results/graph-burning-30-undirected/README.md) beside the [source-selection reasoning](../study-material/graph-burning-source-selection-30.md); emphasize that it is a **different graph** from the directed one.
7. Show the four Java computation files and the Python checker, using the file table above. If asked about repeatability, show the run scripts and [tests](../tests/test_small_graph_burning_search.py).

Suggested closing: **“We can explain and reproduce the verified computations. Next we want your guidance on whether to prioritize distributed/automatic source selection, a larger real dataset, or one of the diffusion models. We also need to stabilize NodeManager before claiming any performance results.”** Record Sir's actual answer in the Week 10 report *after* the meeting; do not pre-fill it.

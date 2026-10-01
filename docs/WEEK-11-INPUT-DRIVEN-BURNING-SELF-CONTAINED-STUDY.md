# Week 11 team study sheet — Graph Burning sources inside the input

**Week:** 25 September–1 October 2026  
**Project:** Distributed graph algorithms for social-network problems using Apache Giraph  
**What is verified:** The new Java classes built on the lab PC, and two scheduled nine-vertex graphs ran through Giraph. The complete three-round run and the incomplete two-round run both matched our hand calculations.  
**What is not verified yet:** The separate hand-picked `1, 9, 5` schedule has input files and a prediction, but has **not** run on Giraph.

This sheet is meant to be read from top to bottom before explaining this week's work to Sir. It includes the actual data, code ideas, commands, results, errors and remaining question in one place. The paths in backticks identify files; no other study page is required to understand the experiment.

## 1. What question did we work on?

Earlier, our Graph Burning program received the new ignition sources as a command-line sequence such as `3:8:6`. Sir asked whether the graph file itself could say which vertex should ignite in which round. He also wanted a readable output: burned (`B`) or not burned (`NB`), and the **first round** in which each vertex burned. A vertex left unburned after the planned rounds should show `NB -1`.

We made a new version rather than replacing the older working version. The new program reads the source schedule from every vertex's text-input line. We kept the same rule as our earlier lab work: **one new source in each round**, and fire spreads across **one edge per round**. We did not try to optimize the source sequence this week.

## 2. Basic words we must be able to explain

| Word | Meaning in our experiment |
|---|---|
| Graph | Vertices and connections between them. Here a vertex is numbered 1–9. |
| Edge | A connection. The line `3 1 2:1 4:1` contains edges from 3 to 2 and 4. We list reverse edges too, so this example behaves as an undirected path. |
| Source | A vertex we deliberately ignite in a chosen round, even if no fire reaches it from a neighbour. |
| Burn round | The first round in which a vertex catches fire, either as a chosen source or from a neighbour. It never changes after that. |
| Superstep | One Giraph computation cycle. Our Java code maps superstep 0 to human round 1, superstep 1 to round 2, and so on. |
| Message | Giraph's way for a burned vertex to tell a neighbour: “you can catch fire in the next round.” Messages sent in one superstep arrive in the next. |
| HDFS | Hadoop's file system, where the job reads the graph and writes its result. It is separate from normal files under `/home/mca2025`. |
| YARN | Hadoop's job/resource manager. The ResourceManager accepts the job; a NodeManager offers containers in which job tasks run. |
| JAR | Compiled Java package. Maven builds our edited classes into the shaded Giraph examples JAR; editing `.java` alone does not change an already-built JAR. |

The `:1` in each edge is an edge weight needed by this input format. **Ordinary Graph Burning here ignores that weight** and counts one hop per round; it is not weighted shortest path.

## 3. New input format and the full example graph

Each text line is:

```text
vertexId sourceRound neighbourId:weight neighbourId:weight ...
```

For example, `3 1 2:1 4:1` means “this is vertex 3; choose it as a new source in round 1; it connects to 2 and 4.” The second field `0` means **not manually selected**. A vertex with `0` can still burn through an edge. Input `0` and output `-1` have different meanings.

All our initial scheduled tests used the same undirected path:

```text
1 -- 2 -- 3 -- 4 -- 5 -- 6 -- 7 -- 8 -- 9
```

It was split into three files, each with three complete vertex records. Hadoop/Giraph reads the **directory** as one graph; the three parts are not three separate graphs.

The complete three-round test input was:

```text
# part-01.txt
1 0 2:1
2 0 1:1 3:1
3 1 2:1 4:1
# part-02.txt
4 0 3:1 5:1
5 0 4:1 6:1
6 3 5:1 7:1
# part-03.txt
7 0 6:1 8:1
8 2 7:1 9:1
9 0 8:1
```

The `# part...` labels above are for this explanation **only**; they are not in the real `.txt` files. Read the second column: vertex 3 is selected in round 1, vertex 8 in round 2, and vertex 6 in round 3. This is the same source order as the older `3:8:6` command, but now the IDs are stored **in the input files**, not passed to Giraph as a source-list argument.

## 4. Calculate the first test ourselves, without a script

| Round | New source | Fire arriving from earlier burned vertices | Newly burned this round |
|---:|---:|---|---|
| 1 | 3 | none | 3 |
| 2 | 8 | 3 reaches 2 and 4 | 2, 4, 8 |
| 3 | 6 | 2 reaches 1; 4 reaches 5; 8 reaches 7 and 9 | 1, 5, 6, 7, 9 |

All nine vertices are burned after round 3. A vertex keeps its **first** burn round: for example, vertex 4 is round 2 even though it remains burned in round 3. The actual Giraph output was:

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

This is the **measured lab result**, not just a Python prediction. It is saved as `results/graph-burning-path-9-scheduled/part-00000.txt`.

## 5. Second test: what if the planned rounds end before all vertices burn?

We made a separate three-file input directory with the **same edges**. Only the source-round column changed: vertex 2 has `1`, vertex 8 has `2`, and every other vertex has `0`. The full second input is:

```text
# part-01.txt
1 0 2:1
2 1 1:1 3:1
3 0 2:1 4:1
# part-02.txt
4 0 3:1 5:1
5 0 4:1 6:1
6 0 5:1 7:1
# part-03.txt
7 0 6:1 8:1
8 2 7:1 9:1
9 0 8:1
```

Again, the `# part...` labels are just separators in this page, not actual input lines. In round 1, only source 2 burns. In round 2, fire from 2 reaches 1 and 3 while source 8 ignites. There is **no round 3** in this schedule, so fire does not get an extra step from 3 or 8. The actual Giraph output was:

```text
1  B   2
2  B   1
3  B   2
4  NB -1
5  NB -1
6  NB -1
7  NB -1
8  B   2
9  NB -1
```

This is saved as `results/graph-burning-path-9-two-round-scheduled/part-00000.txt`. `NB -1` means **not reached within these two rounds**. It does not mean those vertices can never burn; a later round might reach some of them.

## 6. What code runs where?

```text
Three local .txt input parts
        ↓ upload with hdfs dfs -put
One HDFS input directory
        ↓ runner checks input and finds total rounds
Giraph Java input reader → Giraph Java computation (YARN job)
        ↓ raw numeric HDFS output
Output formatter
        ↓
Readable HDFS result: vertexId   B/NB   firstBurnRound/-1
```

The scripts are client-side helpers. The graph computation across Giraph tasks is Java. We should **not** tell Sir that Python is the distributed burning implementation.

### Java input reader — `src/BurningScheduleTextInputFormat.java`

- `TextVertexInputFormat<LongWritable, DoubleWritable, FloatWritable>` declares three types: a long integer vertex ID, a double vertex value, and float edge values. `LongWritable` etc. are Hadoop's serializable wrappers.
- `createVertexReader` creates the object that will read one text record at a time. `nextVertex()` advances to the next line; `getCurrentVertex()` converts that line into a Giraph `Vertex`.
- `line.split("\\s+")` splits a line at one or more spaces or tabs. Token 0 is the ID; token 1 is the selected source round; later tokens are `neighbour:weight` pairs.
- `EdgeFactory.create(...)` makes each outgoing edge. Because this is an undirected experiment, the matching reverse edge must also appear in the neighbour's record.
- `vertex.initialize(id, new DoubleWritable(-sourceRound), edges)` attaches the ID, initial state and edges. A round-3 selected source starts with value `-3`; an unselected vertex starts with `0`. **Negative does not mean already burned.** It stores a future appointment to ignite.
- The reader rejects a negative input round and malformed `neighbour:weight` text. The fuller preflight validator also checks duplicates, reverse edges and schedules before launching Giraph.

### Giraph computation — `src/LearningGraphBurningFromInputComputation.java`

- `BasicComputation<LongWritable, DoubleWritable, FloatWritable, DoubleWritable>` uses the same ID/value/edge types plus a double message type. Every vertex receives an iterable of messages sent by neighbours in the previous superstep.
- `TOTAL_ROUNDS` is a configuration number, such as 3. The runner derives it from the **largest source-round number in the input**. It is **not** a source-ID list.
- `currentRound = getSuperstep() + 1` changes Giraph's zero-based step to our one-based human round.
- `storedValue <= 0` means this vertex has not burned yet. A positive value already records its first burn round, so the program leaves it unchanged.
- The loop over messages chooses the earliest incoming burn round. `storedValue == -currentRound` also allows the vertex to ignite because its input file selected it for this round. If an incoming fire message and manual selection happen in the same round, the recorded round is still that one round.
- On first burn, `vertex.getValue().set(firstArrival)` stores a positive first-burn round. If another round remains, `sendMessage` asks each neighbour to burn in `currentRound + 1`. The message arrives in the **next** superstep, not instantly in the same round.
- We must not `voteToHalt()` early: a future selected source might receive no message but must still wake up for its own planned round. All vertices halt after `totalRounds`.

### Python helpers and what we can skip

| File | Used by the current runner? | Purpose |
|---|---|---|
| `scripts/find_small_graph_burning_sequence.py` | **No** | Earlier optional search/checker, including a greedy option. It can suggest a source order; we are **not using it** for this input-driven experiment. |
| `scripts/validate_burning_schedule.py` | **Yes** | Reads all input parts, rejects malformed/duplicate/missing data, enforces one source per round, checks reverse edges and checks a source was not already burned in an earlier round. It derives the maximum round for the runner. Its normal display also **predicts output for comparison** using BFS distances. It does **not choose** the source vertices. |
| `scripts/format_burning_output.py` | **Yes** | Reads Giraph's two-column raw numeric output. Positive integer → `B` and that round; zero/negative → `NB -1`. It checks for malformed numbers. It does not run the burning algorithm. |
| `scripts/run_graph_burning_from_input.sh` | **Yes** | Orchestrates checks, calls the validator, starts Giraph on YARN, then calls the formatter. It is Bash, not Python. |

It is honest to say: **our current convenient runner requires the validator and formatter Python files**, but it does **not** require the optional greedy/source-finding Python file. If we skip the validator and formatter, we can invoke the Java Giraph job manually by giving `totalRounds` ourselves, but the result will be raw numeric values, not the requested `B`/`NB` format. We should not say “we used no Python at all” when using the current runner.

For clarity, a **possible but not yet separately tested** no-Python invocation
on an already-uploaded three-round input would be:

```bash
hadoop jar "$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar" \
  org.apache.giraph.GiraphRunner \
  org.apache.giraph.examples.LearningGraphBurningFromInputComputation \
  -vif org.apache.giraph.examples.BurningScheduleTextInputFormat \
  -vip /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input \
  -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
  -op /user/mca2025/giraph_learning/manual_raw_output_NEW \
  -w 1 \
  -ca mapred.job.tracker=yarn \
  -ca LearningGraphBurningFromInput.totalRounds=3
```

`manual_raw_output_NEW` must not already exist in HDFS. This skips the
Python validation and friendly formatting, so a bad schedule may fail later
inside Giraph and the output will be **numeric**. Positive values are first
burn rounds; zero/nonpositive values mean unburned. The verified runs above
used the safer Bash runner, **not** this manual alternative.

### What the Bash runner does — `scripts/run_graph_burning_from_input.sh`

1. `set -euo pipefail` makes errors stop the script; in particular, a broken pipe in the HDFS-to-formatter chain should not be treated as success.
2. `JAVA_HOME`, `HADOOP_HOME`, `HADOOP_CONF_DIR`, and `PATH` point to the already-installed Java and Hadoop commands. They do **not** install Hadoop.
3. The script requires exactly two arguments: an HDFS **input path** and a **new** HDFS output path. It checks the shaded JAR, Python helpers, input existence, unused output names, and a running YARN node.
4. It reads every `.txt` part from HDFS into the validator. `--rounds-only` prints the highest legal ignition round (2 or 3 in our tests). This local preflight is suitable for our small teaching graphs, **not** evidence of large-scale distributed preprocessing.
5. `hadoop jar` runs `LearningGraphBurningFromInputComputation` with `BurningScheduleTextInputFormat`, one Giraph worker (`-w 1`), and the derived total-round configuration. There is no colon-separated source-list argument.
6. Giraph's `IdWithValueTextOutputFormat` first writes numeric state to an HDFS directory ending `.__giraph_raw`. The formatter then writes the readable `part-00000` into the requested output directory. The raw path stays available for debugging.

## 7. How we built and ran this on the lab PC

Our setup has two Linux accounts with different roles. **`hduser` starts and manages HDFS/YARN services**. **`mca2025` owns the edited Giraph source, builds the JAR, uploads its graph data and submits jobs**. Running `jps` as `mca2025` may not list daemons owned by `hduser`; that alone does not mean the daemons are down.

After a machine restart, `hduser` checked `jps`; when services were absent, the working start commands were:

```bash
start-dfs.sh
start-yarn.sh
jps
yarn node -list
```

We waited for YARN to register **one `RUNNING` NodeManager**, not just for a Java process to exist. Do not launch a second NodeManager merely because a job waits. The two new Java files were copied to:

```text
/home/mca2025/giraph/giraph-examples/src/main/java/org/apache/giraph/examples/
```

The runner, validator and formatter were copied together to `/home/mca2025/giraph/`. As `mca2025`, we rebuilt once after changing Java source:

```bash
cd "$HOME/giraph"
mvn clean -Phadoop_2 -DskipTests -Dgiraph.maven.duplicate.finder.skip=true package
jar tf "$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar" | grep -E 'BurningScheduleTextInputFormat.class|LearningGraphBurningFromInputComputation.class'
```

All five Maven reactor modules reported `SUCCESS` on 30 September, and both new `.class` names appeared in the shaded JAR. **A successful Maven build proves compilation/packaging, not that a YARN job ran correctly.** We then uploaded exactly the three graph `.txt` files—not their README—to a new HDFS directory:

```bash
hdfs dfs -mkdir -p /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input
hdfs dfs -put /path/to/local/part-*.txt /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input/
hdfs dfs -ls /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input
```

`/path/to/local/` is a placeholder: use the directory where the three transferred parts actually are. `-mkdir -p` creates the HDFS directory, `-put` copies local files to HDFS, and `-ls` verifies them. Existing HDFS files should not be overwritten accidentally. To run the complete three-round case:

```bash
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input \
  /user/mca2025/giraph_learning/graph_burning_path9_scheduled_output
```

For the two-round case we used **separate** HDFS paths ending `graph_burning_path9_two_round_scheduled_input` and `graph_burning_path9_two_round_scheduled_output`. Both actual results are copied above. The output paths must be new because Hadoop refuses an already-existing output directory. A new run with different input does **not** require Maven rebuilding if Java code has not changed.

## 8. Problems we faced and what they taught us

| What happened | Cause / what we did | Lesson |
|---|---|---|
| `localhost:9000` and `:8032` refused connections after reboot | HDFS and YARN had not been started. `hduser` started DFS and YARN, then checked `jps` and `yarn node -list`. | A built Giraph JAR cannot run without live Hadoop services. |
| YARN showed a node with 3 containers, but no NodeManager process or active application existed | This was a stale registration; starting another NodeManager made YARN display two node entries. We confirmed the actual processes, then stopped the old ResourceManager (PID 7711) and started a replacement. YARN then showed exactly one running node with zero containers. | A YARN node-list line alone does not prove that particular NodeManager process is alive. Check processes and active jobs before restarting services. Never restart YARN blindly while work is active. |
| The transferred runner said `Permission denied` when invoked as a program | The shell file did not have the executable bit. `bash "$HOME/giraph/run_graph_burning_from_input.sh" INPUT OUTPUT` ran it successfully. | This is a file-permission problem, not a Java compilation problem. |
| Some pasted commands began with an invisible `` character | The shell interpreted it as part of the command name (`yarn`, `cd`). Typing the command cleanly worked. | Before installing anything because a command is “not found,” check for a stray pasted character. |

We did **not** delete the older results to make these experiments work. Each dataset and result has its own directory so the evidence remains comparable.

## 9. Did we use a “perfect” or greedy source choice?

Not for the two new Giraph runs. The complete `3, 8, 6` case reused a previously studied source sequence to confirm the **new input mechanism** against known results. The incomplete `2, 8` case deliberately stopped after two rounds to verify `NB -1`. Neither run measures how good a source-selection algorithm is. Our optional `find_small_graph_burning_sequence.py` can search for choices, but the input-driven runner **never calls it**.

For the next direct experiment, we wrote another nine-vertex input with **hand-picked non-optimized** sources `1, 9, 5` for rounds 1–3. That choice was made by us, not by Python. Our hand calculation predicts:

```text
1 B 1    2 B 2    3 B 3
4 NB -1  5 B 3    6 NB -1
7 NB -1  8 B 3    9 B 2
```

The input is in `datasets/graph-burning-path-9-hand-picked/`. A local input check agreed with the calculation, but **the Giraph job has not yet run** because of the network interruption. Do not present those rows as an actual cluster result. “Hand-picked” is also more accurate than “random”: we did not use a random-number generator or prove any probability claim. Arbitrary choices need not burn every vertex within the same number of rounds.

## 10. Short explanation we can give Sir

> We moved the Graph Burning source schedule from a command-line list into the second column of each vertex's text record. Our new Java input reader stores a selected round with the vertex, and our Giraph computation ignites that vertex in the matching superstep while fire messages spread one edge per round. The output distinguishes `B` with the first burn round from `NB -1` when the planned rounds end before a vertex is reached. We tested a three-round nine-node path where all vertices burned and a two-round version where five did not; both Giraph results matched our hand calculations. Python was used for input checking, prediction for comparison, and readable output formatting—not to choose optimal sources in these runs. Next we want to run a deliberately non-optimized hand-picked schedule, then discuss whether automatic source selection or a larger dataset is the better next step.

## 11. What remains before we claim more

- Run the hand-picked `1, 9, 5` input through Giraph when network access is stable; save its **actual** HDFS output and compare it with the prediction above.
- Follow Sir's current direction to experiment without an optimizer first.
  At the next meeting, clarify which extension he wants after the simple
  runs: explicit random selection, larger graphs, or another burning rule.
- The current preflight reads the whole input on one client. Our nine-vertex example proves correctness of the mechanism, **not** scalability on a large distributed dataset.
- The current rule permits one new source per round. A model with several sources in round 1, a different spread rule, or an automatic random selector would require an explicit definition and new tests.

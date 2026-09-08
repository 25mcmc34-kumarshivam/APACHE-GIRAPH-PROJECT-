# Beginner Learning Guide: Hadoop, Giraph, and Graph Algorithms

This guide explains what the lab is doing, why each component is needed, and what to study next. It is written for a learner who has completed commands but is still building the ideas behind them.

## 1. The purpose of this project

A normal program usually reads data on one computer, calculates an answer, and exits. A very large social or web graph may contain millions or billions of people, pages, and relationships. It may not fit comfortably in the memory of one process. Hadoop supplies distributed storage and resource management. Giraph supplies a way to divide a graph into partitions and calculate on its vertices in parallel.

Our present installation is a single-node learning cluster. It does not provide real multi-machine speed, but it exposes the same important components and programming model. Tiny graphs let us calculate the expected answer manually before trusting the software.

## 2. The complete path of one Giraph experiment

1. A graph is written as vertices and directed edges.
2. The local dataset is uploaded to HDFS.
3. `hadoop jar` starts `GiraphRunner`.
4. Giraph reads the graph through a vertex input format.
5. YARN allocates containers and starts Giraph tasks.
6. Vertices calculate and exchange messages in supersteps.
7. Giraph writes final vertex values to a new HDFS output directory.
8. We compare the output with a manual calculation.

If a job remains `ACCEPTED`, the graph algorithm has not started; YARN is still waiting for resources. If a job is `RUNNING`, containers are executing. `FINISHED` with `SUCCEEDED` means the computation completed.

## 3. Linux knowledge required

### Local paths and HDFS paths

`/home/mca2025/giraph/datasets/file.json` is a local Linux path. `/user/mca2025/giraph_learning/input/file.json` is an HDFS path. They can have similar names but belong to different filesystems.

```bash
cat file.json
hdfs dfs -cat /user/mca2025/input/file.json
```

The first command reads the local disk. The second asks the HDFS NameNode and DataNode for a distributed file.

### Users and ownership

`hduser` operates Hadoop because Hadoop directories and processes belong to that account. `mca2025` develops Giraph and submits jobs. Running services under different accounts without planning causes permission and log ownership errors.

### Essential commands to understand

| Command | Meaning | Why it is used here |
|---|---|---|
| `pwd` | print working directory | confirms the current location |
| `ls -lh` | list files with readable sizes | verifies datasets and JARs |
| `cd` | change directory | moves into the Giraph source tree |
| `cp` | copy | makes backups or copies source files |
| `chmod +x` | add execute permission | makes a shell script runnable |
| `ps -ef` | list processes | checks the real NodeManager process |
| `grep` | filter matching text | finds errors or classes |
| `tail` | show the end of a file | reads recent log messages |
| `echo $?` | show previous exit status | `0` means success; nonzero means failure |

Without these basics, it is difficult to distinguish a missing file, wrong account, stopped process, or failed command.

## 4. Java knowledge required

Giraph is written in Java. Java source (`.java`) is compiled into bytecode (`.class`), and related classes and resources are packaged in a JAR.

Study these concepts in order:

- variables, primitive types, conditions, and loops;
- classes, objects, methods, and constructors;
- inheritance and method overriding;
- interfaces and packages;
- collections and `Iterable`;
- generics such as `Vertex<LongWritable, DoubleWritable, FloatWritable>`;
- exceptions, especially `IOException`;
- Maven dependencies, modules, profiles, and build lifecycle;
- JAR content and Java classpaths.

### Reading a Giraph generic declaration

```java
BasicComputation<LongWritable, DoubleWritable,
                 FloatWritable, DoubleWritable>
```

In our algorithms these types mean:

1. `LongWritable`: vertex ID, for example vertex `3`.
2. `DoubleWritable`: value stored at the vertex, for example PageRank or distance.
3. `FloatWritable`: value stored on an edge, for example weight `1`.
4. `DoubleWritable`: type of message exchanged between vertices.

Hadoop uses `Writable` classes because values must be serialized when stored or transferred.

## 5. Hadoop in plain language

### HDFS

HDFS stores files as blocks. The NameNode maintains namespace and block-location metadata. DataNodes store the actual blocks. Our one-node lab uses replication factor `1` because only one DataNode exists.

Important commands:

```bash
hdfs dfs -mkdir -p /path
hdfs dfs -put local-file /path/
hdfs dfs -ls -R /path
hdfs dfs -cat /path/file
hdfs dfsadmin -report
```

`-mkdir -p` creates missing parent directories. `-put` uploads. `-ls` lists. `-cat` displays. `dfsadmin -report` checks DataNode capacity and health.

### YARN

YARN controls compute resources:

- ResourceManager decides how cluster resources are allocated.
- NodeManager runs on a worker machine and manages containers.
- ApplicationMaster coordinates one submitted application.
- A container is an allocated amount of memory and CPU in which a task runs.

This explains why a live HDFS does not prove Giraph can run: storage may work while NodeManager is stopped.

## 6. Graph theory foundations

A graph is written as `G = (V, E)`:

- `V` is the set of vertices.
- `E` is the set of edges.

For the five-node graph:

```text
V = {1, 2, 3, 4, 5}
E = {1→2, 2→3, 3→2, 3→4, 4→3, 5→3}
```

The graph is directed because `1→2` does not automatically create `2→1`. It is weighted because every stored edge has a numeric value, although all weights in this example are `1`.

### Adjacency list input

```json
[3,0,[[2,1],[4,1]]]
```

This says:

- vertex ID is `3`;
- its initial value is `0`;
- it has an edge to `2` with weight `1`;
- it has an edge to `4` with weight `1`.

## 7. The Giraph/Pregel model

Giraph uses vertex-centric computation. Instead of writing one global loop over the whole graph, we describe what one vertex does.

Execution proceeds through synchronized supersteps:

1. Every active vertex receives messages sent during the previous superstep.
2. It reads its current value and outgoing edges.
3. It may update its value.
4. It may send messages to other vertices.
5. It may call `voteToHalt()`.
6. A barrier waits until all workers finish the superstep.

A halted vertex can become active again if a message arrives. The job ends when every vertex is inactive and no messages remain.

## 8. Degree calculations

### Out-degree

Out-degree is the number of edges leaving a vertex:

```java
vertex.getNumEdges()
```

For the example graph:

| Vertex | Outgoing neighbors | Out-degree |
|---:|---|---:|
| 1 | 2 | 1 |
| 2 | 3 | 1 |
| 3 | 2, 4 | 2 |
| 4 | 3 | 1 |
| 5 | 3 | 1 |

No messages are needed because each vertex already owns its outgoing-edge list.

### In-degree

In-degree is the number of edges entering a vertex. A vertex does not automatically own a list of incoming edges, so the computation uses messages:

- Superstep 0: each vertex sends `1` along every outgoing edge.
- Superstep 1: each vertex counts the messages received.

| Vertex | Incoming neighbors | In-degree |
|---:|---|---:|
| 1 | none | 0 |
| 2 | 1, 3 | 2 |
| 3 | 2, 4, 5 | 3 |
| 4 | 3 | 1 |
| 5 | none | 0 |

This is the first clear example of why message passing is useful.

## 9. Shortest paths

Single-source shortest path finds the lowest total edge weight from one source to every reachable vertex.

The source starts at distance `0`; all other vertices start at infinity. When a vertex learns a smaller distance, it stores that value and sends `distance + edge weight` to its neighbors. Repeated supersteps propagate improvements until no shorter value is found.

From source `1`:

| Vertex | Best path | Distance |
|---:|---|---:|
| 1 | source | 0 |
| 2 | 1→2 | 1 |
| 3 | 1→2→3 | 2 |
| 4 | 1→2→3→4 | 3 |
| 5 | no directed path | infinity |

The output `1.7976931348623157E308` is Java `Double.MAX_VALUE`, used here to represent infinity/unreachable.

## 10. PageRank

PageRank estimates importance from incoming links. A link from an important vertex contributes more than a link from an unimportant vertex. A vertex divides its contribution across its outgoing edges.

A common form is:

```text
PR(v) = (1 - d) / N + d × Σ(PR(u) / outDegree(u))
```

where:

- `v` is the vertex being updated;
- `u` ranges over vertices linking to `v`;
- `N` is the number of vertices;
- `d` is a damping factor, commonly `0.85`.

PageRank is iterative: initial ranks are assigned, contributions are exchanged, and ranks are updated over several supersteps. Exact numbers depend on the implementation's initialization and stopping rules.

Verified ordering for our graph:

```text
3 > 2 > 4 > 1 = 5
```

Vertex `3` ranks highest because it receives links from `2`, `4`, and `5`, and the scores keep influencing each other through the graph.

Degree and PageRank answer different questions. In-degree counts incoming links equally; PageRank also considers the importance and out-degree of the linking vertices.

## 11. How to read a job command

```text
hadoop jar JAR GiraphRunner Computation \
  -vif InputFormat -vip INPUT \
  -vof OutputFormat -op OUTPUT -w 1
```

- `hadoop jar` launches a Java program using Hadoop's classpath.
- `JAR` contains Giraph and the computation class.
- `GiraphRunner` parses Giraph command-line options.
- `Computation` is the algorithm executed by each vertex.
- `-vif` tells Giraph how to decode input records.
- `-vip` is the HDFS vertex input path.
- `-vof` defines output serialization.
- `-op` is a new HDFS output directory.
- `-w 1` requests one Giraph worker in this single-node lab.
- `-ca key=value` supplies a custom configuration value.

The backslash continues one shell command onto the next line. It must be the final character on the line.

## 12. Practical learning sequence

### Week 1: Linux and terminal

- [ ] Navigate using `pwd`, `ls`, and `cd` without copying commands.
- [ ] Explain absolute and relative paths.
- [ ] Create, copy, move, and inspect small files.
- [ ] Explain users, groups, and permissions.
- [ ] Find a process and read the end of a log.

### Week 2: Java essentials

- [ ] Write a class with fields and methods.
- [ ] Use loops and `Iterable`.
- [ ] Explain inheritance and `@Override`.
- [ ] Read a four-type Giraph generic declaration.
- [ ] Compile a small program and inspect a JAR.

### Week 3: Graph theory

- [ ] Draw directed and undirected graphs.
- [ ] Build adjacency lists.
- [ ] Calculate in-degree and out-degree manually.
- [ ] Trace breadth-first search and weighted shortest paths.
- [ ] Perform two PageRank iterations with a calculator.

### Week 4: Hadoop

- [ ] Explain local filesystem versus HDFS.
- [ ] Explain every daemon shown by `jps`.
- [ ] Upload, list, read, and deliberately remove a test HDFS file.
- [ ] Explain YARN states `ACCEPTED`, `RUNNING`, and `FINISHED`.
- [ ] Locate an application ID and its container logs.

### Week 5: Giraph

- [ ] Explain vertex value, edge value, and message value.
- [ ] Trace supersteps on a three-vertex graph.
- [ ] Modify the source vertex for shortest path.
- [ ] Run the same algorithm on two datasets.
- [ ] Compare manual and Giraph results.

### Later project work

- [ ] Connected components
- [ ] Triangle counting
- [ ] Community detection concepts
- [ ] Dataset cleaning and conversion
- [ ] Correctness tests on tiny graphs
- [ ] Runtime and scalability experiments
- [ ] Tables and plots for the final report

## 13. Exercises

1. Add edge `5→1`. Recalculate all in-degrees and out-degrees before running Giraph.
2. Remove edge `3→2`. Predict how the PageRank ordering may change.
3. Change edge `1→2` weight to `4`. Calculate shortest paths from `1`.
4. Make every relationship bidirectional. Compare in-degree and out-degree.
5. Explain why vertex `5` is unreachable from vertex `1` in the original graph.
6. Write down the messages sent during the first two in-degree supersteps.
7. Create a six-vertex graph with one isolated vertex and predict every algorithm's treatment of it.

## 14. Reliable references

- Apache Hadoop 2.7.7 documentation: https://hadoop.apache.org/docs/r2.7.7/
- Hadoop single-node setup: https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/SingleCluster.html
- HDFS architecture: https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html
- YARN architecture: https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-site/YARN.html
- Oracle Java 8 learning trail: https://docs.oracle.com/javase/tutorial/java/
- Java generics: https://docs.oracle.com/javase/tutorial/java/generics/
- Apache Giraph website: https://giraph.apache.org/
- Original Pregel paper: https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/

Read the version-matched Hadoop documentation first. Newer Hadoop instructions may use different commands, defaults, Java versions, and configuration properties.

## 15. Learning record template

For every session, record:

```text
Date:
Goal:
Concept learned:
Commands used:
Expected result:
Actual result:
Error faced:
Cause:
Fix:
What I can now explain without copying:
Next experiment:
```

The most important progress is not the number of commands completed. It is being able to predict what a command will do, recognize which component failed, and explain why the output is correct.

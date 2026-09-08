# Complete Study Roadmap: From Computer Basics to Apache Giraph

This is the recommended order of study for this project. Do not try to learn every subject at the same time. Complete the exercises and checkpoint at the end of one phase before moving to the next.

Suggested pace: **24 weeks, 7–10 hours per week**. A faster learner may shorten it, but understanding is more important than finishing videos.

## How to use this roadmap

For each topic:

1. Read the short introduction.
2. Watch one course or playlist, not five different courses.
3. Type the examples yourself.
4. Explain the idea in your own notebook without looking at the source.
5. Complete the practical checkpoint.
6. Mark the checkbox only when you can repeat the task without copying.

Use Wikipedia to understand vocabulary and connections. Use official documentation for exact commands and APIs. Use books for deeper understanding. Videos are the starting explanation, not the final authority.

## Three useful YouTube channels

These three channels cover most of the foundations needed here:

1. [Neso Academy](https://www.youtube.com/@nesoacademy) — computer science foundations, operating systems, networks, Java, data structures, and algorithms.
2. [freeCodeCamp.org](https://www.youtube.com/@freecodecamp) — long beginner courses on Linux, Java, Git, data structures, distributed systems, and data engineering.
3. [Gate Smashers](https://www.youtube.com/@GateSmashers) — accessible explanations of operating systems, computer networks, DBMS, big data, Hadoop, and algorithms, particularly useful for Indian university courses.

Also useful for university-level lectures: [NPTEL](https://www.youtube.com/@nptelhrd).

Do not follow a video command blindly when its Hadoop, Java, or Ubuntu version differs from this project. Use this repository's installation guide for the verified versions.

---

# Phase 0 — Computer and Terminal Confidence

**Time:** 1–2 weeks  
**Goal:** Use the terminal without fear and understand where commands operate.

## Topics

- [ ] Hardware: CPU, cores, RAM, disk, network interface
- [ ] Operating system, kernel, process, service, user, and group
- [ ] Linux filesystem hierarchy: `/`, `/home`, `/usr`, `/tmp`, `/var`
- [ ] Absolute and relative paths
- [ ] Files, directories, hidden files, extensions
- [ ] Terminal, shell, Bash, prompt, command, argument, and option
- [ ] Standard input, standard output, and standard error
- [ ] Pipes (`|`) and redirection (`>`, `>>`, `2>`)
- [ ] Exit codes and `echo $?`
- [ ] Permissions: read, write, execute; `chmod`, `chown`
- [ ] Processes: PID, foreground, background, signals, `ps`, `jps`
- [ ] Environment variables: `PATH`, `JAVA_HOME`, `HADOOP_HOME`
- [ ] Text tools: `cat`, `less`, `head`, `tail`, `grep`, `sed`
- [ ] SSH basics and public/private keys

## Learn from

- Website: [Linux Journey](https://linuxjourney.com/)
- Website: [The Linux Command Line](https://linuxcommand.org/tlcl.php)
- Documentation: [Ubuntu Server documentation](https://documentation.ubuntu.com/server/)
- Wikipedia: [Linux](https://en.wikipedia.org/wiki/Linux)
- Wikipedia: [Unix shell](https://en.wikipedia.org/wiki/Unix_shell)
- Wikipedia: [Secure Shell](https://en.wikipedia.org/wiki/Secure_Shell)
- Book: **The Linux Command Line** — William Shotts (legally available from the author's website)
- Book: **How Linux Works** — Brian Ward
- YouTube: search Neso Academy or freeCodeCamp for “Linux command line full course”.

## Practical checkpoint

- [ ] Create `practice/week1/input` without copying a command.
- [ ] Write five lines to a file and filter one word with `grep`.
- [ ] Explain the difference between `/home/mca2025/giraph` and an HDFS path.
- [ ] Find the Java process ID for NodeManager.
- [ ] Explain why a private SSH key must never go to GitHub.

---

# Phase 1 — Programming Logic and Java

**Time:** 3–4 weeks  
**Goal:** Read and modify Giraph computation classes.

## Topics

- [ ] Algorithm, pseudocode, variable, data type, operator
- [ ] Conditions, loops, methods, parameters, and return values
- [ ] Arrays, lists, maps, sets, and iterators
- [ ] Class, object, field, constructor, and method
- [ ] Encapsulation, inheritance, interfaces, and polymorphism
- [ ] Packages, imports, and access modifiers
- [ ] `extends`, `implements`, and `@Override`
- [ ] Exceptions and `IOException`
- [ ] Java generics and type parameters
- [ ] Java I/O and serialization
- [ ] JDK, JRE, JVM, bytecode, compiler, and classpath
- [ ] `Writable`, `LongWritable`, `DoubleWritable`, `FloatWritable`
- [ ] JAR files and `jar tf`
- [ ] Maven: `pom.xml`, dependencies, plugins, profiles, phases
- [ ] Dependency conflicts and why Guava caused our failure

## Learn from

- Official tutorial: [Oracle Java Tutorials](https://docs.oracle.com/javase/tutorial/)
- Official topic: [Classes and Objects](https://docs.oracle.com/javase/tutorial/java/javaOO/)
- Official topic: [Generics](https://docs.oracle.com/javase/tutorial/java/generics/)
- Official topic: [Collections](https://docs.oracle.com/javase/tutorial/collections/)
- Maven guide: [Maven Getting Started](https://maven.apache.org/guides/getting-started/)
- Wikipedia: [Java](https://en.wikipedia.org/wiki/Java_(programming_language))
- Wikipedia: [Java virtual machine](https://en.wikipedia.org/wiki/Java_virtual_machine)
- Book: **Head First Java** — Kathy Sierra, Bert Bates, and Trisha Gee
- Book: **Java: A Beginner's Guide** — Herbert Schildt
- Later reference: **Effective Java** — Joshua Bloch
- YouTube: Neso Academy Java playlist or freeCodeCamp Java full course.

## Practical checkpoint

- [ ] Write a Java class that stores a vertex ID and value.
- [ ] Loop through a list of neighbors and count them.
- [ ] Explain all four types in `BasicComputation<LongWritable, DoubleWritable, FloatWritable, DoubleWritable>`.
- [ ] Build a small Maven project.
- [ ] Explain the difference between source code, `.class`, and `.jar`.

---

# Phase 2 — Data, Datasets, and Big Data

**Time:** 1–2 weeks  
**Goal:** Understand what data is and why distributed tools exist.

## Topics

- [ ] Data, information, record, field, schema, and metadata
- [ ] Structured, semi-structured, and unstructured data
- [ ] CSV, TSV, JSON, XML, Parquet, and Avro
- [ ] Dataset, training dataset, graph dataset, and benchmark dataset
- [ ] Data quality: missing values, duplicates, invalid IDs, bad edges
- [ ] Data cleaning, transformation, validation, and provenance
- [ ] Big data: volume, velocity, variety, veracity, and value
- [ ] Batch processing versus stream processing
- [ ] Data pipeline, ETL, and ELT
- [ ] Scalability: scale up versus scale out
- [ ] Partitioning, replication, locality, and fault tolerance
- [ ] Privacy, consent, anonymization, and dataset licensing

## Learn from

- Wikipedia: [Data set](https://en.wikipedia.org/wiki/Data_set)
- Wikipedia: [Big data](https://en.wikipedia.org/wiki/Big_data)
- Wikipedia: [Data cleansing](https://en.wikipedia.org/wiki/Data_cleansing)
- Website: [Google Dataset Search](https://datasetsearch.research.google.com/)
- Website: [Stanford Large Network Dataset Collection (SNAP)](https://snap.stanford.edu/data/)
- Website: [KONECT Network Datasets](https://konect.cc/networks/)
- Book: **Data Science from Scratch** — Joel Grus
- Book: **Fundamentals of Data Engineering** — Joe Reis and Matt Housley
- YouTube: freeCodeCamp data engineering courses.

## Practical checkpoint

- [ ] Explain why our Giraph JSON is semi-structured data.
- [ ] Validate that every edge target exists as a vertex.
- [ ] Identify self-loops, duplicates, and isolated vertices.
- [ ] Write a short dataset card: source, meaning, size, license, cleaning, and limitations.

---

# Phase 3 — Data Structures, Algorithms, and Graph Theory

**Time:** 3–4 weeks  
**Goal:** Calculate graph answers manually before using Giraph.

## Topics

- [ ] Time and space complexity; Big-O notation
- [ ] Arrays, linked lists, stacks, queues, hash tables, trees
- [ ] Graph, vertex/node, edge/link, order, and size
- [ ] Directed, undirected, weighted, unweighted, simple, and multigraph
- [ ] Self-loop, parallel edge, neighbor, adjacency
- [ ] Adjacency list and adjacency matrix
- [ ] Walk, trail, path, cycle, reachability, connectivity
- [ ] In-degree, out-degree, and total degree
- [ ] Breadth-first search (BFS) and depth-first search (DFS)
- [ ] Unweighted shortest path and Dijkstra's algorithm
- [ ] Connected and strongly connected components
- [ ] Centrality: degree, closeness, betweenness, eigenvector
- [ ] PageRank and damping factor
- [ ] Triangle counting and clustering coefficient
- [ ] Community detection fundamentals
- [ ] Bipartite, social, web, citation, road, and knowledge graphs

## Learn from

- Interactive textbook: [Open Data Structures](https://opendatastructures.org/)
- Course: [Princeton Algorithms](https://algs4.cs.princeton.edu/home/)
- Visualizer: [VisuAlgo](https://visualgo.net/en)
- Wikipedia: [Graph theory](https://en.wikipedia.org/wiki/Graph_theory)
- Wikipedia: [Graph data structure](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))
- Wikipedia: [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
- Wikipedia: [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- Wikipedia: [PageRank](https://en.wikipedia.org/wiki/PageRank)
- Book: **Grokking Algorithms** — Aditya Bhargava
- Book: **Algorithms, 4th Edition** — Robert Sedgewick and Kevin Wayne
- Book: **Networks, Crowds, and Markets** — David Easley and Jon Kleinberg (free official PDF is available from Cornell)
- YouTube: Neso Academy data structures/algorithms; Gate Smashers graph algorithms.

## Practical checkpoint

- [ ] Convert a drawn graph into an adjacency list and JSON input.
- [ ] Calculate all in-degrees and out-degrees manually.
- [ ] Trace BFS one queue operation at a time.
- [ ] Calculate shortest paths from two sources.
- [ ] Perform at least two PageRank iterations with a calculator.
- [ ] Explain why degree and PageRank are not the same measurement.

---

# Phase 4 — Operating Systems, Networking, and Git

**Time:** 2 weeks  
**Goal:** Understand the environment in which distributed processes communicate.

## Topics

- [ ] Program versus process versus thread
- [ ] Concurrency versus parallelism
- [ ] CPU scheduling, memory, virtual memory, and filesystems
- [ ] Hostname, IP address, port, localhost, DNS
- [ ] TCP, client/server, socket, timeout, and firewall
- [ ] HTTP and web user interfaces
- [ ] SSH remote login and authentication
- [ ] Git repository, working tree, staging area, commit
- [ ] Branch, remote, clone, pull, push, merge, and conflict
- [ ] `.gitignore`, README, license, and reproducibility

## Learn from

- Wikipedia: [Process](https://en.wikipedia.org/wiki/Process_(computing))
- Wikipedia: [Thread](https://en.wikipedia.org/wiki/Thread_(computing))
- Wikipedia: [Parallel computing](https://en.wikipedia.org/wiki/Parallel_computing)
- Free book: [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- Free book: [Pro Git](https://git-scm.com/book/en/v2)
- Interactive Git: [Learn Git Branching](https://learngitbranching.js.org/)
- GitHub: [GitHub Skills](https://skills.github.com/)
- YouTube: Neso Academy OS/networking; freeCodeCamp Git course.

## Practical checkpoint

- [ ] Explain why NodeManager is a process and a YARN container is a managed execution allocation.
- [ ] Identify the ResourceManager and NodeManager ports.
- [ ] Make a branch, edit a file, commit, merge, and push.
- [ ] Recover an earlier file version using Git without deleting the repository.

---

# Phase 5 — Distributed and Parallel Computing

**Time:** 2–3 weeks  
**Goal:** Understand why multiple machines change program design.

## Topics

- [ ] Distributed system and distributed computation
- [ ] Parallel computing and multicore computing
- [ ] Concurrency versus parallelism versus distribution
- [ ] Shared memory versus message passing
- [ ] Cluster, node, worker, coordinator, task, and job
- [ ] Network latency, bandwidth, serialization, and communication cost
- [ ] Partitioning and load balancing
- [ ] Replication and availability
- [ ] Failure detection, retry, checkpoint, and recovery
- [ ] Consistency and partial failure
- [ ] Horizontal and vertical scaling
- [ ] Data locality
- [ ] MapReduce model
- [ ] Bulk Synchronous Parallel (BSP)
- [ ] Pregel's vertex-centric model
- [ ] Speedup, efficiency, bottleneck, and Amdahl's law

## The essential distinction

- **Concurrency:** multiple tasks make progress during overlapping time.
- **Parallelism:** multiple tasks execute at the same instant using multiple processing units.
- **Distributed computing:** cooperating tasks run on networked machines with separate memory and possible independent failures.

A system can be concurrent without being parallel, parallel on one machine without being distributed, or both distributed and parallel.

## Learn from

- Wikipedia: [Distributed computing](https://en.wikipedia.org/wiki/Distributed_computing)
- Wikipedia: [Parallel computing](https://en.wikipedia.org/wiki/Parallel_computing)
- Wikipedia: [Bulk synchronous parallel](https://en.wikipedia.org/wiki/Bulk_synchronous_parallel)
- Paper: [Pregel: A System for Large-Scale Graph Processing](https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/)
- Free book: [Distributed Systems, 4th edition](https://www.distributed-systems.net/index.php/books/ds4/)
- Book: **Designing Data-Intensive Applications** — Martin Kleppmann
- Book: **Distributed Systems** — Maarten van Steen and Andrew S. Tanenbaum
- YouTube: NPTEL distributed systems lectures; freeCodeCamp distributed-systems courses.

## Practical checkpoint

- [ ] Draw one coordinator and three workers with messages between them.
- [ ] Explain what happens when one worker is slow.
- [ ] Explain why network messages are more expensive than local method calls.
- [ ] Partition a ten-vertex graph across two workers on paper.
- [ ] Explain Giraph's synchronization barrier.

---

# Phase 6 — Hadoop Ecosystem

**Time:** 3 weeks  
**Goal:** Operate the single-node cluster and understand every daemon.

## Topics

- [ ] Hadoop Common, HDFS, YARN, and MapReduce
- [ ] HDFS block, NameNode, DataNode, and SecondaryNameNode
- [ ] Namespace metadata versus file block data
- [ ] Replication factor and under-replication
- [ ] HDFS permissions and user directories
- [ ] ResourceManager, NodeManager, ApplicationMaster, and container
- [ ] YARN resource requests: memory and vcores
- [ ] Application states and diagnostics
- [ ] Map, shuffle, reduce, and input split
- [ ] Configuration files: `core-site.xml`, `hdfs-site.xml`, `mapred-site.xml`, `yarn-site.xml`
- [ ] Hadoop logs and YARN container logs
- [ ] Pseudo-distributed versus multi-node cluster
- [ ] Hive, HBase, Spark, and ZooKeeper at overview level

## Learn from

- Official: [Apache Hadoop 2.7.7 documentation](https://hadoop.apache.org/docs/r2.7.7/)
- Official: [Single-node setup](https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/SingleCluster.html)
- Official: [HDFS architecture](https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- Official: [YARN architecture](https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-site/YARN.html)
- Official: [HDFS commands](https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/FileSystemShell.html)
- Official: [YARN commands](https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-site/YarnCommands.html)
- Wikipedia: [Apache Hadoop](https://en.wikipedia.org/wiki/Apache_Hadoop)
- Wikipedia: [HDFS](https://en.wikipedia.org/wiki/Apache_Hadoop#Hadoop_distributed_file_system)
- Book: **Hadoop: The Definitive Guide** — Tom White
- Book: **Data-Intensive Text Processing with MapReduce** — Jimmy Lin and Chris Dyer (free official PDF)
- YouTube: Gate Smashers Hadoop/big-data material; freeCodeCamp Hadoop courses.

## Practical checkpoint

- [ ] Draw the complete HDFS and YARN architecture from memory.
- [ ] Explain every `jps` process.
- [ ] Upload and read a file from HDFS.
- [ ] Diagnose a job intentionally submitted while NodeManager is stopped.
- [ ] Locate an application ID and read its logs.
- [ ] Explain why repeated NameNode formatting is dangerous.

---

# Phase 7 — Apache Giraph

**Time:** 3 weeks  
**Goal:** Understand and implement vertex-centric graph algorithms.

## What Giraph is

Apache Giraph is an iterative graph-processing framework built on Hadoop. It was designed for large-scale vertex-centric computation and was inspired by Google's Pregel model. A graph is divided among workers. During each synchronized superstep, active vertices update their values and send messages that arrive in the next superstep.

Giraph was historically used for large social-graph analysis, including work at Facebook. The Apache project is now retired in the Apache Attic. It remains valuable in this project for learning Pregel, BSP, message passing, distributed graph algorithms, and reproducible research on an established codebase. For new production systems, also study maintained technologies such as Apache Spark GraphX and other modern graph platforms.

## Topics

- [ ] Giraph architecture and Hadoop integration
- [ ] Vertex-centric thinking
- [ ] Vertex ID, vertex value, edge value, and message value
- [ ] `BasicComputation` and `compute()`
- [ ] Supersteps and synchronization barriers
- [ ] `sendMessage()` and message delivery
- [ ] `voteToHalt()` and reactivation
- [ ] Master computation and worker context
- [ ] Aggregators and combiners
- [ ] Input formats and output formats
- [ ] Graph partitioning and worker count
- [ ] ZooKeeper coordination
- [ ] Checkpointing and fault recovery
- [ ] Out-of-core concepts
- [ ] Custom configuration with `-ca`
- [ ] Reading source, tests, Javadocs, and container logs
- [ ] Giraph dependency compatibility and shaded JARs

## Learn from

- Official introduction: [Introduction to Apache Giraph](https://giraph.apache.org/intro.html)
- Official examples API: [Giraph example classes](https://giraph.apache.org/apidocs/org/apache/giraph/examples/package-summary.html)
- Official source: [Apache Giraph on GitHub](https://github.com/apache/giraph)
- Project status: [Apache Attic — Giraph](https://attic.apache.org/projects/giraph.html)
- Wikipedia: [Apache Giraph](https://en.wikipedia.org/wiki/Apache_Giraph)
- Background paper: **Pregel: A System for Large-Scale Graph Processing** — Malewicz et al.
- Book: **Practical Graph Analytics with Apache Giraph** — Roman Shaposhnik and Claudio Martella
- Code study: `giraph-examples/src/main/java/org/apache/giraph/examples`

The official Giraph quick start is historically useful but uses older Hadoop and Java versions. Do not copy its installation commands over the verified repository guide.

## Practical checkpoint

- [ ] Explain one input JSON line field by field.
- [ ] Trace in-degree messaging through two supersteps.
- [ ] Explain why out-degree needs no messages.
- [ ] Run PageRank and shortest path from two sources.
- [ ] Change a computation and rebuild the shaded JAR.
- [ ] Explain the Guava `NoSuchMethodError` and relocation fix.
- [ ] Implement one new computation with a manually verified tiny graph.

---

# Phase 8 — Social Network Analysis and Research Skills

**Time:** 3–4 weeks, then continue throughout the project  
**Goal:** Turn technical experiments into a defensible academic project.

## Topics

- [ ] Social network, actor, relation, tie, and interaction
- [ ] Homophily, influence, diffusion, and information cascades
- [ ] Centrality and interpretation limitations
- [ ] Community structure and modularity
- [ ] Link prediction and recommendation basics
- [ ] Temporal and dynamic networks
- [ ] Sampling bias and missing edges
- [ ] Correlation versus causation
- [ ] Research question, hypothesis, baseline, and metric
- [ ] Literature search and related-work table
- [ ] Experimental design and reproducibility
- [ ] Dataset ethics, privacy, terms, and licensing
- [ ] Runtime, memory, communication, and scalability measurement
- [ ] Tables, plots, discussion, threats to validity, and conclusions

## Learn from

- Course/book: [Networks, Crowds, and Markets](https://www.cs.cornell.edu/home/kleinber/networks-book/)
- Book: **Social Network Analysis: Methods and Applications** — Wasserman and Faust
- Book: **Network Science** — Albert-László Barabási; [free online edition](http://networksciencebook.com/)
- Website: [Google Scholar](https://scholar.google.com/)
- Website: [Semantic Scholar](https://www.semanticscholar.org/)
- Website: [arXiv](https://arxiv.org/)
- Wikipedia: [Social network analysis](https://en.wikipedia.org/wiki/Social_network_analysis)
- Wikipedia: [Community structure](https://en.wikipedia.org/wiki/Community_structure)
- YouTube: NPTEL social network analysis or network-science lectures.

## Practical checkpoint

- [ ] Write one precise research question.
- [ ] Select a legally usable dataset and write its dataset card.
- [ ] Define expected outputs and evaluation metrics before running experiments.
- [ ] Keep code, configuration, dataset version, and results under version control.
- [ ] Compare tiny-graph results manually.
- [ ] Report failures and limitations, not only successful output.

---

# Phase 9 — Modern Context After Giraph

**Time:** later in the project  
**Goal:** Understand where the learned ideas appear today.

## Topics

- [ ] Apache Spark fundamentals and resilient distributed datasets
- [ ] Spark GraphX and Pregel-style API
- [ ] GraphFrames overview
- [ ] Apache Flink graph/dataflow concepts
- [ ] Graph databases versus graph-computation engines
- [ ] Neo4j and Cypher overview
- [ ] Distributed graph neural network overview
- [ ] Cloud-managed data processing concepts

## Learn from

- Official: [Apache Spark](https://spark.apache.org/docs/latest/)
- Official: [Spark GraphX](https://spark.apache.org/docs/latest/graphx-programming-guide.html)
- Official: [Neo4j documentation](https://neo4j.com/docs/)
- Wikipedia: [Graph database](https://en.wikipedia.org/wiki/Graph_database)
- Book: **Graph Algorithms** — Mark Needham and Amy E. Hodler

This phase should come after the Giraph experiments. Changing tools too early will hide the concepts we are trying to learn.

---

# Final progress checklist

## Foundation

- [ ] I can use Linux without copying every command.
- [ ] I can read basic Java and Maven files.
- [ ] I understand datasets and data-quality checks.
- [ ] I can calculate graph results manually.

## Systems

- [ ] I can distinguish concurrency, parallelism, and distribution.
- [ ] I can explain HDFS and YARN architecture.
- [ ] I can diagnose `ACCEPTED`, `RUNNING`, `FAILED`, and `SUCCEEDED` jobs.

## Giraph

- [ ] I understand vertices, messages, supersteps, and halting.
- [ ] I can run and explain degree, PageRank, and shortest path.
- [ ] I can modify, build, and test a computation.

## Research

- [ ] I can state the purpose and limitation of every metric.
- [ ] I can document a dataset and respect its license and privacy constraints.
- [ ] I can reproduce an experiment from Git and explain its output.
- [ ] I can compare Giraph with a maintained modern graph framework.

## Recommended study rule

Spend approximately **40% reading/watching, 50% practicing, and 10% writing your own notes**. If you cannot explain a command or result without looking at the guide, repeat the practical exercise before moving forward.

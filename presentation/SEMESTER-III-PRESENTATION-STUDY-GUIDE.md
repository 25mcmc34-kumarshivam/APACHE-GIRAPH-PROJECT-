# Semester III presentation study guide

This note is for Kumar and Archana. We should read it together before the evaluation. The slide deck is a short presentation; this file explains every slide in simple language, what each word means, what we actually did, and what we should say if the panel asks for details.

## Our one-minute project summary

Our project studies distributed graph algorithms for social-network type data using Apache Giraph. A graph contains vertices, which represent entities, and edges, which represent relationships. We first prepared a Hadoop and YARN environment, built Apache Giraph, and ran small verified examples. We then added Graph Burning experiments. For Graph Burning, a Python program calculates an expected answer from a supplied graph and source schedule. The Giraph program runs the same input through Hadoop/YARN. We compare both outputs line by line. The largest verified run in this semester used 348,087 vertices and 1,128,693 undirected connections. Both sides produced 348,087 rows, with 243,095 burned and 104,992 unburned vertices. The comparison exit code was 0, meaning the prediction and Giraph output matched exactly.

This is a verified foundation. It is not yet an optimized source-selection algorithm or a final multi-node performance study.

## Important correction about “distributed”

The software stack is distributed even though our lab currently uses one physical worker machine. HDFS stores the input as Hadoop files, YARN allocates containers, and Giraph divides vertex computation among mapper tasks. We used multiple `part-*.txt` files as one logical graph and submitted jobs through YARN. The current machine is a pseudo-distributed or single-node cluster, so it demonstrates the distributed execution model without giving us a true multi-machine speedup. True multi-node scaling is future work.

## Slide-by-slide explanation

### Slide 1: Title

The title states the project area and the framework. “Distributed graph algorithms” means algorithms whose graph work can be divided across workers. “Social network problems” is the application area. “Apache Giraph” is the Pregel-style graph-processing framework we used. This slide identifies our Group A presenters and supervisor. The QR code does not belong on the title slide because it distracts from the project identity. We keep it on the final references slide, where a panel member naturally looks for the repository.

### Slide 2: Problem definition

We explain why ordinary single-program processing becomes difficult when a graph has many vertices and edges. The project needs a repeatable way to load split graph files, execute vertex-centric algorithms, and check the answers. The problem is not only “write Java code”. It includes setup, data movement, execution, verification and explanation.

If asked what a vertex-centric algorithm means, say: each vertex stores its own value, reads messages from neighbouring vertices, updates its value, and may send messages for the next superstep.

### Slide 3: Aim and scope

The left side says what we planned: install and operate Giraph, understand supersteps, run baseline algorithms, and implement Graph Burning. The right side says what we reached: JSON and text input, multiple HDFS parts, an independent Python prediction, and a verified 348,087-vertex run.

“Scope reached” does not mean the whole one-year project is finished. It means this semester’s foundation works.

### Slide 4: Literature and existing work

Pregel is the graph-computation model behind the vertex-centric idea. Giraph is the framework we used to run that style of computation with Hadoop. HDFS is the distributed file system. YARN is the resource manager that starts containers for jobs. PageRank, degree, BFS and shortest paths gave us understandable baseline jobs before Graph Burning.

Graph Burning is our main experimental direction. A source sequence tells the program which vertex ignites in each round. Existing fire spreads according to the configured rule, and each vertex records its first burn round.

### Slide 5: Progress through the semester

This timeline is a short summary, not an empty future plan. We began with Linux and project basics. We then configured Java, Git, Maven, Hadoop, HDFS and YARN on the shared lab system, solved permission and environment problems, built Giraph, and ran baseline algorithms. After that we moved to input-driven Graph Burning, Python prediction, large graph conversion, and exact verification.

### Slide 6: System architecture

The flow is: local text files become HDFS input, YARN assigns resources, Giraph runs vertex-centric supersteps, and the output records burn status and the first burn round. `hduser` owns the Hadoop service processes. `mca2025` builds and submits the Giraph experiments. This separation was necessary because Hadoop service permissions were not available to an ordinary project account.

### Slide 7: Baseline graph algorithms

PageRank estimates importance using incoming contributions. Out-degree counts outgoing edges. In-degree counts incoming edges. BFS measures the minimum number of edges from a source. Weighted shortest path measures minimum total edge weight from a source. These jobs taught us how input formats, vertex values, messages, supersteps, HDFS output paths and YARN status work.

### Slide 8: Graph Burning model

The example source sequence is `3:8:6`. In round 1, vertex 3 is the scheduled source. In round 2, vertex 8 is scheduled and previously burning fire continues to spread. In round 3, vertex 6 is scheduled and the earlier fire continues. The result stores `B` with the first burn round or `NB -1` when the vertex remains unburned in the configured experiment.

The exact spread rule must remain aligned with the faculty-approved model. We should describe the implementation honestly as the current scheduled-round model and say that constrained burning sets and source optimization are the next research step.

### Slide 9: Input, prediction and verification pipeline

The same logical graph is read twice. Python reads the local scheduled parts and calculates the expected first-burn round. Giraph reads equivalent parts from HDFS and produces the actual output. We normalize and compare the two tabular outputs. This design catches both algorithm mistakes and input-format mistakes.

### Slide 10: Experiments completed

The table shows the progression from 30 nodes, to a 120-node grid, to 9,625 vertices from Web-Google, and finally to the 348,087-vertex experiment. The number of rounds is a configured input choice, not a claim that the graph has only that many possible distances. “Verified result” means the Python and Giraph result rows matched for that run.

### Slide 11: 348,087-vertex result

The bars show the final counts. Burned means Giraph returned `B` with a positive round. Unburned means Giraph returned `NB -1`. The configuration contained 348,087 vertices, 1,128,693 undirected connections and eight scheduled source rounds. Source selection was a reproducible random baseline. We must not call it optimal.

### Slide 12: Verification and runtime

The strongest correctness statement is the row count and exact comparison: Python expected 348,087 rows, Giraph produced 348,087 rows, and the comparison exit code was 0. The measured Giraph run took 54.887 seconds after YARN was running. Python preview took much longer because it wrote a full node-state table and burned-edge table for every round. That is a preview and explanation cost, not a fair distributed-runtime comparison.

### Slide 13: Our contribution

This slide names only our Group A contribution. Kumar can explain shared-server access, Hadoop/YARN checks, Giraph builds, input-driven Java integration, runners, large graph conversion, HDFS uploads and the reproducibility record. Archana can explain the graph model, baseline algorithms, output interpretation and presentation of the workflow. Both of us should understand all parts; this is a division of presentation responsibility, not a claim that one person alone did the whole project.

### Slide 14: Demonstration plan

For a live demo, first show the scheduled input directory, then run the validator, confirm a RUNNING YARN node, run the Giraph runner, display the `B/NB` output, and compare it with Python. If the network or lab service is unstable, use saved repository evidence rather than claiming a live result that was not observed.

### Slide 15: Conclusion and future work

Completed work includes the repeatable Hadoop/Giraph workflow, baseline algorithms, input-driven Graph Burning, and exact Python-versus-Giraph verification at 348k vertices. Future work includes confirming the final faculty burning constraints, running true multi-node experiments, comparing source-selection strategies, and extending our Group A implementation. The current result is a foundation, not the final optimization result.

### Slide 16: References and repository QR

The references point to Apache Giraph, Apache Hadoop, Stanford SNAP datasets and our GitHub repository. The QR code is placed here because it gives the panel a direct path to source code, weekly reports, datasets, commands and evidence after the explanation. Putting it on the first slide would make the opening slide busier and would invite scanning before the problem is understood.

## Vocabulary we must know

- **Graph:** a collection of vertices and edges.
- **Vertex:** one item in the graph, such as a person or page.
- **Edge:** a relationship or connection between two vertices.
- **Directed edge:** an edge with a source and a target.
- **Undirected edge:** a connection treated in both directions.
- **Adjacency list:** one vertex followed by its neighbours and optional weights.
- **Vertex value:** the current value stored at a vertex.
- **Message:** data sent from one vertex to another for a later superstep.
- **Superstep:** one synchronized phase of vertex computation.
- **HDFS:** Hadoop’s file system for storing distributed input and output.
- **YARN:** Hadoop’s resource manager and scheduler.
- **Container:** the execution allocation in which a task runs.
- **Giraph runner:** the command-line entry point that starts a Giraph job.
- **Input format:** the parser that converts text or JSON into typed vertices and edges.
- **Output format:** the writer that converts vertex values into result files.
- **Reference calculation:** an independent answer used for checking the distributed implementation.
- **`B`:** the vertex burned in the experiment.
- **`NB`:** the vertex not burned within the configured rounds.
- **First burn round:** the earliest round in which a vertex becomes burned.

## Questions the panel may ask

### Why did you use Apache Giraph?

Giraph provides a Pregel-style vertex-centric model that matches graph algorithms. It lets us define vertex computation and messages while Hadoop handles input, task execution and output.

### Where is the distributed concept used if you have one physical machine?

HDFS, YARN and Giraph still use distributed-system interfaces. Input is split into multiple files, YARN starts containers, and Giraph divides vertex work among mapper tasks. However, our current lab is a single-node pseudo-distributed cluster. We will measure real multi-node scaling later.

### Why do you use two accounts?

`hduser` runs Hadoop services because the service installation and permissions belong to that account. `mca2025` builds the project, uploads experiment input and submits Giraph jobs. This is an operational separation, not two different algorithms.

### Why are there multiple input files?

The files are partitions of one logical graph. HDFS reads the directory as a collection of input files. Multiple parts demonstrate the same pattern that a larger distributed dataset uses.

### Why did you use both JSON and text?

JSON helped us begin with Giraph’s existing typed input format. Plain text adjacency lists are easier to inspect, split and explain. The text format requires a matching custom reader because the line contains a vertex id followed by `neighbour:weight` tokens.

### What does exit code 0 mean in the comparison?

The comparison program found no difference between the expected Python rows and actual Giraph rows. It does not prove every possible graph is correct; it proves the tested input and configuration matched exactly.

### Is the random source sequence optimal?

No. It is a reproducible baseline used to test the workflow on a large graph. Finding an optimal or constrained source sequence is future work.

### Why did Python take longer than Giraph?

The Python preview wrote a complete node table and a burned-edge table for every round. Giraph wrote the final distributed result. They measured different workloads, so the times should not be compared as an algorithm speed contest.

### What is the largest verified result?

348,087 vertices and 1,128,693 undirected connections. Python and Giraph both produced 348,087 rows, with 243,095 burned and 104,992 unburned.

### What is the limitation of the current semester result?

The system is verified on the tested graphs, but it is still a single-node cluster, the source schedule is not optimized, and the final constrained burning model must be confirmed with the faculty.

### What will you do next?

We will confirm the exact burning-set constraints, run larger and multi-node experiments, compare source-selection methods, and keep the Python reference and Giraph implementation synchronized.

## Simple speaking order

1. Kumar introduces the problem, setup, architecture and input pipeline.
2. Archana explains the baseline algorithms and Graph Burning model.
3. Kumar presents the large-graph experiment and verification numbers.
4. Archana explains the contribution, limitations and future work.
5. Both answer questions using the definitions and evidence above.

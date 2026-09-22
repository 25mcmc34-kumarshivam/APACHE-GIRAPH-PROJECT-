# Why We Build Giraph with Maven

We repeated the Maven command while working on PageRank, degree, BFS and Graph
Burning. It helps to know which changes require a build and what the command
actually produces.

## The four separate things

```text
Java source code → Maven build → JAR file → Giraph job reads an HDFS dataset
```

1. **Source code:** `.java` files under
   `/home/mca2025/giraph/giraph-examples/src/main/java/...`. A new class or
   edit here is only text until compiled.
2. **Build instructions:** `pom.xml` files tell Maven which modules,
   dependencies, plugins and Hadoop profile to use.
3. **Artifact:** the build writes compiled `.class` files and JARs under
   `target/`. Our runner uses the shaded examples JAR:
   `/home/mca2025/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar`.
4. **Input data:** graph files live on the local disk first and are uploaded to
   HDFS. Replacing a graph file does not change Java bytecode.

Hadoop and YARN are the installed runtime. Running Maven does not reinstall
Hadoop or change the basic service configuration. It rebuilds the Giraph
project and replaces generated artifacts in its `target/` directories.

## The command used in our lab

Run as `mca2025` from the Giraph project root:

```bash
cd "$HOME/giraph"
mvn clean -Phadoop_2 -DskipTests -Dgiraph.maven.duplicate.finder.skip=true package
```

| Part | What it does | Why we use it |
|---|---|---|
| `cd "$HOME/giraph"` | Enters the source repository containing the parent `pom.xml`. | Maven discovers the full module build from this location. |
| `mvn` | Starts Maven. | Maven follows the instructions in the POM files. |
| `clean` | Removes previous generated `target/` outputs. | Avoids relying on stale compiled files. It does not remove `src/` or HDFS data. |
| `-Phadoop_2` | Activates the `hadoop_2` profile. | The Giraph source supports multiple Hadoop build variants; this lab uses Hadoop 2.7.7. |
| `-DskipTests` | Skips running the test suite during this build. | Speeds iteration. It is **not** proof the new algorithm works; we must test its actual output. |
| `-Dgiraph.maven.duplicate.finder.skip=true` | Sets a project property to skip the duplicate dependency check. | Used in this installation's known build configuration. |
| `package` | Executes the Maven lifecycle through packaging. | Compiles `.java` to `.class` and creates JAR artifacts. |

The `Reactor Summary` lists the modules Maven processed. Our new algorithms
are under `giraph-examples`, but the parent build also builds Core, Blocks and
Distribution because the modules depend on one another. `BUILD SUCCESS` means
Maven finished; it does not validate the mathematical output.

## Why we rebuilt for each program

PageRank itself was already in Giraph, but we changed build configuration to
produce a Hadoop compatible shaded JAR. Later, we added our own degree, BFS
and Graph Burning `.java` classes. After each Java change, we rebuilt to put
the new bytecode into the JAR. `hadoop jar` executes the JAR; it does not read
the `.java` source directly.

If Java source has **not** changed since the last successful build, rerunning
the same algorithm on another graph does not require Maven. Only the HDFS input
path, output path or configuration arguments change.

## How to decide what to do without memorizing a command

| What changed? | Required action |
|---|---|
| `.java` source or `pom.xml` | Build again; verify the intended class is inside the new JAR. |
| Only local graph data | Upload the changed data to HDFS; use a new output path. No build. |
| Only source vertex or burning sequence | Change the job argument. No build. |
| Only explanation/README files | No build and no Hadoop job required. |
| Hadoop services stopped after reboot | Start HDFS and YARN as `hduser`; this is independent of Maven. |

## Verify what was built

For Graph Burning:

```bash
jar tf "$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar" \
  | grep 'LearningGraphBurningComputation.class'
```

`jar tf` lists the JAR's contents. The expected class entry is:

```text
org/apache/giraph/examples/LearningGraphBurningComputation.class
```

That check succeeded on 22 September 2026 after the Graph Burning source was
transferred and the Maven reactor reported `BUILD SUCCESS` in 48.461 seconds.
The next necessary check is a Giraph run compared with a manual answer.

## Normal sequence for a new algorithm

1. Work out a small graph and expected result on paper.
2. Put the Java class in the correct Giraph package and source directory.
3. Run Maven from the repository root and confirm `BUILD SUCCESS`.
4. Use `jar tf` to confirm the class is present in the actual runnable JAR.
5. Upload the small graph to HDFS.
6. Run with a **new** HDFS output directory.
7. Compare every output value with the manual calculation.
8. Only then try larger or multiple-part datasets.

## Important paths and accounts

- `hduser` starts and stops HDFS/YARN.
- `mca2025` edits/builds Giraph and submits jobs.
- `/home/mca2025/giraph` is the upstream Giraph source checkout used for
  building on the server.
- This GitHub repository holds our project source copies, scripts, datasets,
  explanations and results. Pushing a file here does **not** automatically
  transfer it into the server's Giraph checkout or rebuild its JAR.

The last point explains why we transferred the new Java class with `scp`, then
ran Maven on the server. These are separate actions.

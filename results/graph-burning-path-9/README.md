# Verified Graph Burning Experiment — Nine-Vertex Path

The Giraph job ran on the lab's Hadoop 2.7.7 single-node cluster on
23 September 2026. Input was the three-part path dataset in
[`datasets/graph-burning-path-9/`](../../datasets/graph-burning-path-9/).
Sources `3:8:6` were ignited in rounds 1, 2 and 3, respectively.

The actual HDFS output was:

```text
/user/mca2025/giraph_learning/graph_burning_path9_output
```

The values in [`burn-rounds-3-8-6.txt`](burn-rounds-3-8-6.txt) were copied
from the successful runner output. Every one of the nine values matches the
manual calculation in the dataset README. The last burn round is 3, and the
known path result `b(P9)=ceil(sqrt(9))=3` confirms this sequence is optimal
**for this path graph**.

This experiment validates simulation for one known graph and source sequence.
The computation does not itself search for a minimum sequence. It currently
does not reject a source ID that is absent or already burned, so future tests
must validate source sequences before interpreting them as valid burning
sequences. Larger and disconnected graph tests remain to be done.

## Commands used

After copying the Java source into the server's Giraph examples package:

```bash
cd "$HOME/giraph"
mvn clean -Phadoop_2 -DskipTests -Dgiraph.maven.duplicate.finder.skip=true package
jar tf giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar \
  | grep 'LearningGraphBurningComputation.class'
bash "$HOME/giraph/run_graph_burning.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_input \
  /user/mca2025/giraph_learning/graph_burning_path9_output \
  3:8:6
```

The first run used `3,8,6` and failed **before YARN submission** because
Giraph's `-ca` parser split that value at commas. The source and runner were
changed to use colons. Java was rebuilt, and the second run completed.

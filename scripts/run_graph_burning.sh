#!/usr/bin/env bash
# Run the deterministic Graph Burning simulator on a text adjacency-list graph.
# Usage: run_graph_burning.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH SOURCE_SEQUENCE
# Example SOURCE_SEQUENCE: 3,8,6

set -euo pipefail

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

INPUT_PATH="${1:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"
OUTPUT_PATH="${2:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"
SOURCE_SEQUENCE="${3:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"

test -f "$GIRAPH_JAR" || {
  echo "ERROR: Missing Giraph JAR: $GIRAPH_JAR"; exit 1;
}
hdfs dfs -test -e "$INPUT_PATH" || {
  echo "ERROR: Missing HDFS input: $INPUT_PATH"; exit 1;
}
! hdfs dfs -test -e "$OUTPUT_PATH" || {
  echo "ERROR: HDFS output already exists: $OUTPUT_PATH"; exit 1;
}
yarn node -list 2>&1 | grep -q 'RUNNING' || {
  echo "ERROR: No RUNNING YARN NodeManager found"; exit 1;
}

echo "Graph Burning source sequence: $SOURCE_SEQUENCE"
hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  org.apache.giraph.examples.LearningGraphBurningComputation \
  -vif org.apache.giraph.examples.LongDoubleFloatTextInputFormat \
  -vip "$INPUT_PATH" \
  -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
  -op "$OUTPUT_PATH" \
  -w 1 \
  -ca mapred.job.tracker=yarn \
  -ca "LearningGraphBurning.sourceSequence=$SOURCE_SEQUENCE"

echo "Graph Burning completed: $OUTPUT_PATH"
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\* | sort -n

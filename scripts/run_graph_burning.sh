#!/usr/bin/env bash
# Run the deterministic Graph Burning simulator on a text adjacency-list graph.
# Usage: run_graph_burning.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH SOURCE_SEQUENCE
# Example SOURCE_SEQUENCE: 3:8:6 (Giraph reserves commas in -ca values)

set -euo pipefail
# -e: stop after a failed command; -u: reject missing variables;
# pipefail: a failed command inside a pipeline also makes the pipeline fail.

# Use installed Java/Hadoop locations when the SSH shell has not loaded them.
# The ${NAME:-fallback} form keeps an already configured value if present.
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

# $1, $2 and $3 are the three words placed after the script name.
# The :? syntax prints Usage and stops if a required word is absent.
INPUT_PATH="${1:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"
OUTPUT_PATH="${2:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"
SOURCE_SEQUENCE="${3:?Usage: run_graph_burning.sh INPUT OUTPUT SOURCES}"

# The colon separates source IDs. A comma would be split by Giraph's -ca
# parser into different settings; the regular expression catches that early.
if [[ ! "$SOURCE_SEQUENCE" =~ ^-?[0-9]+(:-?[0-9]+)*$ ]]; then
  echo "ERROR: SOURCES must be colon-separated vertex IDs, for example 3:8:6"
  exit 2
fi

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"

# Check all prerequisites BEFORE asking Hadoop to submit a job.
test -f "$GIRAPH_JAR" || {
  echo "ERROR: Missing Giraph JAR: $GIRAPH_JAR"; exit 1;
}
hdfs dfs -test -e "$INPUT_PATH" || {
  echo "ERROR: Missing HDFS input: $INPUT_PATH"; exit 1;
}
! hdfs dfs -test -e "$OUTPUT_PATH" || {
  # Hadoop job output paths must be new: it will not overwrite old results.
  echo "ERROR: HDFS output already exists: $OUTPUT_PATH"; exit 1;
}
# This checks YARN's reported node state, not the real Linux process.
# If YARN has a stale node, also inspect: ps -ef | grep '[N]odeManager'.
yarn node -list 2>&1 | grep -q 'RUNNING' || {
  echo "ERROR: No RUNNING YARN NodeManager found"; exit 1;
}

echo "Graph Burning source sequence: $SOURCE_SEQUENCE"
# hadoop jar starts the Giraph job. The class after GiraphRunner is OUR
# algorithm; -vif reads graph lines; -vip identifies the HDFS input; -vof
# prints vertex ID and value; -op is the new HDFS output directory.
# -w 1 uses one worker for our single-node teaching setup.
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
# part-m-* are Hadoop's output files. cat joins their contents; sort -n
# presents numeric vertex IDs in order. This does not change HDFS data.
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\* | sort -n

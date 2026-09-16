#!/usr/bin/env bash
# TEACHING COPY — original: scripts/run_shortest_path.sh
# Weighted shortest path calculates minimum total edge weight from SOURCE_ID.
# Ye BFS nahi hai: BFS hops count karta hai, this algorithm weights add karta hai.

set -euo pipefail
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
INPUT_PATH="${1:?Usage: run_shortest_path.sh INPUT SOURCE_ID OUTPUT}"
SOURCE_ID="${2:?Usage: run_shortest_path.sh INPUT SOURCE_ID OUTPUT}"
OUTPUT_PATH="${3:?Usage: run_shortest_path.sh INPUT SOURCE_ID OUTPUT}"

test -f "$GIRAPH_JAR" || { echo "Missing Giraph JAR: $GIRAPH_JAR"; exit 1; }
hdfs dfs -test -e "$INPUT_PATH" || { echo "Missing HDFS input: $INPUT_PATH"; exit 1; }
! hdfs dfs -test -e "$OUTPUT_PATH" || { echo "Output already exists: $OUTPUT_PATH"; exit 1; }
yarn node -list | grep -q 'RUNNING' || { echo "No RUNNING YARN NodeManager found"; exit 1; }

hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  org.apache.giraph.examples.SimpleShortestPathsComputation \
  -vif org.apache.giraph.io.formats.JsonLongDoubleFloatDoubleVertexInputFormat \
  -vip "$INPUT_PATH" \
  -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
  -op "$OUTPUT_PATH" \
  -w 1 \
  -ca mapred.job.tracker=yarn \
  -ca SimpleShortestPathsVertex.sourceId="$SOURCE_ID"
# Last custom argument is essential: source vertex ko distance 0 milta hai;
# other vertices minimum received weighted distance update karte hain.

echo "Shortest-path job completed: $OUTPUT_PATH"
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\*

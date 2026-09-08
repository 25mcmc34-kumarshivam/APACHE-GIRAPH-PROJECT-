#!/usr/bin/env bash
set -euo pipefail

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
INPUT_PATH="${1:?Usage: run_pagerank.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH}"
OUTPUT_PATH="${2:?Usage: run_pagerank.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH}"

test -f "$GIRAPH_JAR" || { echo "Missing Giraph JAR: $GIRAPH_JAR"; exit 1; }
hdfs dfs -test -e "$INPUT_PATH" || { echo "Missing HDFS input: $INPUT_PATH"; exit 1; }
! hdfs dfs -test -e "$OUTPUT_PATH" || { echo "Output already exists: $OUTPUT_PATH"; exit 1; }
yarn node -list | grep -q 'RUNNING' || { echo "No RUNNING YARN NodeManager found"; exit 1; }

hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  org.apache.giraph.examples.SimplePageRankComputation \
  -vif org.apache.giraph.io.formats.JsonLongDoubleFloatDoubleVertexInputFormat \
  -vip "$INPUT_PATH" \
  -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
  -op "$OUTPUT_PATH" \
  -w 1 \
  -mc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankMasterCompute' \
  -wc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankWorkerContext' \
  -ca mapred.job.tracker=yarn

echo "PageRank completed: $OUTPUT_PATH"
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\*

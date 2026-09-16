#!/usr/bin/env bash
# TEACHING COPY — original: scripts/run_pagerank.sh
# This older script runs PageRank on the JSON-array input used in the first lab.
# New text datasets should normally use run_text_graph_algorithm.sh instead.

set -euo pipefail
# -e = stop on failure; -u = undefined variable is error; pipefail = pipeline
# me koi bhi command fail ho to complete pipeline fail mani jayegi.

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

# Fat/shaded JAR contains Giraph, our classes and relocated Guava classes.
GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
# `${1:?message}` requires argument 1; `${2:?message}` requires argument 2.
INPUT_PATH="${1:?Usage: run_pagerank.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH}"
OUTPUT_PATH="${2:?Usage: run_pagerank.sh INPUT_HDFS_PATH OUTPUT_HDFS_PATH}"

# Fail early with understandable messages instead of submitting a broken job.
test -f "$GIRAPH_JAR" || { echo "Missing Giraph JAR: $GIRAPH_JAR"; exit 1; }
hdfs dfs -test -e "$INPUT_PATH" || { echo "Missing HDFS input: $INPUT_PATH"; exit 1; }
# Giraph/Hadoop refuses an existing output directory, so the check is reversed.
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
# `hadoop jar`: YARN par Java program submit karta hai.
# GiraphRunner: command-line configuration read karta hai.
# computation: PageRank ka vertex-centric algorithm.
# JSON VIF: har JSON line ko vertex/value/weighted edges me convert karta hai.
# IdWithValue output: result me `vertex-id value` likhta hai.
# `mapred.job.tracker=yarn`: old Hadoop key ko YARN mode par force karta hai.

echo "PageRank completed: $OUTPUT_PATH"
# `part-m-*` output part files ko print karta hai; backslash prevents local shell
# expansion so HDFS receives the wildcard.
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\*

#!/usr/bin/env bash
# Run one supported Giraph algorithm on a text adjacency-list dataset.
#
# Usage:
#   run_text_graph_algorithm.sh ALGORITHM INPUT OUTPUT [SOURCE_ID]
#
# Algorithms:
#   pagerank, outdegree, indegree, bfs, shortest-path
#
# BFS and shortest-path use SOURCE_ID. It defaults to vertex 1.

set -euo pipefail

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

usage() {
  cat <<'EOF'
Usage:
  run_text_graph_algorithm.sh ALGORITHM INPUT OUTPUT [SOURCE_ID]

Algorithms:
  pagerank
  outdegree
  indegree
  bfs
  shortest-path

Example:
  ./run_text_graph_algorithm.sh bfs \
    /user/mca2025/giraph_learning/thirty_node_text_input \
    /user/mca2025/giraph_learning/thirty_node_bfs_from_1_output \
    1
EOF
}

if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  usage
  exit 2
fi

ALGORITHM="$1"
INPUT_PATH="$2"
OUTPUT_PATH="$3"
SOURCE_ID="${4:-1}"

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
TEXT_INPUT_FORMAT="org.apache.giraph.examples.LongDoubleFloatTextInputFormat"
TEXT_OUTPUT_FORMAT="org.apache.giraph.io.formats.IdWithValueTextOutputFormat"

case "$ALGORITHM" in
  pagerank)
    COMPUTATION="org.apache.giraph.examples.SimplePageRankComputation"
    ;;
  outdegree)
    COMPUTATION="org.apache.giraph.examples.LearningOutDegreeComputation"
    ;;
  indegree)
    COMPUTATION="org.apache.giraph.examples.LearningInDegreeComputation"
    ;;
  bfs)
    COMPUTATION="org.apache.giraph.examples.LearningBfsComputation"
    ;;
  shortest-path)
    COMPUTATION="org.apache.giraph.examples.SimpleShortestPathsComputation"
    ;;
  *)
    echo "ERROR: Unsupported algorithm: $ALGORITHM"
    usage
    exit 2
    ;;
esac

if ! [[ "$SOURCE_ID" =~ ^-?[0-9]+$ ]]; then
  echo "ERROR: SOURCE_ID must be an integer: $SOURCE_ID"
  exit 2
fi

for required_command in java hadoop hdfs yarn; do
  if ! command -v "$required_command" >/dev/null 2>&1; then
    echo "ERROR: Required command is unavailable: $required_command"
    exit 1
  fi
done

if [ ! -f "$GIRAPH_JAR" ]; then
  echo "ERROR: Giraph JAR is missing:"
  echo "$GIRAPH_JAR"
  exit 1
fi

if ! hdfs dfs -test -e "$INPUT_PATH"; then
  echo "ERROR: HDFS input does not exist:"
  echo "$INPUT_PATH"
  exit 1
fi

if hdfs dfs -test -e "$OUTPUT_PATH"; then
  echo "ERROR: HDFS output already exists:"
  echo "$OUTPUT_PATH"
  echo "Giraph requires a new output path for every run."
  exit 1
fi

YARN_NODES="$(yarn node -list 2>&1)"
printf '%s\n' "$YARN_NODES"
if ! printf '%s\n' "$YARN_NODES" | grep -q 'RUNNING'; then
  echo "ERROR: No RUNNING YARN NodeManager is registered."
  echo "Restart YARN as hduser before submitting the job."
  exit 1
fi

GIRAPH_ARGS=(
  "$COMPUTATION"
  -vif "$TEXT_INPUT_FORMAT"
  -vip "$INPUT_PATH"
  -vof "$TEXT_OUTPUT_FORMAT"
  -op "$OUTPUT_PATH"
  -w 1
  -ca mapred.job.tracker=yarn
)

case "$ALGORITHM" in
  pagerank)
    GIRAPH_ARGS+=(
      -mc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankMasterCompute'
      -wc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankWorkerContext'
    )
    ;;
  bfs)
    GIRAPH_ARGS+=(
      -ca "LearningBfsComputation.sourceId=$SOURCE_ID"
    )
    ;;
  shortest-path)
    GIRAPH_ARGS+=(
      -ca "SimpleShortestPathsVertex.sourceId=$SOURCE_ID"
    )
    ;;
esac

echo "Submitting $ALGORITHM job..."
echo "Input:  $INPUT_PATH"
echo "Output: $OUTPUT_PATH"
if [ "$ALGORITHM" = "bfs" ] || [ "$ALGORITHM" = "shortest-path" ]; then
  echo "Source: $SOURCE_ID"
fi

hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  "${GIRAPH_ARGS[@]}"

echo
echo "$ALGORITHM completed successfully."
echo "Result:"
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\* | sort -n

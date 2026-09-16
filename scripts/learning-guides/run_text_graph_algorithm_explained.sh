#!/usr/bin/env bash
# TEACHING COPY — original: scripts/run_text_graph_algorithm.sh
# One common runner avoids retyping the long `hadoop jar` command.
# Ek hi script PageRank, degree, BFS aur shortest path select/run karti hai.
# Usage: script ALGORITHM HDFS_INPUT HDFS_OUTPUT [SOURCE_ID]

set -euo pipefail

# Defaults make the script work even if an SSH shell did not load .bashrc.
# Existing environment values are respected; otherwise lab paths are used.
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

usage() {
  # Quoted EOF stops Bash from expanding `$` or variables in help text.
  cat <<'EOF'
Usage:
  run_text_graph_algorithm.sh ALGORITHM INPUT OUTPUT [SOURCE_ID]

Algorithms: pagerank, outdegree, indegree, bfs, shortest-path
SOURCE_ID is used by bfs/shortest-path and defaults to 1.
EOF
}

# `$#` is argument count. Three required, at most four accepted.
if [ "$#" -lt 3 ] || [ "$#" -gt 4 ]; then
  usage
  exit 2 # 2 means incorrect command usage, not a cluster failure.
fi

ALGORITHM="$1"   # Human-friendly short algorithm name.
INPUT_PATH="$2"  # HDFS file or directory; directory can contain many parts.
OUTPUT_PATH="$3" # Must be a new HDFS directory.
SOURCE_ID="${4:-1}" # Optional fourth value; default vertex is 1.

GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
# Text reader expects: vertex_id neighbor_id:weight neighbor_id:weight ...
TEXT_INPUT_FORMAT="org.apache.giraph.examples.LongDoubleFloatTextInputFormat"
# Output writer produces two columns: vertex ID and final vertex value.
TEXT_OUTPUT_FORMAT="org.apache.giraph.io.formats.IdWithValueTextOutputFormat"

# `case` maps easy names to full Java class names. It is clearer and safer
# than asking a beginner to type a package name every time.
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

# Regex permits an optional minus sign and one or more digits. Source ID text
# like `one` is rejected before YARN resources are used.
if ! [[ "$SOURCE_ID" =~ ^-?[0-9]+$ ]]; then
  echo "ERROR: SOURCE_ID must be an integer: $SOURCE_ID"
  exit 2
fi

# Check every executable. `command -v` searches PATH; hidden output keeps the
# error message simple. Loop avoids writing the same test four times.
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

# HDFS is a separate filesystem, so ordinary `test -e` cannot check this path.
if ! hdfs dfs -test -e "$INPUT_PATH"; then
  echo "ERROR: HDFS input does not exist:"
  echo "$INPUT_PATH"
  exit 1
fi

# Hadoop output committers require a new directory to prevent overwriting data.
if hdfs dfs -test -e "$OUTPUT_PATH"; then
  echo "ERROR: HDFS output already exists:"
  echo "$OUTPUT_PATH"
  echo "Giraph requires a new output path for every run."
  exit 1
fi

# Capture output once, show it to the learner, then search it for RUNNING.
YARN_NODES="$(yarn node -list 2>&1)"
printf '%s\n' "$YARN_NODES"
if ! printf '%s\n' "$YARN_NODES" | grep -q 'RUNNING'; then
  echo "ERROR: No RUNNING YARN NodeManager is registered."
  echo "Restart YARN as hduser before submitting the job."
  exit 1
fi

# Bash array keeps each option/value as a separate safe argument. Quoted array
# expansion later prevents spaces or special characters from being split.
GIRAPH_ARGS=(
  "$COMPUTATION"
  -vif "$TEXT_INPUT_FORMAT"
  -vip "$INPUT_PATH"
  -vof "$TEXT_OUTPUT_FORMAT"
  -op "$OUTPUT_PATH"
  -w 1
  -ca mapred.job.tracker=yarn
)

# Only algorithms needing extra configuration receive it.
case "$ALGORITHM" in
  pagerank)
    GIRAPH_ARGS+=(
      -mc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankMasterCompute'
      -wc 'org.apache.giraph.examples.SimplePageRankComputation$SimplePageRankWorkerContext'
    )
    ;;
  bfs)
    GIRAPH_ARGS+=( -ca "LearningBfsComputation.sourceId=$SOURCE_ID" )
    ;;
  shortest-path)
    GIRAPH_ARGS+=( -ca "SimpleShortestPathsVertex.sourceId=$SOURCE_ID" )
    ;;
esac

echo "Submitting $ALGORITHM job..."
echo "Input:  $INPUT_PATH"
echo "Output: $OUTPUT_PATH"
if [ "$ALGORITHM" = "bfs" ] || [ "$ALGORITHM" = "shortest-path" ]; then
  echo "Source: $SOURCE_ID"
fi

# Actual submission. `"${GIRAPH_ARGS[@]}"` expands every array item as exactly
# one command argument. Giraph communicates through YARN/HDFS and writes result
# part files under OUTPUT_PATH.
hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  "${GIRAPH_ARGS[@]}"

echo
echo "$ALGORITHM completed successfully."
echo "Result:"
# Sort numerically by first column so vertex 2 comes before vertex 10.
hdfs dfs -cat "$OUTPUT_PATH"/part-m-\* | sort -n

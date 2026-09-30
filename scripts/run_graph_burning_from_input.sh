#!/usr/bin/env bash
# Run Graph Burning with one source round written on each vertex's input line.
# Usage: run_graph_burning_from_input.sh HDFS_INPUT HDFS_OUTPUT
# The final output contains vertex<TAB>B/NB<TAB>first_round_or_minus_one.

set -euo pipefail

export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

if [ "$#" -ne 2 ]; then
  echo 'Usage: run_graph_burning_from_input.sh HDFS_INPUT HDFS_OUTPUT' >&2
  exit 2
fi
INPUT_PATH="$1"
OUTPUT_PATH="$2"
# Giraph first writes numeric state here. We keep it for debugging; the
# readable B/NB output is placed at the requested OUTPUT_PATH afterward.
RAW_PATH="${OUTPUT_PATH}.__giraph_raw"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GIRAPH_JAR="$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"

for command_name in java python3 hadoop hdfs yarn; do
  command -v "$command_name" >/dev/null 2>&1 || {
    echo "ERROR: missing command $command_name" >&2; exit 1;
  }
done
test -f "$GIRAPH_JAR" || { echo "ERROR: missing JAR $GIRAPH_JAR" >&2; exit 1; }
test -f "$SCRIPT_DIR/validate_burning_schedule.py" || {
  echo 'ERROR: validator must be beside this runner' >&2; exit 1;
}
test -f "$SCRIPT_DIR/format_burning_output.py" || {
  echo 'ERROR: formatter must be beside this runner' >&2; exit 1;
}
hdfs dfs -test -e "$INPUT_PATH" || {
  echo "ERROR: HDFS input missing: $INPUT_PATH" >&2; exit 1;
}
if hdfs dfs -test -e "$OUTPUT_PATH" || hdfs dfs -test -e "$RAW_PATH"; then
  echo "ERROR: output or raw path already exists: $OUTPUT_PATH / $RAW_PATH" >&2
  echo 'Choose a new output name; existing results are never overwritten.' >&2
  exit 1
fi
YARN_NODES="$(yarn node -list 2>&1)"
printf '%s\n' "$YARN_NODES"
if ! printf '%s\n' "$YARN_NODES" | grep -q 'RUNNING'; then
  echo 'ERROR: no RUNNING YARN NodeManager was reported' >&2
  exit 1
fi

read_hdfs_input() {
  if hdfs dfs -test -d "$INPUT_PATH"; then
    # Quote the HDFS glob so the LOCAL shell does not expand it.
    hdfs dfs -cat "${INPUT_PATH}/*.txt"
  else
    hdfs dfs -cat "$INPUT_PATH"
  fi
}

# The input file, not a typed source list, determines the total rounds.
# Validation also requires one legal source per round and reverse edges.
TOTAL_ROUNDS="$(read_hdfs_input | python3 "$SCRIPT_DIR/validate_burning_schedule.py" --stdin --rounds-only)"
echo "Input schedule is valid for $TOTAL_ROUNDS round(s)."
echo "Numeric Giraph output: $RAW_PATH"

hadoop jar "$GIRAPH_JAR" \
  org.apache.giraph.GiraphRunner \
  org.apache.giraph.examples.LearningGraphBurningFromInputComputation \
  -vif org.apache.giraph.examples.BurningScheduleTextInputFormat \
  -vip "$INPUT_PATH" \
  -vof org.apache.giraph.io.formats.IdWithValueTextOutputFormat \
  -op "$RAW_PATH" \
  -w 1 \
  -ca mapred.job.tracker=yarn \
  -ca "LearningGraphBurningFromInput.totalRounds=$TOTAL_ROUNDS"

# Convert numeric states to the requested B/NB format and save them in HDFS.
# pipefail ensures a broken HDFS read or formatter cannot be reported as OK.
hdfs dfs -mkdir -p "$OUTPUT_PATH"
hdfs dfs -cat "${RAW_PATH}/part-m-*" \
  | python3 "$SCRIPT_DIR/format_burning_output.py" \
  | sort -n \
  | hdfs dfs -put - "$OUTPUT_PATH/part-00000"

echo "Readable Graph Burning output: $OUTPUT_PATH/part-00000"
hdfs dfs -cat "$OUTPUT_PATH/part-00000"

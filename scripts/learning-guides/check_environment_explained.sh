#!/usr/bin/env bash
# TEACHING COPY — original: scripts/check_environment.sh
# Purpose: job run karne se pehle required commands aur Hadoop services check
# karna. This script changes no HDFS data and starts/stops no daemon.

set -u
# `-u`: undefined variable use hone par Bash error dega. `-e` intentionally
# nahi hai because we want to complete all checks and report every problem.

# `${NAME:-default}` means: existing value rakho; unset/empty ho to default use
# karo. Export makes these values available to child commands.
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export HADOOP_CONF_DIR="${HADOOP_CONF_DIR:-$HADOOP_HOME/etc/hadoop}"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"

failures=0 # Har missing/failed check ke liye counter increment hoga.

check_command() {
  # `$1` function ko diya gaya command name hai. `command -v` executable ka
  # resolved path batata hai. Output hidden hai because we print our own line.
  if command -v "$1" >/dev/null 2>&1; then
    printf '[OK] %s: %s\n' "$1" "$(command -v "$1")"
  else
    printf '[MISSING] command: %s\n' "$1"
    failures=$((failures + 1))
  fi
}

echo '=== Commands ==='
# Loop repeats the same function for every required tool.
for command_name in java javac git mvn ssh hadoop hdfs yarn jps; do
  check_command "$command_name"
done

echo
echo '=== Versions ==='
# `2>&1` combines stderr with stdout. `head -n 1` keeps output short.
# `|| true` lets later checks continue even if one program is missing.
java -version 2>&1 | head -n 1 || true
hadoop version 2>/dev/null | head -n 1 || true
mvn -version 2>/dev/null | head -n 1 || true
git --version 2>/dev/null || true

echo
echo '=== Hadoop processes ==='
jps 2>/dev/null || true # Java processes owned by the current Unix user.

echo
echo '=== HDFS ==='
if hdfs dfsadmin -report >/dev/null 2>&1; then
  echo '[OK] NameNode is reachable.'
else
  echo '[NOT READY] NameNode is not reachable.'
  failures=$((failures + 1))
fi

echo
echo '=== YARN ==='
# Save both output and error text so it can be displayed and examined.
yarn_nodes="$(yarn node -list 2>&1 || true)"
printf '%s\n' "$yarn_nodes"
if printf '%s\n' "$yarn_nodes" | grep -q 'RUNNING'; then
  echo '[OK] A RUNNING NodeManager is registered.'
else
  echo '[NOT READY] No RUNNING NodeManager is registered.'
  failures=$((failures + 1))
fi

echo
if [ "$failures" -eq 0 ]; then
  echo 'Environment check passed.'
else
  echo "Environment check found $failures problem(s). Read docs/INSTALLATION.md."
  exit 1 # Non-zero tells another script/terminal that readiness failed.
fi

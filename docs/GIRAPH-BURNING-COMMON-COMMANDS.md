# Common command procedure for a Graph Burning experiment

This is the reusable procedure. The graph name, parts, schedule, HDFS input
and HDFS output change; the overall workflow stays the same.

## 1. Connect

```powershell
ssh hduser@<CURRENT-IP>
ssh mca2025@<CURRENT-IP>
```

Use `hduser` for Hadoop services and `mca2025` for source files, HDFS input,
Giraph jobs and result downloads.

## 2. Start and check Hadoop (hduser terminal)

```bash
start-dfs.sh
start-yarn.sh
jps
yarn node -list
```

At least one NodeManager must show `RUNNING`. Do not submit while it says
`Total Nodes:0`.

## 3. Check the environment (mca2025 terminal)

```bash
whoami
command -v hdfs
command -v yarn
ls -lh "$HOME/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar"
```

## 4. Validate or create input

The scheduled text format is:

```text
vertex_id source_round neighbour_id:weight neighbour_id:weight ...
```

`0` means not a source. The graph needs one line per vertex, reverse edges
for an undirected experiment, one source per round and contiguous rounds.

```bash
python3 "$HOME/giraph/validate_burning_schedule.py" \
  "$HOME/giraph_learning_burning/<schedule-directory>"
```

For a SNAP edge list, convert and schedule it:

```bash
python3 "$HOME/giraph/convert_snap_edge_list.py" \
  "$HOME/giraph_learning_large/snap/<source-file>" \
  "$HOME/giraph_learning_large/<unscheduled-directory>" \
  --max-node-id <BOUND> --parts <PART_COUNT>

python3 "$HOME/giraph/prepare_random_burning_input.py" \
  "$HOME/giraph_learning_large/<unscheduled-directory>" \
  "$HOME/giraph_learning_large/<scheduled-directory>" \
  --rounds <ROUNDS> --seed <SEED>
```

The ID bound is not a promised vertex count. Use the converter's measured
`Vertices:` result.

## 5. Preview expected output

```bash
preview=$(mktemp -d "$HOME/giraph_learning_burning/preview-XXXXXX")
python3 "$HOME/giraph/show_burning_rounds.py" \
  "$HOME/giraph_learning_burning/<schedule-directory>" \
  --output-dir "$preview"
```

The output directory must start empty. The preview creates `expected.tsv` and
one node/edge table per round. It can be slow because it writes detailed
intermediate state.

## 6. Upload parts to HDFS

```bash
hdfs_input=/user/mca2025/giraph_learning/<experiment>_input
hdfs dfs -test -e "$hdfs_input" || {
  hdfs dfs -mkdir -p "$hdfs_input"
  hdfs dfs -put "$HOME/giraph_learning_burning/<schedule-directory>"/part-*.txt "$hdfs_input/"
}
hdfs dfs -ls "$hdfs_input"
```

Only `part-*.txt` files belong in the HDFS input directory. Do not upload
`selection.json`, preview logs or expected output as input.

## 7. Run Giraph

```bash
hdfs_output=/user/mca2025/giraph_learning/<experiment>_output
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  "$hdfs_input" "$hdfs_output"
```

The runner refuses to overwrite an existing result. Use a new output name for
a repeat. For wall-clock timing:

```bash
time bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  "$hdfs_input" "/user/mca2025/giraph_learning/<experiment>_output_timed"
```

`real` is elapsed time; `user` and `sys` are CPU accounting values.

## 8. Inspect and compare

```bash
hdfs dfs -ls "$hdfs_output"
hdfs dfs -cat "$hdfs_output/part-00000" | head
hdfs dfs -cat "$hdfs_output/part-00000" > "$HOME/giraph_learning_large/<experiment>_giraph_actual.tsv"
cmp -s "$HOME/giraph_learning_large/<experiment>_giraph_actual.tsv" \
  "$preview/expected.tsv"
echo "Comparison exit code: $?"
```

Exit code `0` means the complete Python and Giraph files match. It does not
mean that the source schedule is optimal.

## 9. Save evidence

Copy scheduled parts, `selection.json`, `expected.tsv`, round tables and the
Giraph output into clearly named `datasets/` and `results/` folders. Add the
experiment to `docs/EXPERIMENT-INDEX.md` and record exact commands, errors,
fixes, timings and counts in the current weekly report. Never commit
passwords, SSH keys, Hadoop logs, `target/` directories or the original huge
SNAP file.

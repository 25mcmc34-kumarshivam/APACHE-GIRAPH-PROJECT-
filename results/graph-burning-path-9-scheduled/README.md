# Verified input-driven Graph Burning result: nine-node path

The new runner completed on the lab Giraph/Hadoop setup on 30 September
2026. Its HDFS input directory contained the three `part-*.txt` files from
`datasets/graph-burning-path-9-scheduled/`. Source round markers in those
files selected vertex 3 in round 1, vertex 8 in round 2 and vertex 6 in
round 3. The command did **not** pass `3:8:6` as a source-list argument.

Command:

```bash
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input \
  /user/mca2025/giraph_learning/graph_burning_path9_scheduled_output
```

The runner reported the readable HDFS file
`/user/mca2025/giraph_learning/graph_burning_path9_scheduled_output/part-00000`.
The actual nine rows, copied from the user's terminal output, are in
`part-00000.txt` beside this README. `B` means burned; the last column is
the first burn round. Each row matches the manual prediction. No vertex
remained unburned in this test. The runner also preserves raw numeric
Giraph values in the sibling HDFS directory ending `.__giraph_raw`.

This verifies the **new input-driven computation and output formatting**
on one completely burned graph. It does not yet verify `NB -1` in a real
Giraph run; that needs a deliberately incomplete source schedule.

## Later round-by-round preview and comparison

By 26 October 2026, we ran `scripts/show_burning_rounds.py` on a local copy
of this same HDFS input. Its [`round-preview/`](round-preview/) folder holds
`expected.tsv`, three per-round vertex tables, three per-round burned-edge
tables, three NetworkX GraphML burned subgraphs and three PNG snapshots.
This preview matched the **saved 30 September Giraph output** exactly:
`diff -u expected.tsv part-00000` returned exit code 0. No new Giraph job
was submitted for this later comparison. The server file timestamps showed
20 October, different from the client date; the files have not been relabelled
as a new Giraph run.

In the PNGs blue means the current source, orange another newly burned
vertex, yellow previously burned, and grey unburned. Dark edges join two
burned endpoints; they show the induced subgraph, not necessarily the fire's
travel path. The [Hinglish study guide](../../study-material/hinglish-code-guide/show-burning-rounds-Hinglish.md)
explains every file and step.

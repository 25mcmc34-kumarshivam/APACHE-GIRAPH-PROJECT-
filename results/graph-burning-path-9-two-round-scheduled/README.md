# Verified two-round Graph Burning result

On 30 September 2026, the lab Giraph runner completed with the three
`part-*.txt` files from `datasets/graph-burning-path-9-two-round-scheduled/`
uploaded to the HDFS input directory below. Source vertices 2 and 8 were
marked for rounds 1 and 2 **inside those files**; no source list was typed
in the run command.

```bash
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_two_round_scheduled_input \
  /user/mca2025/giraph_learning/graph_burning_path9_two_round_scheduled_output
```

The actual readable HDFS output was
`/user/mca2025/giraph_learning/graph_burning_path9_two_round_scheduled_output/part-00000`.
The nine rows copied from the terminal are in `part-00000.txt` beside this
README. They match the local prediction. `NB -1` means the vertex was not
reached **within these two rounds**; it does not mean it could never burn.
The runner also keeps the raw Giraph output in the sibling directory ending
`.__giraph_raw`.

The first attempt to invoke the script directly returned `Permission
denied` because its executable bit was not set on the lab copy. Running
it with `bash` (as shown above) succeeded; no Java rebuild was needed.

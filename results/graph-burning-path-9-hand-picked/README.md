# Verified hand-picked Graph Burning result

On **6 October 2026 (client date)**, we ran the input-driven Giraph
computation on the nine-vertex path in
`datasets/graph-burning-path-9-hand-picked/`. The source sequence was
chosen by hand, not by the greedy or exact-search Python helper: vertex 1
in round 1, vertex 9 in round 2, and vertex 5 in round 3. The files were
split into three parts and uploaded to one HDFS input directory.

```bash
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/graph_burning_path9_hand_picked_input \
  /user/mca2025/giraph_learning/graph_burning_path9_hand_picked_output
```

YARN reported application `application_1790779476667_0001` as
`FINISHED / SUCCEEDED`. The actual readable HDFS output was
`/user/mca2025/giraph_learning/graph_burning_path9_hand_picked_output/part-00000`;
its nine rows are copied to `part-00000.txt` beside this README. They match
the hand calculation: vertices **4, 6, and 7** are `NB -1` after three
rounds. This shows that a legal but unoptimized source schedule need not
burn every vertex within the same round budget.

The lab PC's clock still displayed **30 September 2026 UTC** during this
6 October session, so its HDFS/YARN log timestamps are not reliable as
calendar dates until that clock is corrected. The Git commit and this
client-observed date identify when the follow-up was done. We did not
change the system clock during the experiment.

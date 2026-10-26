# Verified 120-node grid experiment

`python-preview/` contains the expected final `B`/`NB` file and eight
round-by-round vertex/edge tables for the [scheduled 120-node grid](../../datasets/grid-120-random-burning-seed-20261026/).
The source sequence `15:104:35:101:41:111:83:86` was random-but-eligible,
using seed `20261026`, not optimized. Python predicts 119 burned vertices;
vertex 85 is `NB -1` at the end of round 8.

On the lab PC, we uploaded the same four parts to
`/user/mca2025/giraph_learning/graph_burning_grid120_random_20261026_input`
and submitted a fresh Giraph job. Its readable output is
`/user/mca2025/giraph_learning/graph_burning_grid120_random_20261026_output/part-00000`.
The user copied that output to a local file and ran `diff -u` against the
lab Python `expected.tsv`: **exit code 0**, meaning all 120 final rows
matched. The result was **119 `B`, one `NB -1` (vertex 85)**. This verifies
the implementation for this specific input and random schedule; it does not
mean the sequence is optimal.

The eight lab-generated PNG/GraphML round previews are saved in
`lab-round-preview/`. The actual HDFS TSV remains on the lab server; its
copy into this repository is pending. The pictures are Python
visualizations, not Giraph's own output.

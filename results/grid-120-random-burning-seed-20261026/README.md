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

| Round | Lab PNG | Burned subgraph | State of every node | Burned-to-burned edges |
|---:|---|---|---|---|
| 1 | [PNG](lab-round-preview/round-01.png) | [GraphML](lab-round-preview/round-01-burned.graphml) | [nodes.tsv](lab-round-preview/round-01-nodes.tsv) | [edges.tsv](lab-round-preview/round-01-burned-edges.tsv) |
| 2 | [PNG](lab-round-preview/round-02.png) | [GraphML](lab-round-preview/round-02-burned.graphml) | [nodes.tsv](lab-round-preview/round-02-nodes.tsv) | [edges.tsv](lab-round-preview/round-02-burned-edges.tsv) |
| 3 | [PNG](lab-round-preview/round-03.png) | [GraphML](lab-round-preview/round-03-burned.graphml) | [nodes.tsv](lab-round-preview/round-03-nodes.tsv) | [edges.tsv](lab-round-preview/round-03-burned-edges.tsv) |
| 4 | [PNG](lab-round-preview/round-04.png) | [GraphML](lab-round-preview/round-04-burned.graphml) | [nodes.tsv](lab-round-preview/round-04-nodes.tsv) | [edges.tsv](lab-round-preview/round-04-burned-edges.tsv) |
| 5 | [PNG](lab-round-preview/round-05.png) | [GraphML](lab-round-preview/round-05-burned.graphml) | [nodes.tsv](lab-round-preview/round-05-nodes.tsv) | [edges.tsv](lab-round-preview/round-05-burned-edges.tsv) |
| 6 | [PNG](lab-round-preview/round-06.png) | [GraphML](lab-round-preview/round-06-burned.graphml) | [nodes.tsv](lab-round-preview/round-06-nodes.tsv) | [edges.tsv](lab-round-preview/round-06-burned-edges.tsv) |
| 7 | [PNG](lab-round-preview/round-07.png) | [GraphML](lab-round-preview/round-07-burned.graphml) | [nodes.tsv](lab-round-preview/round-07-nodes.tsv) | [edges.tsv](lab-round-preview/round-07-burned-edges.tsv) |
| 8 | [PNG](lab-round-preview/round-08.png) | [GraphML](lab-round-preview/round-08-burned.graphml) | [nodes.tsv](lab-round-preview/round-08-nodes.tsv) | [edges.tsv](lab-round-preview/round-08-burned-edges.tsv) |

The [lab expected final TSV](lab-round-preview/expected.tsv) is the file compared with Giraph on the lab PC; the [local generated expected TSV](python-preview/expected.tsv) is the reproducible pre-run prediction. `python-preview/` also contains `round-01` through `round-08` node and burned-edge tables, but no lab PNGs. The [experiment index](../../docs/EXPERIMENT-INDEX.md) maps this result to its precise four-part input.

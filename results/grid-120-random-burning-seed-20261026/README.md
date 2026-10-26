# Python prediction for the 120-node grid experiment

`python-preview/` contains the expected final `B`/`NB` file and eight
round-by-round vertex/edge tables for the [scheduled 120-node grid](../../datasets/grid-120-random-burning-seed-20261026/).
The source sequence `15:104:35:101:41:111:83:86` was random-but-eligible,
using seed `20261026`, not optimized. Python predicts 119 burned vertices;
vertex 85 is `NB -1` at the end of round 8.

**No Giraph result is recorded here yet.** The next step is to upload the
four `part-*.txt` files to HDFS, run `run_graph_burning_from_input.sh` using
a new output path, save the actual `part-00000`, and compare it against
`python-preview/expected.tsv`. Per-round GraphML and PNG can be generated
on the lab PC with `--networkx --png`; these are Python visualizations,
not Giraph's own output.

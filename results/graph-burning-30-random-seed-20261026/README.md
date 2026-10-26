# Python prediction for the 30-node random-source experiment

This folder currently contains **only local Python predictions** from
`scripts/show_burning_rounds.py` for
[`datasets/thirty-node-random-burning-seed-20261026/`](../../datasets/thirty-node-random-burning-seed-20261026/).
There is no verified Giraph output in this folder yet.

Four randomly selected eligible sources, using seed `20261026`, are
`4:27:12:15`. The Python program predicts 24 burned vertices and six
unburned vertices (`14,18,19,20,24,25`) after round 4. The
`python-preview/` directory contains `expected.tsv` and round-by-round
node and burned-edge tables. After the Giraph job runs, save its actual
output separately and use `diff -u` to compare it with `expected.tsv`.

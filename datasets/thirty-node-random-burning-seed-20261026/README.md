# 30-node undirected graph with a random, non-optimized burning schedule

This is the **same 30-vertex, 55-undirected-connection topology** as
[`../thirty-node-undirected-burning/`](../thirty-node-undirected-burning/),
split into the same three text parts. The only added field is the second
column, `source_round`, required by `BurningScheduleTextInputFormat`.

We used `scripts/prepare_random_burning_input.py` with four rounds and
integer seed `20261026`. It picked uniformly from the vertices that had
not burned **before** each round; it did not score coverage or search for a
short/optimal sequence. The generated sequence was:

| Round | Random eligible source |
|---:|---:|
| 1 | 4 |
| 2 | 27 |
| 3 | 12 |
| 4 | 15 |

`selection.json` records the seed and sequence. Only the three `part-*.txt`
files go into the Giraph HDFS input directory; `selection.json` and this
README are metadata. Input line `4 1 3:1 5:1 9:1` means vertex 4 is the
round-1 source and has the listed neighbours. A `0` in column two means
not chosen as a source; it may still burn by propagation.

Reproduce locally from the repository root (choose a **new** output path;
the script refuses to overwrite this committed dataset):

```bash
python3 scripts/prepare_random_burning_input.py \
  datasets/thirty-node-undirected-burning /tmp/thirty-node-random-20261026 \
  --rounds 4 --seed 20261026
python3 scripts/validate_burning_schedule.py /tmp/thirty-node-random-20261026
python3 scripts/show_burning_rounds.py /tmp/thirty-node-random-20261026
```

The [Python prediction](../../results/graph-burning-30-random-seed-20261026/python-preview/expected.tsv)
has 24 `B` vertices and six `NB -1` vertices (14, 18, 19, 20, 24, 25).
The lab Giraph job then ran on these exact three parts; its
[actual output](../../results/graph-burning-30-random-seed-20261026/giraph-actual.tsv)
matches the prediction (`diff` exit 0). See the [result record](../../results/graph-burning-30-random-seed-20261026/README.md).

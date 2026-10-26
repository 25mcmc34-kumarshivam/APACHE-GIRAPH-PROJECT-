# 120-node grid with a random, non-optimized burning schedule

The four `part-*.txt` files are the [same 120-node grid](../grid-120-unscheduled/)
with one extra **second column**: the ignition round (`0` if a vertex is
not a chosen source). The graph still has 218 undirected connections.
Only the `part-*.txt` files should be uploaded as HDFS input. `selection.json`
records how sources were picked; it is metadata, not a vertex file.

We used eight rounds and random seed `20261026`. The preparer chose one
uniformly random **eligible** vertex per round (not already burned before
that round). It did not maximize coverage or prove a minimum burning number.

| Round | Source |
|---:|---:|
| 1 | 15 |
| 2 | 104 |
| 3 | 35 |
| 4 | 101 |
| 5 | 41 |
| 6 | 111 |
| 7 | 83 |
| 8 | 86 |

Recreate into a new path:

```bash
python3 scripts/prepare_random_burning_input.py \
  datasets/grid-120-unscheduled /tmp/grid-120-scheduled \
  --rounds 8 --seed 20261026
```

The [Python preview](../../results/grid-120-random-burning-seed-20261026/python-preview/expected.tsv)
predicts **119 `B` and one `NB -1` (vertex 85)** after round 8. This is
only a prediction until the same input is run on the lab Giraph system and
the actual HDFS output is compared. Because the files were generated on a
Windows Python installation, the committed `.txt` files may have CRLF
line endings; the text reader accepts them, and comparison should be done
by rows or after normalizing line endings.

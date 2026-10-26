# Synthetic 120-node undirected grid, before source selection

`scripts/generate_grid_graph.py` generated a **10-row by 12-column** grid.
Vertex IDs are row-major: the top row is 1–12, the second row is 13–24,
and the bottom row is 109–120. A vertex connects to an existing neighbour
immediately above, below, left or right; there are no diagonal connections.
Each undirected connection is written at both endpoints with weight `1`.

Counts: **120 vertices**, **218 undirected connections** (436 adjacency
entries), **four parts** of 30 vertex lines each. The edge count is
`10×(12−1) + 12×(10−1) = 218`. `topology.json` records these parameters.
This is a reproducible **synthetic teaching graph**, not a downloaded social
network or a measured real-world dataset. It is larger than our earlier
30-node graph while its structure is easy to verify.

Regenerate it into a new path from the repository root:

```bash
python3 scripts/generate_grid_graph.py /tmp/grid-120-regenerated \
  --rows 10 --columns 12 --parts 4
```

The lines here have format `vertex neighbour:weight ...` and **do not**
contain burning-source rounds. Giraph's input-driven burning reader needs
the [scheduled version](../grid-120-random-burning-seed-20261026/), not
these original files.

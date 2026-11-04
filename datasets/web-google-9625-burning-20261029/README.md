# Web-Google 9,625-vertex Graph Burning input

This is a reproducible burning input derived from Stanford SNAP's
`web-Google.txt` edge list. The original file is a directed web graph with
875,713 vertices and 5,105,039 edges. It is not stored in this repository.

For the first lab-scale large-graph experiment, the converter kept source
IDs below `100000`, converted retained edges to an undirected adjacency
graph, removed self-loops/duplicates, and kept the largest connected
component. The resulting graph has **9,625 vertices and 14,511 undirected
edges**, split across four text parts.

The source sequence was selected uniformly at random from eligible vertices
with seed `20261104`; it was not greedy or optimized:

```text
35524:55197:63686:84985:3677:38948
```

Each `part-*.txt` record uses the scheduled Giraph format:

```text
vertex_id source_round neighbour_id:weight neighbour_id:weight ...
```

`selection.json` records the seed, number of rounds and selected sources.
Only the four `part-*.txt` files belong in the HDFS input directory;
`selection.json` is metadata.

The conversion program is [`convert_snap_edge_list.py`](../../scripts/convert_snap_edge_list.py),
followed by [`prepare_random_burning_input.py`](../../scripts/prepare_random_burning_input.py).

# Web-Google 348,087-vertex Graph Burning input

This is the larger Week 16 experiment derived from Stanford SNAP's directed
`web-Google.txt`. We kept source IDs below `500000`, converted the retained
edges to undirected adjacency, removed self-loops and duplicates, kept the
largest connected component, and split the result into eight parts.

The converted graph contains **348,087 vertices and 1,128,693 undirected
connections**. It is a real-data baseline, not an optimized burning input.
Eight eligible random sources were chosen with seed `20261105`:

```text
96901:113758:455241:73976:310174:473800:320304:118094
```

The `part-*.txt` records use the current Giraph format:

```text
vertex_id source_round neighbour_id:weight neighbour_id:weight ...
```

`selection.json` is metadata and must not be uploaded to HDFS. Only the
eight `part-*.txt` files form the HDFS input directory.

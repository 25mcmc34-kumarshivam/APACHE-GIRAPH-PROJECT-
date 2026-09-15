# Thirty-Node Multi-File Text Dataset

This directory contains one directed graph divided across three physical text
files. Giraph reads the directory as one logical input dataset.

## Format

```text
vertexId neighborId:weight neighborId:weight ...
```

Example: `5 1:1 10:1 11:1` means vertex 5 has weighted outgoing edges to
vertices 1, 10, and 11. All current weights are 1.

## Verified structure

- Files: 3
- Vertices: 30 (10 records per file)
- Directed edges: 79
- Duplicate vertex IDs: 0
- Referenced but undefined vertices: 0

Splitting a dataset into files does not split it into independent graphs.
Edges may point to vertices stored in any other part file.

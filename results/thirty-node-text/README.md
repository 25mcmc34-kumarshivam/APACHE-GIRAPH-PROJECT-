# Verified Thirty-Node Results

Dataset: [`../../datasets/thirty-node-text/`](../../datasets/thirty-node-text/)

All four results were produced by Giraph on 15 September 2026 using the same
HDFS directory containing three physical input files.

Validation:

- Output vertices: 30 for every computation
- Dataset edges: 79
- Sum of out-degrees: 79
- Sum of in-degrees: 79
- Highest PageRank: vertex 8, followed by vertex 6
- BFS source: vertex 1
- BFS maximum distance: 8 hops
- BFS unreachable vertices: none

The BFS output exactly matched the manually calculated levels recorded in the
Week 9 report.

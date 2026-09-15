# Verified Thirty-Node Results

Dataset: [`../../datasets/thirty-node-text/`](../../datasets/thirty-node-text/)

All five results were produced by Giraph on 15 September 2026 using the same
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
- Weighted shortest-path source: vertex 1
- BFS and weighted shortest-path outputs: identical for all 30 vertices

The BFS output exactly matched the manually calculated levels recorded in the
Week 9 report.

The calculation and interpretation are explained in the
[`BFS thirty-node walkthrough`](../../docs/BFS-THIRTY-NODE-WALKTHROUGH.md).

The equality of the two distance results was checked directly from HDFS with
`diff`. Exit code `0` confirmed that there was no difference. This is expected
because every edge in this dataset has weight `1`.

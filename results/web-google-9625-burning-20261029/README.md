# Verified 9,625-vertex Web-Google Graph Burning experiment

This experiment ran the input-driven Giraph Graph Burning computation on
the converted Web-Google subgraph in
[`datasets/web-google-9625-burning-20261029/`](../../datasets/web-google-9625-burning-20261029/).
The graph contains 9,625 vertices and 14,511 undirected edges. Six random,
eligible but non-optimized sources were scheduled:
`35524:55197:63686:84985:3677:38948`.

Python created the independent prediction in `python-preview/expected.tsv`.
Giraph ran on HDFS input
`/user/mca2025/giraph_learning/web_google_9625_burning_input` and wrote
`/user/mca2025/giraph_learning/web_google_9625_burning_output/part-00000`.
The copied [actual Giraph output](giraph-actual.tsv) has 9,625 rows and
matches the Python prediction exactly (`diff -u` exit code `0`).

Final result: **131 vertices burned** and **9,494 remained `NB -1`** after
six rounds. Six rounds were chosen as a first manageable test, not because
the graph requires six rounds and not because six is optimal. With `k`
source rounds, the first source can spread at most `k-1` hops by the end,
the second at most `k-2` hops, and the final source only ignites itself.
Therefore this run used maximum radii `5,4,3,2,1,0`. This is a correctness
check for this random schedule, not an optimization result; low coverage is
expected for a sparse large component under this short schedule.

| Evidence | File |
|---|---|
| Python prediction and six round state tables | [`python-preview/`](python-preview/) |
| Actual Giraph final output | [`giraph-actual.tsv`](giraph-actual.tsv) |
| Input and schedule | [`datasets/web-google-9625-burning-20261029/`](../../datasets/web-google-9625-burning-20261029/) |
| Converter test | [`test_convert_snap_edge_list.py`](../../tests/test_convert_snap_edge_list.py) |

# Reusable Giraph Scripts

Beginner-friendly teaching copies of every script, with detailed English and
Hinglish comments, are in [`learning-guides/`](learning-guides/README.md).
They explain variables, Bash syntax, safety checks, Giraph options, input
parsing, BFS, and diagram generation without making the operational scripts
harder to maintain.

## Text graph algorithm runner

`run_text_graph_algorithm.sh` runs the five algorithms currently used in the
project without repeatedly typing the complete `hadoop jar` command.

Supported names:

- `pagerank`
- `outdegree`
- `indegree`
- `bfs`
- `shortest-path`

Syntax:

```bash
./run_text_graph_algorithm.sh ALGORITHM INPUT OUTPUT [SOURCE_ID]
```

Example:

```bash
./run_text_graph_algorithm.sh shortest-path \
  /user/mca2025/giraph_learning/thirty_node_text_input \
  /user/mca2025/giraph_learning/thirty_node_shortest_from_1_output \
  1
```

The script checks commands, the shaded Giraph JAR, HDFS input, output-path
safety, and YARN availability before submitting a job. It always uses the
project's plain-text `LongDoubleFloatTextInputFormat`.

The runner was verified on the lab server on 16 September 2026 using the
weighted six-vertex dataset and BFS from source vertex 1. The produced output
matched the manually calculated hop distances.

HDFS output directories cannot be reused. Choose a new output path or remove
an old experimental output deliberately after confirming that it is no longer
needed.

## Other scripts

- `check_environment.sh` checks Java, Hadoop, HDFS, YARN, Git and Maven.
- `generate_graphviz_from_text.py` validates text graph parts and creates an
  exact Graphviz DOT diagram.
- `run_pagerank.sh` and `run_shortest_path.sh` are the earlier JSON-oriented
  scripts retained as part of the lab history.

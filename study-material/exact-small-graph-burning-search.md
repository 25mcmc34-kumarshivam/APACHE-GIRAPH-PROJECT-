# How the computer can choose Graph Burning sources (small graphs)

Until now, **we** supplied sequences such as `3:8:6`; Giraph told us when
each vertex first burned. The new
[`find_small_graph_burning_sequence.py`](../scripts/find_small_graph_burning_sequence.py)
does the reverse for a **small** graph: it tries possible source sequences
until it finds the shortest one that covers every vertex.

## Think of it as checking guesses

For a graph with vertices 1 through 6, the checker asks:

1. Can one chosen source burn everything in one round?
2. If not, can two sources burn everything in two rounds?
3. If not, can three sources burn everything in three rounds?

It starts with the smallest round count. For each count it checks possible
ordered choices. The first count with a valid sequence is the **minimum for
that small input**. Trying all possibilities is called exhaustive search.

The two key rules are:

- Source chosen in round `i` can reach a vertex at most `k-i` edges away by
  the end of round `k`. For three rounds, source 1 can reach distance 2,
  source 2 distance 1, and source 3 distance 0.
- A later source cannot have burned in an **earlier** round. It may be reached
  by fire in the *same* round it is chosen.

The program uses BFS internally to find edge-count distances. It ignores the
`:1` edge weights because Graph Burning here counts rounds/edges, not weighted
cost. It requires both directions of each edge to be present, since this is
an undirected graph experiment. Separate components are allowed.

## Run it without starting Hadoop

From the repository root, with Python 3:

```bash
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-path-9
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-star-7/graph.txt
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-disconnected-6/graph.txt
```

This script reads **local text files**, not HDFS. It needs no Maven build and
no YARN. It prints a source sequence; copy that sequence into the existing
Giraph runner if you want to verify per-vertex burn rounds on the lab setup.

On our three stored graphs, it returned:

| Graph | Exact minimum rounds | One sequence found |
|---|---:|---|
| Nine-node path | 3 | `3:7:9` |
| Seven-node star | 2 | `1:2` |
| Two disconnected three-node paths | 3 | `1:4:6` |

A graph can have several shortest sequences. Finding `3:7:9` does not make
our earlier verified path sequence `3:8:6` wrong; both take three rounds.
Likewise, `1:4:6` and our tested `2:5:4` each use three rounds on the two
separate paths. The printed sequences come from a **local Python search**;
only the earlier sequences have been checked in Giraph so far.

To run the script's own checks, use:

```bash
python3 -m unittest discover -s tests -p test_small_graph_burning_search.py -v
```

Why not use it on 30 or millions of vertices? The number of possible source
orders grows very quickly. The script refuses graphs larger than ten vertices
and stops if its search-state budget is exhausted. If it stops, it does **not**
claim an exact answer. Later we need a scalable heuristic or distributed
selection method for larger data. This is a reference checker, **not** the
final Giraph algorithm.

Formal background: [Bonato, Janssen and Roshanbin, *How to Burn a Graph*](https://math.ryerson.ca/~abonato/papers/Burning-IM-revised4.pdf)
and [Bessy et al., *Bounds on the Burning Number*](https://arxiv.org/abs/1511.06023).

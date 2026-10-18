# Eight-vertex graph for the limited-neighbour experiment

This is a small undirected teaching graph, divided into two text files. Read
both files together; every vertex is defined once, and every edge appears in
both directions. The `:1` is an edge weight from the older text-graph format.
This Python experiment checks it but does not use it to decide who burns.

```text
Edges: 1--2, 1--3, 1--7, 2--4, 4--5, 4--8, 5--6, 6--8
```

The input schedule is `schedule-1-4-6.txt`:

```text
1 1 2 3
2 4 5
3 6 -
```

Each row means `round  source  neighbours explicitly selected to ignite`.
Round 1: source 1 ignites vertices 2 and 3, but not adjacent vertex 7.
Round 2: source 4 ignites vertex 5, but not adjacent vertex 8. Round 3:
source 6 ignites only itself; `-` means no neighbours selected.

The three neighbour limits are 2, 1, and 0 because there are three rounds.
No program chose these vertices for us. The source sequence and its selected
neighbours were written by hand for an easily checked demonstration.

This **source-only limited-neighbour rule** is a proposed interpretation of
the 18 October team discussion. It is separate from the standard Graph
Burning rule used by our Java/Giraph experiments. See the
[complete study sheet](../../docs/WEEK-14-LIMITED-NEIGHBOUR-BURNING-STUDY.md)
before comparing their results.

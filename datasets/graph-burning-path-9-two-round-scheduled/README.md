# Two-round scheduled path: designed to test `NB -1`

This is the same nine-node undirected path as the complete test, but the
input marks vertex 2 for round 1 and vertex 8 for round 2. The second
column is the scheduled source round; `0` means no manual ignition.

```text
1--2--3--4--5--6--7--8--9
   ^                 ^
 round 1           round 2
```

At the end of round 2, fire from 2 has reached 1 and 3, and vertex 8 has
been ignited. Vertices 4, 5, 6, 7, and 9 have **not** burned yet. The
predicted readable output is:

```text
1  B   2
2  B   1
3  B   2
4  NB -1
5  NB -1
6  NB -1
7  NB -1
8  B   2
9  NB -1
```

Local prediction is not a Giraph result. Keep this dataset in its own HDFS
input directory and give its job a new HDFS output path. Do not modify or
overwrite the complete three-round example.

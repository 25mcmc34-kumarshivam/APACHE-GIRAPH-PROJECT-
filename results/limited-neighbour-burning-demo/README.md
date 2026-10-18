# Lab result for the Python limited-neighbour experiment

On 18 October 2026, `mca2025` ran the new Python simulator on the lab PC
using the two files in `datasets/limited-neighbour-burning-demo/graph-parts/`
and `schedule-1-4-6.txt`. The program exited with code 0. The resulting
local lab file was
`/home/mca2025/giraph_learning_limited_neighbour/week14/result-1-4-6.txt`.
Its eight rows matched the hand calculation exactly, byte for byte, and are
preserved in [result-1-4-6.txt](result-1-4-6.txt).

This was **not** a YARN, HDFS, or Giraph job. It was a local Python run on
the same Ubuntu lab computer. Therefore this result demonstrates the new
rule and the code path, not distributed performance.

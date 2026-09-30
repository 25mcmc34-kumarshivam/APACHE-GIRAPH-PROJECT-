# Graph Burning with the ignition schedule inside the input file

**Status, 30 September 2026:** The new input reader, computation, runner,
validator, formatter and nine-node example are in the repository. The local
Python tests pass. The lab Maven build succeeded and both new classes are in
the shaded JAR. The three input parts were uploaded to HDFS and validated
after reading them back. The **Giraph job run is still pending**;
the predicted table below must not be presented as a newly observed cluster
result until that run succeeds and is compared row by row.

This is a new variant, not a replacement for the earlier working
`LearningGraphBurningComputation` and `run_graph_burning.sh`. Keeping both
lets us compare the old command-line schedule with the new file-based one.

## The requested change

Previously a graph line had only an ID and outgoing neighbours:

```text
3 2:1 4:1
```

The operator also typed `3:8:6` on the command line. Now the second column
of each graph line says **which round selects that vertex as a new source**:

```text
3 1 2:1 4:1    # vertex 3 is chosen in round 1
8 2 7:1 9:1    # vertex 8 is chosen in round 2
6 3 5:1 7:1    # vertex 6 is chosen in round 3
5 0 4:1 6:1    # vertex 5 is not chosen; fire may still reach it
```

The real `.txt` files do **not** contain the explanatory `#` comments shown
above; each record is just `vertexId sourceRound neighbour:weight ...`.
`sourceRound=0` means not scheduled. Exactly one vertex must have `1`, one
must have `2`, and so on without missing rounds. We keep the same classical
one-new-source-per-round rule as last week. Multiple sources in one round
would be a different model and are rejected by this week's validator.

We deliberately use `0` for “not a new source” in the **input** and reserve
`-1` for “not burned by the end” in the **output**. Those are different
ideas: a vertex with input `0` may still burn through a neighbour.

## Readable output

Each result row has three tab-separated fields:

```text
vertexId    status    firstBurnRound
17          B         5
5           NB        -1
```

`B` means burned; the positive number tells **when it first burned**.
`NB -1` means not burned within the scheduled rounds. It is not an error
code or a negative burn time. The runner keeps the internal numeric Giraph
result in a separate HDFS path ending `.__giraph_raw` for debugging, and
creates the requested human-readable HDFS output path. Never report the
internal negative schedule values as burn rounds.

## The nine-node path example

`datasets/graph-burning-path-9-scheduled/` has three files. They describe
`1--2--3--4--5--6--7--8--9` and mark vertex 3 for round 1, vertex 8 for
round 2 and vertex 6 for round 3. Example record:

```text
3 1 2:1 4:1
```

The leftmost `3` is the ID. The following `1` is **the chosen-source
round**, not an edge weight. `2:1` and `4:1` are outgoing neighbours with
weights 1. Each undirected connection appears on both endpoint lines.
The graph is split across files, but one HDFS input directory supplies them
all to Giraph.

Manual prediction:

| Round | New source | Other newly reached vertices | First-burn result |
|---:|---:|---|---|
| 1 | 3 | none | 3→1 |
| 2 | 8 | 2, 4 from 3 | 2→2, 4→2, 8→2 |
| 3 | 6 | 1, 5, 7, 9 through earlier fire | 1→3, 5→3, 6→3, 7→3, 9→3 |

The local validator predicts:

```text
1  B  3
2  B  2
3  B  1
4  B  2
5  B  3
6  B  3
7  B  3
8  B  2
9  B  3
```

To test `NB -1`, use a separate version of this same path with only vertex
2 scheduled in round 1 and vertex 8 in round 2. By the end, only 1, 2, 3
and 8 have burned; vertices 4, 5, 6, 7 and 9 should be `NB -1`. **Do not
modify the committed three-round example in place**; keep each test as a
separate input directory and output path.

## What the new files do

| File | Purpose and important logic |
|---|---|
| `src/BurningScheduleTextInputFormat.java` | Parses `vertexId sourceRound neighbour:weight...`. Creates the same Long/Double/Float vertex types as our earlier algorithms. Stores `-sourceRound` as the initial vertex value. `0` remains zero. A negative value is **pending scheduled ignition**, not an output burn round. |
| `src/LearningGraphBurningFromInputComputation.java` | Reads each vertex's own pending round. At Giraph superstep 0 (human round 1), a `-1` source burns. Messages carry the next round to neighbours. On first burn the vertex value changes to positive first-burn round. Vertices do not halt before the last round, because a later source might have no incoming message. |
| `scripts/validate_burning_schedule.py` | Reads all input parts (or standard input from HDFS); checks unique vertex IDs, edge syntax/endpoints, reverse edges, exactly one source for each round, and sources not already burned *before* selection. It predicts burn rounds locally using BFS. The runner uses its `--rounds-only` mode to derive the last round automatically from the file. This is a local preflight check, not a distributed algorithm. |
| `scripts/format_burning_output.py` | Converts raw `vertexId numericValue` from Giraph to `vertexId B round` for a positive value, or `vertexId NB -1` for zero/negative value. Rejects malformed or fractional burn rounds. |
| `scripts/run_graph_burning_from_input.sh` | Checks Java/Hadoop/Python, JAR, HDFS input/output and YARN; validates the graph; passes the derived total-round count (but **no source IDs**) to Giraph; writes the readable result into a new HDFS output directory. It keeps the raw numeric output separately as evidence. |
| `tests/test_input_driven_burning.py` | Nine new local tests for the schedule, expected path values, `NB -1`, malformed/repeated/missing rounds, reverse edges and formatter. Eleven older Graph Burning tests still pass, making 20 tests total in the local suite. |

### Why store a negative round inside the Java vertex value?

Giraph does not give one vertex direct access to all input records. Each
vertex needs to carry its own schedule until its selected round. The
existing `DoubleWritable` vertex value can temporarily encode it:

- `-3.0` means “this vertex has not burned yet; select it in round 3.”
- `0.0` means “not selected and not yet burned.”
- `2.0` means “this vertex first burned in round 2.”

When a vertex burns because a neighbour reaches it earlier, its value
becomes positive, so it does not ignite a second time later. The validator
rejects a source scheduled for a round **after** it was already burned;
arrival in the same round is allowed, matching last week's star example.
The positive final value is then reformatted for the user.

### Why is `totalRounds` still passed as a `-ca` setting?

The sources are **not** passed by command line anymore. The runner reads
the input file first, finds the largest source round and checks that all
earlier rounds have one source. It passes only that **number of rounds** to
the Giraph class so it knows when to stop. Without it, Giraph vertices
cannot know from their own local records when every other vertex's schedule
ends. This is a teaching implementation: the local full-input preflight
would be a bottleneck for a truly huge dataset. A later design could use a
Giraph aggregator or separate metadata for scalable execution.

## Repeatable local checks, before the lab run

From the repository root:

```bash
python3 scripts/validate_burning_schedule.py datasets/graph-burning-path-9-scheduled
python3 -m unittest discover -s tests -p 'test_*.py'
bash -n scripts/run_graph_burning_from_input.sh
```

On 30 September the validator printed 9 vertices, 8 undirected connections,
3 scheduled rounds, sources `3:8:6`, and the predicted table above. All 20
Python tests and the Bash syntax check passed locally. Separately, the lab
Maven build succeeded, and the shaded JAR contains both new classes. **None
of these checks proves a YARN job completed or the output is correct.**

## Lab run checklist (not yet verified)

1. As `hduser`, confirm HDFS/YARN are running and `yarn node -list` shows
   one healthy `RUNNING` node. Do not start a duplicate NodeManager if one
   is already active.
2. As `mca2025`, copy the two new Java files into
   `$HOME/giraph/giraph-examples/src/main/java/org/apache/giraph/examples/`
   and place the three new scripts together under `$HOME/giraph/`.
3. Build from `$HOME/giraph` with the same working Maven profile used in
   earlier experiments. Check the new two `.class` files in the shaded JAR.
   **Completed on 30 September;** the build summary is saved under `results/`.
4. Upload **only** the three `part-*.txt` input files into a new HDFS
   directory. Do not upload the dataset README as graph input.
   **Completed on 30 September:** HDFS read-back showed all three parts
   and the expected `3:8:6` schedule.
5. Run `bash "$HOME/giraph/run_graph_burning_from_input.sh" INPUT OUTPUT`
   with a new output name. No `3:8:6` argument is required.
6. Inspect `OUTPUT/part-00000`; compare all nine rows to the prediction.
   Also inspect `OUTPUT.__giraph_raw/part-m-*` if a value looks wrong.
7. Only after success, copy the actual HDFS result into `results/`, record
   the YARN application ID/build result, and update the Week 11 report.

### Known limits and honest presentation

This version is for the existing **one-source-per-round, undirected**
Graph Burning model. It has not yet been run on the lab server. It does not
automatically select the sources, change the mathematical model, or solve
the recurring NodeManager problem. The new preflight scans the full input
locally and is meant for the current teaching datasets, not a scalability
benchmark. A later extension could allow multiple simultaneous first-round
sources, but that needs an explicit rule and new tests before we claim it.

# Week 15 — code with comments (learning copy, not executable)

This is the **annotated-code track**. The tested programs stay in [`scripts/`](../../scripts/) and [`src/`](../../src/). The snippets below explain their actual logic with extra comments; do not paste isolated snippets over the working files. For a story-like explanation with no coding background, read [BABY-LEVEL-HINGLISH.md](BABY-LEVEL-HINGLISH.md).

## 1. Generate the 120-node topology

Runtime file: [`generate_grid_graph.py`](../../scripts/generate_grid_graph.py).

```python
for row in range(rows):                    # 0..9 for a 10-row grid
    for column in range(columns):          # 0..11 for a 12-column grid
        vertex = row * columns + column + 1
        # +1 because graph IDs start at 1, while Python indexes start at 0.
        neighbours = []
        if row > 0:                         # Not on top border: an UP neighbour exists.
            neighbours.append(vertex - columns)
        if row + 1 < rows:                  # Not on bottom border: a DOWN neighbour exists.
            neighbours.append(vertex + columns)
        if column > 0:                      # Not on left border: a LEFT neighbour exists.
            neighbours.append(vertex - 1)
        if column + 1 < columns:            # Not on right border: a RIGHT neighbour exists.
            neighbours.append(vertex + 1)
        graph[vertex] = sorted(neighbours)  # Dictionary: node ID -> adjacent node IDs.
```

For node 1, only right node 2 and down node 13 exist. For node 14 (row 2, column 2 in human counting), neighbours are 2, 13, 15 and 26. Each connection appears at both ends. `sum(map(len, graph.values())) // 2` divides the 436 adjacency entries by two, giving 218 undirected edges. `split_parts` uses `start = index * len(vertices) // part_count` and `end = (index+1) * len(vertices) // part_count`: four equal ID ranges of 30 lines. Splitting the *files* does not disconnect the graph.

The generator refuses an existing output path to avoid overwriting an earlier experiment. `topology.json` stores dimensions/counts for humans; it is not vertex input.

## 2. Choose a reproducible but **non-optimized** schedule

Runtime file: [`prepare_random_burning_input.py`](../../scripts/prepare_random_burning_input.py).

```python
rng = random.Random(seed)            # Own RNG: same seed + graph => same choice sequence.
chosen = {}                          # round_number -> source_vertex, initially empty.
distances = {}                       # already chosen source -> shortest-hop map.
for round_number in range(1, rounds + 1):
    eligible = [
        vertex for vertex in sorted(graph)  # Sorted IDs make seeded runs reproducible.
        if vertex not in chosen.values()    # Never choose the same source twice.
        and all(
            previous_round + distances[previous_source].get(vertex, float("inf"))
            >= round_number                # Earlier fire must NOT have burned it before now.
            for previous_round, previous_source in chosen.items()
        )
    ]
    source = rng.choice(eligible)           # Random choice; NO coverage/degree score here.
    chosen[round_number] = source
    distances[source] = distances_from(graph, source)  # BFS hop distances for next check.
```

`previous_round + distance` is the earliest arrival from an earlier source. `< round_number` would mean it burned **before** the new ignition and is invalid. `>=` allows arrival in the same round. `float("inf")` means unreachable. `random.Random(seed)` does not optimize; it only makes this particular experiment repeatable. For seed `20261026`, sources were `15:104:35:101:41:111:83:86`.

`prepare_parts` inserts the source round after each ID. It leaves all neighbours and weights unchanged, then calls `parse_lines` again and asserts the graph equals the original. It writes `selection.json` for provenance, **not** HDFS input.

## 3. Validate input and independently predict final rounds

Runtime file: [`validate_burning_schedule.py`](../../scripts/validate_burning_schedule.py).

`parse_lines` produces two dictionaries: `graph[vertex] = set(neighbours)` and `sources[round] = vertex`. It rejects duplicate vertex IDs, two sources in one round, missing rounds, undefined neighbours and missing reverse edges. That is why the directory must contain **only** the intended `part-*.txt` files: unrelated `.txt` files might be parsed as vertices.

```python
distances = {source: 0}                    # Source is zero edges from itself.
queue = deque([source])                   # BFS queue: visit shortest-hop layers in order.
while queue:
    vertex = queue.popleft()               # Take next discovered vertex.
    for neighbour in graph[vertex]:
        if neighbour not in distances:     # First visit gives shortest unweighted route.
            distances[neighbour] = distances[vertex] + 1
            queue.append(neighbour)
```

This is *unweighted* BFS, even though input edges say `:1`. It counts how many edges fire must traverse. For each vertex, `predicted_rounds` computes every source's arrival as `source_round + hop_distance`, takes the minimum, and writes `-1` if the earliest arrival would be **after** round 8. Thus it can predict final answers without using Giraph or the iterative preview. It does not find an optimal sequence.

## 4. Python round-by-round preview

Runtime file: [`show_burning_rounds.py`](../../scripts/show_burning_rounds.py).

```python
burned = {}                               # vertex -> first round in which it burned.
frontier = set()                          # ONLY vertices newly burned in previous round.
for round_number in range(1, max(sources) + 1):
    source = sources[round_number]         # Fixed by input. Preview does not choose it.
    reached_from_old_fire = set().union(
        *(graph[vertex] for vertex in frontier)
    ) if frontier else set()               # Round 1: empty frontier, no spread yet.
    newly = (reached_from_old_fire | {source}) - burned.keys()
    # | is set union: neighbours reached OR this round's new source.
    # - removes nodes burned in earlier rounds; do not assign a new first round.
    burned.update({vertex: round_number for vertex in newly})
    frontier = newly                       # They spread NEXT round, not immediately.
```

`write_text_files` writes `expected.tsv` for final comparison and, for each round, a node-state and burned-edge table. A burned-edge table is the **induced subgraph**: original edges whose two endpoints are already burned. It does not tell us the unique edge through which fire travelled.

`write_networkx_files` uses `nx.Graph()` for the full graph and `full.subgraph(cumulative).copy()` for the burned induced subgraph. `nx.write_graphml` saves a reusable graph file. `matplotlib.use("Agg")` means PNGs can be saved over SSH without opening a GUI. Colours: blue current source, orange other newly burned, yellow previously burned, grey still unburned. The drawing is a *visual aid*, not Giraph's output or the correctness check. On a 120-node spring layout labels may overlap; use TSVs for exact IDs.

The program also compares its iterative result with `predicted_rounds`, the BFS-distance method. That is an internal Python self-check. The **separate** Giraph comparison is `diff -u` after the job.

## 5. Java reader and Giraph computation

Runtime files: [`BurningScheduleTextInputFormat.java`](../../src/BurningScheduleTextInputFormat.java) and [`LearningGraphBurningFromInputComputation.java`](../../src/LearningGraphBurningFromInputComputation.java).

```java
String[] tokens = line.split("\\s+");   // Split a line on spaces/tabs.
long vertexId = Long.parseLong(tokens[0]); // First column: node ID.
int sourceRound = Integer.parseInt(tokens[1]); // Second: 0 or ignition round.
// tokens[2..] each have neighbourId:weight and become Giraph Edge objects.
vertex.initialize(new LongWritable(vertexId),
    new DoubleWritable(-sourceRound), edges);
// Negative value preserves a future ignition round inside the vertex.
// Zero = never selected as a source. Positive value is assigned after burning.
```

```java
long currentRound = getSuperstep() + 1;   // Giraph superstep 0 represents round 1.
if (storedValue <= 0) {                   // Already-positive vertices keep first burn round.
    double firstArrival = Double.MAX_VALUE; // Sentinel: no fire reached this node yet.
    for (DoubleWritable message : messages) {
        firstArrival = Math.min(firstArrival, message.get());
    }
    if (storedValue == -currentRound) {   // This input line schedules ignition now.
        firstArrival = Math.min(firstArrival, currentRound);
    }
    if (firstArrival != Double.MAX_VALUE) {
        vertex.getValue().set(firstArrival); // Record first burn round permanently.
        if (currentRound < totalRounds) {
            // Send next-round arrival to each neighbour. Giraph delivers messages
            // in the NEXT superstep, so there is no same-round second hop.
            for (Edge<LongWritable, FloatWritable> edge : vertex.getEdges()) {
                sendMessage(edge.getTargetVertexId(),
                    new DoubleWritable(currentRound + 1));
            }
        }
    }
}
if (currentRound >= totalRounds) vertex.voteToHalt(); // End after last round.
```

`totalRounds` comes from the runner's validated input, not from a typed source list. A future source must stay active until its round even if it received no earlier message. Edge weights are parsed as `FloatWritable` for format compatibility but are not used in this computation.

## 6. Shell runner, formatter and comparison

Runtime files: [`run_graph_burning_from_input.sh`](../../scripts/run_graph_burning_from_input.sh), [`format_burning_output.py`](../../scripts/format_burning_output.py).

- `set -euo pipefail`: stop on failed commands, missing variables and a failing pipeline. This prevents a broken HDFS read from being reported as success.
- `INPUT_PATH="$1"`, `OUTPUT_PATH="$2"`: first/second command arguments are **HDFS paths**, not Windows or Linux-local files. Quote variables to preserve spaces and exact values.
- `RAW_PATH="${OUTPUT_PATH}.__giraph_raw"`: Giraph writes its numeric internal state there first. Do not mistake it for the readable final result.
- `hdfs dfs -test -e`: verify input exists; refuse to overwrite an existing output/raw path.
- `yarn node -list`: require a `RUNNING` worker. Zero nodes means restart/check YARN before submitting.
- `hdfs dfs -cat "${INPUT_PATH}/*.txt" | python3 ... --stdin --rounds-only`: stream all HDFS input parts into validator and obtain the number of rounds. The quoted HDFS glob is expanded by HDFS, not the local shell.
- `hadoop jar ... -vif ... -vip ... -vof ... -op ... -w 1`: submit Java computation; `-vif` reader class, `-vip` HDFS input, `-vof` output format, `-op` fresh HDFS output, `-w 1` one Giraph worker.
- `hdfs dfs -cat RAW/part-m-* | python3 format_burning_output.py | sort -n | hdfs dfs -put - OUTPUT/part-00000`: stream numeric result through formatter, sort by numeric vertex ID and save readable HDFS result. `-` after `-put` means standard input.
- Formatter: numeric value `>0` becomes `B round`; value `<=0` becomes `NB -1`. It rejects malformed/non-finite values.
- `diff -u expected.tsv actual.tsv`: empty output **and exit code 0** means every corresponding final line matched. Use `echo $?` immediately after `diff`, before another command changes the exit code.

To see *how the commands moved data* rather than only their syntax, use the [weekly work report](../../weekly-reports/2026-10-29-week-15.md#repeat-the-120-node-practical-yourself).

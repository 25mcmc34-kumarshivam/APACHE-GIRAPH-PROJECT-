# Limited-neighbour burning: our Python experiment (18 October 2026)

We had already run **standard Graph Burning** on Giraph. On 18 October, our
team discussed a different rule based on the notebook example: for a chosen
sequence of three sources such as **1, 4, 6**, let the first source burn at
most **two** of its direct neighbours, the second at most **one**, and the
third **none** (it only burns itself). We wrote a short Python program so we
could see every choice and result clearly before changing any Giraph code.

The notebook's notation needs care. In the standard definition,
`N_2(1)` means **all vertices at graph distance at most two from vertex 1**.
It does *not* mean “pick at most two direct neighbours.” The original
[Graph Burning paper](https://arxiv.org/html/1507.06524v1) defines that
closed neighbourhood and its covering formula. Here we call our experiment
**source-only limited-neighbour burning** so nobody mistakes it for the
standard formula. The source-only and exact-neighbour choices below are our
explicit implementation assumptions, not a claim that Sir has approved every
detail of the model.

## The exact rule used in this experiment

Suppose the schedule has `k` rounds. In round `r` (starting at 1):

1. Choose one source vertex written in the schedule. It must still be unburned.
2. That source burns in round `r`.
3. The schedule may name **at most `k-r` unburned, directly adjacent vertices**
   for that source to ignite in the same round. We list these neighbours
   explicitly. The program does **not** choose them by greedy search, random
   selection, or vertex ID.
4. Vertices burned in older rounds stay burned but **do not spread again**.
   This is a source-only teaching model. It is the major difference from
   standard Graph Burning, where old fire continues to spread.
5. A vertex's output round is the first round in which it burns. Any vertex
   still untouched after round `k` gets `NB -1`.

For `k=3`, the limits are `3-1=2`, `3-2=1`, and `3-3=0`. “At most” matters:
the source may choose fewer than its limit. The limit counts **selected direct
neighbours**, not the source itself, not hops, and not total graph degree.

### Hinglish mein seedha matlab

Teen rounds hain. Pehle source ke paas do direct neighbours ko jalane ki
maximum permission hai; doosre ke paas ek; teesra sirf khud jalega. Kaunse
neighbours jalenge, woh hum schedule mein khud likhte hain. Jo pehle round
mein jal chuka hai woh next round mein apne aap aage fire **nahin** failata.
Yeh hamara naya practice model hai; purana Giraph wala standard burning
algorithm alag hai.

## The graph and the chosen schedule

The graph is in two files, not one. Python reads both `.txt` files in
[`datasets/limited-neighbour-burning-demo/graph-parts/`](../datasets/limited-neighbour-burning-demo/graph-parts/).
Together they define these eight vertices and edges:

```text
1--2, 1--3, 1--7, 2--4, 4--5, 4--8, 5--6, 6--8
```

This edge list is the precise graph definition; each `--` means a direct,
undirected connection.
The actual input lines are:

```text
# part-01.txt
1 2:1 3:1 7:1
2 1:1 4:1
3 1:1
4 2:1 5:1 8:1

# part-02.txt
5 4:1 6:1
6 5:1 8:1
7 1:1
8 4:1 6:1
```

For example, `1 2:1 3:1 7:1` defines vertex 1 and its three neighbours.
The `:1` weights keep our earlier Giraph-style text format; this simulator
ignores weights because only adjacency matters. We repeat an undirected edge
on both endpoint lines: `1 2:1` and `2 1:1`. The program rejects a missing
reverse edge, undefined vertex, repeated vertex, self-loop, or invalid value.

The [schedule](../datasets/limited-neighbour-burning-demo/schedule-1-4-6.txt)
is separate from the graph:

```text
# round  source  selected_direct_neighbours
1 1 2 3
2 4 5
3 6 -
```

The first `1` on the first data line is the **round number**; the second `1`
is the **source vertex ID**. The `2 3` are the exact neighbours selected.
The `-` on the last line means “choose no neighbours.” It is **not** a
negative vertex. The schedule was picked by hand, not optimized.

We deliberately gave source 1 **three** graph neighbours but selected only
two. Vertex 7 tests that the limit really works. Likewise source 4 has
neighbours 2, 5, and 8 but chooses only 5. Vertex 8 tests that an unchosen
neighbour remains unburned even when it touches burned vertices.

## Calculate the answer by hand before running code

| Round | Source | Limit | Newly burned | Burned so far | Why |
| --- | ---: | ---: | --- | --- | --- |
| 1 | 1 | 2 | 1, 2, 3 | 1, 2, 3 | Source 1 selects 2 and 3; it does not select 7. |
| 2 | 4 | 1 | 4, 5 | 1, 2, 3, 4, 5 | Source 4 selects 5; it does not select 8. |
| 3 | 6 | 0 | 6 | 1, 2, 3, 4, 5, 6 | Source 6 has no neighbour allowance. |

There are eight graph vertices, and six burned. Vertices 7 and 8 remain
unburned. Being adjacent to a burned vertex does **not** automatically burn
them in this particular model.

This also makes the difference from the old Java/Giraph rule concrete. Under
**standard** Graph Burning on this same graph and source order, fire from 1
would reach *all* its neighbours, including 7, in round 2; fire from 4
would reach 8 in round 3. Standard burning would cover all eight vertices
by round 3. That is a manual comparison, **not** a second measured lab run.

```text
vertex  status  first_burn_round
1       B       1
2       B       1
3       B       1
4       B       2
5       B       2
6       B       3
7       NB      -1
8       NB      -1
```

`B` means burned, `NB` means not burned when the scheduled rounds end, and
`-1` is a clear numeric marker for “no burn round.” It does not mean the
vertex burned in a negative round.

## What each Python function does

The working program is
[`scripts/simulate_limited_neighbour_burning.py`](../scripts/simulate_limited_neighbour_burning.py).
The code has comments at the decisions that matter. Read it in this order:

1. **`read_graph(path)`**: if `path` is a directory, it sorts and opens every
   `.txt` part. Each line is split by spaces. The first value becomes the
   vertex ID. Every `neighbour:weight` token becomes an entry in a `set` of
   adjacent IDs. A Python `set` prevents duplicates and makes membership
   checks easy. After reading all parts, it checks that each neighbour has
   its own vertex line and the reverse edge exists. It returns a dictionary
   like `{1: {2, 3, 7}, 2: {1, 4}, ...}`.
2. **`read_schedule(path)`**: each non-comment line yields `(source,
   chosen_neighbours)`. It demands rounds `1, 2, ..., k` in that order.
   Our three entries become `[(1,[2,3]), (4,[5]), (6,[])]`. The empty list
   is the meaning of `-`.
3. **`simulate(graph, schedule)`**: creates `first_burn`, a dictionary with
   every vertex initially set to `-1`. In each round it computes `k-r`,
   rejects too many chosen neighbours, non-adjacent IDs, a repeated or
   already-burned source, and a neighbour already burned. It then sets the
   source and its chosen neighbours to that round number. Its `trace` keeps
   the round, source, limit, newly burned IDs, and total burned count.
4. **`result_lines(first_burn)`**: sorts vertex IDs numerically and turns a
   value such as `{7: -1}` into `7 NB -1` for a readable result.
5. **`main()`**: reads the command-line options, calls the functions, prints
   the round trace and final table. If `--output` is given, it creates a
   **new** result file. It refuses to overwrite a previous result, so use a
   new filename for another experiment.

The test file
[`tests/test_limited_neighbour_burning.py`](../tests/test_limited_neighbour_burning.py)
checks the eight-vertex result and the limits, rejects a non-neighbour and
an already-burned source, verifies that unchosen vertices do not ignite,
and checks a bad one-way graph edge. These tests help catch our coding
mistakes; they do not prove that this is the faculty's intended rule.

### Hinglish code-reading note

`graph` dictionary mein har node ke direct neighbours ka set hai.
`schedule` list batati hai round-wise *kaunsa source* aur *exactly kaunse*
neighbours choose kiye. `first_burn` dictionary start mein sab ke liye
`-1` rakhti hai. Loop har round mein limit `k-r` nikalta hai, selected IDs
ko check karta hai, phir sirf unhi nodes ki value us round se badalta hai.
`trace` se hum dekh sakte hain ki har step par kitne nodes naye jale.

## The actual sequence of work and commands

1. We kept the existing Java/Giraph files unchanged. The new rule is short
   enough to try locally in Python before attempting any distributed
   implementation.
2. We made two graph parts and one hand-written schedule under
   `datasets/limited-neighbour-burning-demo/`. Splitting the graph does not
   split the *logical* graph: the parser reads both parts before simulation.
3. We wrote the Python simulator and seven tests. On the Windows repository
   checkout, this command passed all seven tests:

   ```powershell
   python -m unittest discover -s tests -p 'test_limited_neighbour_burning.py' -v
   ```

4. We ran the program locally to compare it with the hand calculation:

   ```powershell
   python scripts/simulate_limited_neighbour_burning.py --graph datasets/limited-neighbour-burning-demo/graph-parts --schedule datasets/limited-neighbour-burning-demo/schedule-1-4-6.txt
   ```

5. We verified SSH login to the lab PC for **both** `mca2025` and `hduser`.
   Only `mca2025` was needed for this experiment. We transferred the four
   new input/program files to
   `/home/mca2025/giraph_learning_limited_neighbour/week14/`. We did not
   copy passwords or the repository `.env` file to that folder.
6. As `mca2025` on Ubuntu, the actual run was equivalent to:

   ```bash
   python3 "$HOME/giraph_learning_limited_neighbour/week14/simulate_limited_neighbour_burning.py" \
     --graph "$HOME/giraph_learning_limited_neighbour/week14/graph-parts" \
     --schedule "$HOME/giraph_learning_limited_neighbour/week14/schedule-1-4-6.txt" \
     --output "$HOME/giraph_learning_limited_neighbour/week14/result-1-4-6.txt"
   ```

   `python3` runs the script. `--graph` points to a **directory**, so both
   graph-part files are read. `--schedule` points to the manually chosen
   round/vertex list. `--output` saves the final table. No `hadoop jar`,
   `mvn`, `hdfs`, or `yarn` command is necessary for this local Python run.
7. The lab program exited successfully and printed the same round trace and
   all eight rows as our hand calculation. The saved lab result matched the
   expected text **byte for byte**. We copied those eight rows into
   [`results/limited-neighbour-burning-demo/result-1-4-6.txt`](../results/limited-neighbour-burning-demo/result-1-4-6.txt).

## What this establishes—and what it does not

We have a working, explained Python experiment for a **source-only cap on
directly chosen neighbours**. It shows that the limits `2,1,0` are obeyed,
including two vertices deliberately left unburned. We have **not** shown
that this cap is the same as the notebook's `N_2, N_1, N_0` notation: in
published Graph Burning that notation counts **hop distance**, not the
number of picked neighbours. We have also **not** implemented this new rule
on Giraph or claimed a distributed speedup. For the 22 October meeting we
should show Sir the small example and ask whether earlier fires should keep
spreading and whether he wants the cap to apply to each source or each
burned vertex. Those answers would change the algorithm.

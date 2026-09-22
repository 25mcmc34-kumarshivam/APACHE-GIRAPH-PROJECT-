# Graph Burning and Diffusion Models

## Why we are studying this

Our project studies distributed graph algorithms for social-network problems.
Graph burning and diffusion models ask a common question: **if something starts
at one or more vertices, how does it spread through the network over time?**
The “something” may represent information, influence, a rumour, product
adoption, malware, fire, or infection.

The picture shown in the meeting—one burning vertex followed by its connected
vertices burning—represents a time-based spreading process. The important part
is the rule used to decide when a neighbour changes state. Different rules give
different models.

## First distinction: problem, process and model

- A **graph** contains vertices (people/computers/locations) and edges
  (friendships/connections/contact routes).
- A **state** records whether a vertex is unburned, active, susceptible,
  infected, recovered, etc.
- A **round/time step** is one synchronized update of all vertices.
- A **seed/source** is a vertex where spreading starts.
- A **diffusion model** defines the activation rule.
- An **optimization problem** asks which seeds should be chosen to achieve an
  objective, such as maximum influence or minimum completion time.

## 1. GB — Graph Burning

Graph Burning is a deterministic, discrete-time model introduced by Bonato,
Janssen and Roshanbin. It is not ordinary BFS, although fire propagation from
one source resembles BFS layers.

At every round:

1. Choose one new unburned vertex as a fire source.
2. Fire from vertices already burning spreads to their unburned neighbours.
3. A burned vertex remains burned permanently.

If sources are `x1, x2, ..., xk`, source `x1` has the most time to spread,
`x2` has one less round, and `xk` is ignited only in the final round. The
sequence is a **burning sequence** if the entire graph is burned after `k`
rounds. The minimum possible `k` is the **burning number**, written `b(G)`.

Equivalent coverage condition:

```text
V(G) = N[k-1](x1) union N[k-2](x2) union ... union N[0](xk)
```

`N[r](x)` means every vertex within graph distance `r` of `x`.

### Small path example

For the path `1—2—3—4—5—6—7—8—9`, use three sources:

```text
Round 1: ignite 3
Round 2: fire from 3 reaches 2 and 4; ignite 8
Round 3: fire reaches 1, 5, 7 and 9; ignite 6
```

All nine vertices are burned in three rounds. For a path with `n` vertices,
the burning number is `ceil(sqrt(n))`, so `b(P9)=3`.

### What must be implemented separately

There are two different tasks:

- **Simulation:** given a source sequence, calculate each vertex's burn round.
- **Optimization:** find the shortest possible source sequence and therefore
  the burning number.

Simulation is straightforward and suitable for our first Giraph program.
Finding the optimum is computationally difficult: the graph-burning decision
problem is NP-complete even for restricted graph classes. Therefore, after the
simulator we should implement and compare practical heuristics rather than
claiming that a heuristic always finds the exact burning number.

## 2. ICM — Independent Cascade Model

ICM is probabilistic. Start with one or more active seed vertices. When vertex
`u` first becomes active, it receives **one chance** to activate each currently
inactive neighbour `v`. The attempt succeeds with edge probability `p(u,v)`.
Whether one edge succeeds is independent of other attempts. An activated
vertex stays active, but it does not repeatedly retry a failed neighbour.

Example: if `p(1,2)=0.3`, activation of vertex 1 does not guarantee activation
of vertex 2. Repeating the same experiment with a different random seed may
produce a different cascade. Results are normally reported as averages over
many Monte Carlo runs.

Use cases include viral marketing, information sharing, recommendation spread
and influence maximization.

## 3. LTM — Linear Threshold Model

LTM is based on accumulated social pressure. Each inactive vertex `v` has a
threshold `theta(v)`, commonly between 0 and 1. Each incoming neighbour `u`
contributes influence weight `w(u,v)`. Vertex `v` activates when:

```text
sum of weights from active incoming neighbours >= theta(v)
```

Unlike ICM, several neighbours can combine their influence. For example, if a
vertex has threshold `0.6`, contributions `0.2` and `0.3` are insufficient,
but adding another contribution `0.2` activates it because the total is `0.7`.

This model suits collective adoption, peer pressure, joining a movement, or
adopting a technology after enough contacts have adopted it.

## 4. SIR — Susceptible, Infected, Recovered/Removed

Each vertex is in one of three states:

- **S — Susceptible:** can become infected.
- **I — Infected:** can infect susceptible neighbours.
- **R — Recovered/Removed:** no longer infectious and normally cannot be
  infected again in the basic model.

At each step, infection can cross an `S-I` edge with probability `beta`, and an
infected vertex can recover with probability `gamma`. Unlike GB, IC and LT,
activation is not necessarily permanent: an infected vertex later moves to R.
SIR is used for epidemics, malware propagation and other processes where an
active infectious period ends.

## 5. What does “LTIDT” mean?

`LTIDT` was not found as a standard graph-spreading or social-network diffusion
model acronym in the original and survey literature checked for this note. We
must not invent an expansion. Possible explanations are:

- the faculty listed **LT** and **IDT** as two separate items;
- it was written with a hyphen or different spelling;
- it is an acronym defined in a particular paper or slide;
- it may have referred to a discrete-time form of another model.

Action for the next meeting: show the original photo/slide or ask, “Sir, could
you please confirm the full form and reference for LTIDT?” Once confirmed, add
the exact definition and source here.

## Comparison table

| Model | Deterministic? | How a vertex changes state | Permanent? | Main output |
|---|---|---|---|---|
| GB | Yes, for a fixed source sequence | selected as a source or reached by fire | Yes | burn round, burning number |
| ICM | No | one probabilistic attempt from each newly active neighbour | Yes | cascade size/probability |
| LTM | Deterministic after weights and thresholds are fixed | active-neighbour weight reaches threshold | Yes | activation round/cascade size |
| SIR | No in the usual stochastic network form | infection probability, then recovery probability | Infection is temporary | epidemic curve, final infected/recovered count |

## GB compared with the BFS already implemented

- BFS has one fixed source and finds minimum hop distance from that source.
- GB may ignite a different new source in every round.
- BFS output is `distance[source, v]`.
- GB output is the earliest round in which each vertex burns.
- Running multi-source BFS once is still not identical to graph burning because
  GB sources start at different times and therefore have different radii.

Our BFS knowledge is still useful: each fire source produces expanding BFS-like
layers, and Giraph messages naturally carry the next burn round.

## Giraph implementation plan

### Phase A — deterministic Graph Burning simulator

Start with a small undirected text graph and a known source schedule. Store one
value per vertex:

```text
burnRound = -1   means unburned
burnRound >= 0   means the first round in which it burned
```

Giraph superstep design:

1. Read the source schedule, for example `3,8,6`.
2. At superstep 0, ignite source 3 and send a fire message to its neighbours.
3. At the next superstep, vertices receiving their first fire message record
   that round, send fire onward, and the scheduled source 8 is also ignited.
4. Continue until every vertex is burned or no progress is possible.
5. Use aggregators to count newly burned, total burned and unburned vertices.
6. Output `vertex_id burn_round source_flag` or an equivalent documented form.

Only newly burned vertices need to send messages: a fire wave moves one edge
per round, and repeated messages from old burned vertices would be unnecessary.

### Phase B — validation

- Manually verify the path example.
- Verify a star, cycle and disconnected graph.
- Check that every vertex burns exactly once.
- Compare Giraph burn rounds with a small sequential reference program.
- Test multiple HDFS input part files.

### Phase C — source-selection heuristics

After the simulator is correct, compare possible heuristics:

- highest-degree unburned vertex;
- farthest unburned vertex from existing sources;
- centrality-based selection;
- randomized selection with a fixed random seed;
- a published graph-burning approximation/heuristic.

For small graphs, exhaustive search can provide the true optimum for validation.
For larger graphs, report that a heuristic returns an upper bound, not
necessarily the exact burning number.

### Phase D — other diffusion models

Implement one model at a time after GB:

- ICM needs edge probabilities, random trials and repeated simulations.
- LTM needs incoming influence weights and a threshold for every vertex.
- SIR needs state, infection/recovery probabilities and careful random-number
  handling for reproducible distributed experiments.

## Proposed work for this week

- [x] Understand GB, ICM, LTM and SIR at concept level.
- [x] Identify that LTIDT requires confirmation.
- [ ] Draw and manually solve a small Graph Burning example.
- [ ] Define the Giraph input, output and source-schedule formats.
- [ ] Implement `LearningGraphBurningComputation.java` as a simulator.
- [ ] Build the shaded Giraph JAR.
- [ ] Run and validate it on small graphs.
- [ ] Add English/Hinglish code explanation, results and weekly report.

## Reliable learning sources

1. Bonato, Janssen and Roshanbin, **How to Burn a Graph** — original Graph
   Burning paper: <https://arxiv.org/abs/1507.06524>
2. Bonato, **A Survey of Graph Burning** — definitions, results and open
   problems: <https://doi.org/10.55016/ojs/cdm.v16i1.71194>
3. Bonato, Janssen and Roshanbin, **Burning a Graph is Hard** — complexity of
   finding the optimum: <https://arxiv.org/abs/1511.06774>
4. Kempe, Kleinberg and Tardos, **Maximizing the Spread of Influence through a
   Social Network** — foundational IC/LT influence-maximization paper:
   <https://www.cs.cornell.edu/home/kleinber/kdd03-inf.pdf>
5. PLOS ONE, **MATI** background section — clear illustrated definitions of
   IC and LT: <https://doi.org/10.1371/journal.pone.0206318>
6. NPTEL, **Social Networks** — Week 7 lectures 89–94 cover diffusion,
   cascades, communities and thresholds:
   <https://www.nptel.ac.in/courses/106106169>
7. MIT OpenCourseWare, **Epidemiological Models—Disease Spreading in a
   Population** — university video explaining SIR:
   <https://ocw.mit.edu/courses/res-10-s95-physics-of-covid-19-transmission-fall-2020/resources/video-3-1-epidemiological-models2014disease-spreading-in-a-population/>
8. MIT Networks Lecture 8, **Diffusion through Networks** — network structure,
   epidemics and diffusion:
   <https://economics.mit.edu/sites/default/files/inline-files/Lecture%208%20-%20Diffusion%20through%20Networks.pdf>

Prefer these papers and university courses over short unsourced videos. Read
the Graph Burning original paper first through its definition and examples;
the full proofs can be studied later.

*Sources checked: 22 September 2026.*

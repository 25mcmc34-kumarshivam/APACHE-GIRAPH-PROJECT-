# LearningGraphBurningComputation — Hinglish Guide

This is a team-learning explanation. Giraph compiles the Java file in `src/`;
this Markdown file is only for understanding.

## Program ka goal

Hum pehle se diya hua source sequence, jaise `3,8,6`, simulate karte hain. Har
round me ek naya source burn hota hai aur pichhle round me burn hue vertices
apne neighbours ko message bhejte hain. Final value batati hai vertex pehli baar
kaunse round me burn hua.

This first program **minimum burning number search nahi karta**. It checks
whether a supplied burning sequence covers the graph and calculates burn rounds.

## Generic types

```java
BasicComputation<LongWritable, DoubleWritable,
    FloatWritable, DoubleWritable>
```

- `LongWritable`: vertex ID, such as 1 or 9.
- first `DoubleWritable`: vertex value, used as burn round.
- `FloatWritable`: input edge weight. Burning ignores it, but our shared text
  reader provides this edge type.
- second `DoubleWritable`: message carrying the next burn round.

## Configuration

`StrConfOption SOURCE_SEQUENCE` command ke
`-ca LearningGraphBurning.sourceSequence=3,8,6` value ko read karta hai.
`getSources()` commas par split karke `long[] {3, 8, 6}` banata hai. Array
order hi burning-round order hai.

## Superstep and round

Giraph superstep zero se start hota hai, but human-readable burning rounds one
se start hote hain:

```java
long currentRound = getSuperstep() + 1;
```

Therefore superstep 0 = round 1, superstep 1 = round 2, and so on.

## Unburned marker

```java
vertex.getValue().set(Double.MAX_VALUE);
```

Very large value ko infinity ki tarah use kiya hai. Jab tak smaller burn-round
value nahi milti, vertex unburned maana jata hai.

## Two ways a vertex can burn

1. It receives a fire message from a neighbour that burned in the previous
   round.
2. Its ID equals the scheduled source for the current round.

The program takes the minimum value, so a vertex already reached by spreading
cannot later be overwritten with a worse round.

## Why only newly burned vertices send messages

Fire crosses one edge per round. A vertex only starts its outgoing fire wave
when it first burns. Purana burned vertex har round same messages bhejega to
network traffic waste hoga.

## Why the last round sends no further fire

A sequence containing `k` sources defines `k` burning rounds. Fire produced in
round `k` would arrive in round `k+1`, outside the sequence being evaluated.
Therefore messages are sent only when `earliestRound < sources.length`.

## Why vertices do not halt immediately

In ordinary BFS, a halted vertex is reactivated by an incoming message. A
future burning source might receive no message, but it must still execute in
its scheduled round. Therefore all vertices remain active until the final
configured round. After that they call `voteToHalt()`.

## Expected nine-node result

For path `1—2—3—4—5—6—7—8—9` and sequence `3,8,6`:

- round 1: vertex 3;
- round 2: vertices 2, 4 and source 8;
- round 3: vertices 1, 5, 7, 9 and source 6.

All vertices burn in three rounds. Output value `3.0` means “first burned in
round 3”; it is not a shortest-path weight.

## Present limitation

The program evaluates a supplied sequence. Next research stage me source
selection heuristic or exact search add hoga. Until then, do not describe its
output as proof that every supplied sequence is optimal.

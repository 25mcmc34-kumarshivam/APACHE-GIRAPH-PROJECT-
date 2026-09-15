# Giraph Java Programs — Hinglish Learning Guide

> **Sirf team learning ke liye:** Is folder ki files explanation notes hain.
> Giraph build ya server execution mein inka use nahi hota. Actual compilable
> Java files repository ke `src/` folder mein hain.

## Is guide ko kaise use karein

1. Pehle actual Java file `src/` mein dekho.
2. Phir usi program ka Hinglish explanation yahan padho.
3. Har important line ko apne words mein explain karne ki koshish karo.
4. Program run karne se pehle expected output manually calculate karo.

## Programs

1. [Out-degree computation](LearningOutDegreeComputation-Hinglish.md)
2. [In-degree computation](LearningInDegreeComputation-Hinglish.md)
3. [Plain-text graph reader](LongDoubleFloatTextInputFormat-Hinglish.md)
4. [Breadth-first search](LearningBfsComputation-Hinglish.md)

## Common Giraph types

```java
BasicComputation<LongWritable, DoubleWritable,
                 FloatWritable, DoubleWritable>
```

Is declaration ke chaar types ka order fixed hai:

1. `LongWritable` — vertex ki ID, jaise `1`, `2`, ya `30`.
2. `DoubleWritable` — vertex ke andar store hone wali value, jaise degree,
   PageRank, ya distance.
3. `FloatWritable` — edge ka value/weight.
4. `DoubleWritable` — vertices ke beech bheje jane wale message ka type.

`Writable` Hadoop ka serializable format hai. Data ko disk par store ya network
par transfer karne ke liye Hadoop ko normal Java primitive ke badle ye wrapper
types chahiye hote hain.

## Common words

- **Vertex:** graph ka node.
- **Edge:** do vertices ke beech directed connection.
- **Outgoing edge:** current vertex se bahar jane wala edge.
- **Incoming edge:** kisi aur vertex se current vertex par aane wala edge.
- **Superstep:** Giraph computation ka synchronized round.
- **Message:** ek vertex se doosre vertex ko bheja gaya data.
- **`voteToHalt()`:** vertex bolta hai ki abhi uske paas aur kaam nahi hai.
  Future message aane par Giraph us vertex ko phir active kar sakta hai.

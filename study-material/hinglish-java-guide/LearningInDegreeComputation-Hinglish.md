# LearningInDegreeComputation — Hinglish Explanation

Actual code: [`src/LearningInDegreeComputation.java`](../../src/LearningInDegreeComputation.java)

## Program ka purpose

Kisi vertex par kitne directed edges aa rahe hain, woh in-degree hai. Giraph
vertex ke paas normally outgoing edges hote hain, incoming-edge list nahi.
Isliye message passing use karni padti hai.

## Do supersteps kyun?

### Superstep 0 — messages bhejna

```java
if (getSuperstep() == 0)
```

`getSuperstep()` current synchronized round ka number deta hai. First round
zero se start hota hai.

```java
for (Edge<LongWritable, FloatWritable> outgoingEdge : vertex.getEdges())
```

Current vertex ke har outgoing edge par loop chalta hai.

```java
sendMessage(
    outgoingEdge.getTargetVertexId(), new DoubleWritable(1.0));
```

Har edge ke destination ko ek marker message `1.0` bheja jata hai. Example:
agar `5 → 1`, `5 → 10`, aur `5 → 11` hain, vertex 5 teen alag messages bhejega.

Message ki numeric value add nahi ho rahi. Sirf message ki presence ek incoming
edge ko represent karti hai.

### Superstep 1 — messages count karna

```java
long incomingEdgeCount = 0;
```

Count zero se start hota hai.

```java
for (DoubleWritable ignoredMessage : messages) {
  incomingEdgeCount++;
}
```

Jitne messages current vertex ko mile, utni baar count increment hota hai.
Variable ka naam `ignoredMessage` hai because message ke andar `1.0` value ko
read karna necessary nahi; hame sirf messages ki sankhya chahiye.

```java
vertex.getValue().set(incomingEdgeCount);
vertex.voteToHalt();
```

Final in-degree vertex value mein store hota hai, phir vertex halt karta hai.

## Example

Vertex `1` ko edges `5→1`, `6→1`, aur `30→1` milte hain. Superstep 0 mein ye
teen sources vertex 1 ko message bhejte hain. Superstep 1 mein vertex 1 three
messages count karke value `3.0` store karta hai.

## Important graph identity

Directed graph mein:

```text
sum(out-degree) = total edges = sum(in-degree)
```

Hamare 30-node dataset mein tino values `79` hain. Ye result validation ka
strong check hai.

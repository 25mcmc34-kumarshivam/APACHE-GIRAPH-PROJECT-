# LearningOutDegreeComputation — Hinglish Explanation

Actual code: [`src/LearningOutDegreeComputation.java`](../../src/LearningOutDegreeComputation.java)

## Program ka purpose

Har vertex se kitne directed edges bahar ja rahe hain, unki counting karna
out-degree kehlata hai.

Example:

```text
5 1:1 10:1 11:1
```

Vertex `5` ke teen outgoing neighbors hain: `1`, `10`, aur `11`. Isliye iska
out-degree `3` hai.

## Imports ka meaning

```java
import java.io.IOException;
```

Giraph ka `compute()` method I/O problem report kar sakta hai, isliye
`IOException` declare hota hai.

```java
import org.apache.giraph.graph.BasicComputation;
import org.apache.giraph.graph.Vertex;
```

`BasicComputation` hamare algorithm ka base class hai. `Vertex` current node,
uski value, aur uske outgoing edges ko represent karta hai.

```java
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
```

Ye Hadoop ke serializable types hain: long ID, double vertex value, aur float
edge weight.

## Class declaration

```java
public class LearningOutDegreeComputation extends BasicComputation<
    LongWritable, DoubleWritable, FloatWritable, DoubleWritable>
```

Meaning: vertex ID long hai, vertex value double hai, edge value float hai, aur
message type double hai. Out-degree mein messages use nahi honge, lekin Giraph
generic declaration mein message type dena compulsory hai.

## `compute()` parameters

```java
Vertex<LongWritable, DoubleWritable, FloatWritable> vertex
```

`vertex` woh current node hai jiske liye Giraph abhi calculation kar raha hai.

```java
Iterable<DoubleWritable> messages
```

Previous superstep se aaye messages. Is algorithm mein iska use nahi hota,
kyunki outgoing-edge list current vertex ke paas already available hai.

## Main calculation

```java
long outgoingEdgeCount = vertex.getNumEdges();
```

`getNumEdges()` current vertex ke outgoing edges ki total sankhya deta hai.

```java
vertex.getValue().set(outgoingEdgeCount);
```

Calculated count ko vertex ki stored value bana diya jata hai. Job complete
hone par output format vertex ID aur ye value print karta hai.

```java
vertex.voteToHalt();
```

Calculation ek hi superstep mein complete ho gayi. Koi message nahi bhejna,
isliye vertex halt kar sakta hai.

## Complexity

Giraph ko har vertex ke edge objects traverse karke count karne ki zarurat nahi;
`getNumEdges()` size deta hai. Conceptually output har vertex ke liye ek baar
calculate hota hai. Communication cost zero hai because no messages are sent.

## Yaad rakhna

Out-degree local information hai. Isi wajah se ye in-degree se simpler hai.

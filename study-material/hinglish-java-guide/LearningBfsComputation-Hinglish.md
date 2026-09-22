# LearningBfsComputation — Hinglish Explanation

Actual code: [`src/LearningBfsComputation.java`](../../src/LearningBfsComputation.java)

## BFS kya calculate karta hai?

Breadth-first search source vertex se har reachable vertex tak minimum number
of edges, yani minimum hops, calculate karta hai. Edge weights ignore hote hain.

## Source configure karna

```java
public static final LongConfOption SOURCE\\\_ID = new LongConfOption(
    "LearningBfsComputation.sourceId", 1L,
    "Vertex from which BFS starts");
```

Default source ID `1` hai. Command mein source change kiya ja sakta hai:

```text
-ca LearningBfsComputation.sourceId=5
```

## Initial values

```java
if (getSuperstep() == 0) {
  vertex.getValue().set(Double.MAX\\\_VALUE);
}
```

Sab vertices pehle infinity/unreachable hain. Java mein yahan
`Double.MAX\\\_VALUE` infinity marker ke roop mein use ho raha hai.

```java
double smallestCandidate =
    vertex.getId().get() == SOURCE\\\_ID.get(getConf())
        ? 0.0 : Double.MAX\\\_VALUE;
```

Agar current vertex selected source hai, candidate distance zero. Baaki ke liye
infinity.

## Messages se minimum lena

```java
for (DoubleWritable message : messages) {
  smallestCandidate = Math.min(smallestCandidate, message.get());
}
```

Multiple paths se multiple candidates aa sakte hain. `Math.min` sabse chhota
hop count choose karta hai.

## Better path milne par update

```java
if (smallestCandidate < vertex.getValue().get())
```

Sirf tab work hota hai jab new distance stored distance se better hai. Isse
unnecessary repeated messages kam hote hain.

```java
double neighborDistance = smallestCandidate + 1.0;
```

Current vertex se ek edge cross karne par hop count one increase hota hai.

Har outgoing neighbor ko ye candidate message bheja jata hai. Next superstep
mein neighbors apna minimum choose karte hain.

## `voteToHalt()` ke baad kya hoga?

Vertex temporary inactive hota hai. Agar next round mein new message aata hai,
Giraph usko automatically active kar deta hai. Jab koi message pending nahi aur
sab vertices inactive ho jate hain, BFS complete hota hai.

## BFS versus weighted shortest path

* BFS: every edge ka cost one hop. Stored weight ignore hota hai.
* Weighted shortest path: path cost edge weights ka sum hota hai.

Hamare current dataset mein every edge weight `1` hai, so BFS aur weighted
shortest-path distances equal honge. Later unequal weights wala dataset bana kar
dono algorithms ka difference clearly demonstrate karna chahiye.


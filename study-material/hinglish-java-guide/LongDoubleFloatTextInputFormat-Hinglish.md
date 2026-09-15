# LongDoubleFloatTextInputFormat — Hinglish Explanation

Actual code: [`src/LongDoubleFloatTextInputFormat.java`](../../src/LongDoubleFloatTextInputFormat.java)

## Is class ki zarurat kyun hai?

Algorithm ko file ka raw text samajh nahi aata. `VertexInputFormat` raw line ko
Giraph `Vertex` object mein convert karta hai.

Hamari format:

```text
1 2:1 6:1
```

Meaning: vertex 1, edge to 2 with weight 1, aur edge to 6 with weight 1.

File `.txt` ho ya kisi aur extension ki, parser extension nahi dekhta. Command
mein `-vif org.apache.giraph.examples.LongDoubleFloatTextInputFormat` dene ke
karan Giraph ye class use karta hai.

## Configuration object

```java
private ImmutableClassesGiraphConfiguration<...> configuration;
```

Giraph ke configured vertex/edge types ka record. `configuration.createVertex()`
correct type ka empty vertex object banata hai.

## Separators

```java
Pattern.compile("\\s+")
```

One or more spaces/tabs par line ko tokens mein divide karta hai. `\\s+` use
karne se extra spaces ke wajah se empty token nahi banta.

```java
Pattern.compile(":")
```

`2:1` ko target ID `2` aur weight `1` mein divide karta hai.

## Current line read karna

```java
String line = getRecordReader().getCurrentValue().toString().trim();
```

Hadoop record reader se current line milti hai. `trim()` start/end spaces hata
deta hai.

```java
String[] tokens = tokenSeparator.split(line);
long vertexIdNumber = Long.parseLong(tokens[0]);
```

Line tokens mein divide hoti hai. First token vertex ID hai aur text se long
number mein convert hota hai.

## Edges banana

Loop token 1 se start hota hai because token 0 vertex ID tha. Har `ID:weight`
token validate aur parse hota hai:

```java
long targetVertexId = Long.parseLong(edgeParts[0]);
float edgeWeight = Float.parseFloat(edgeParts[1]);
```

Then `EdgeFactory.create()` target and weight ka Giraph edge object banata hai.

## Vertex initialize karna

```java
vertex.initialize(
    new LongWritable(vertexIdNumber),
    new DoubleWritable(0.0),
    outgoingEdges);
```

Isme ID, initial vertex value `0.0`, aur complete outgoing-edge list attach hoti
hai. PageRank, degree, BFS, aur shortest-path algorithms later vertex value ko
apne answer se replace kar dete hain.

## Multiple files ka behavior

HDFS input path ek directory hai. Hadoop directory ke tino part files padhta
hai. Har line se ek vertex banta hai. Edge ka target kisi bhi part file mein
defined ho sakta hai; part file boundary graph connection ko restrict nahi karti.

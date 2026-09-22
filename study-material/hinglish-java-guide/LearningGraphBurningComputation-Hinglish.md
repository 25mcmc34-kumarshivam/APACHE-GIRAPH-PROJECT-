# LearningGraphBurningComputation — Hinglish Guide

This is a team-learning explanation. Giraph compiles the Java file in `src/`;
this Markdown file is only for understanding.

## Pehle teen files ka role clear karo

| File | Kaam | Kahan chalta hai? |
|---|---|---|
| `src/LearningGraphBurningComputation.java` | Ek vertex ke liye ek round ka fire rule | Giraph/YARN workers |
| `scripts/run_graph_burning.sh` | Job start karta hai; input, output, sources pass karta hai | `mca2025` shell |
| `scripts/find_small_graph_burning_sequence.py` | Chhote graph me sources khud search karta hai | Local Python; Giraph nahi |

Java file ka naam `LearningGraphBurningComputation.java` hai; compiled class
JAR me jati hai. Sirf Markdown edit karne se Java job ka behaviour change nahi
hota. Java source change ho to Maven rebuild aur naya JAR use karna padta hai.

## Program ka goal

Hum pehle se diya hua source sequence, jaise `3:8:6`, simulate karte hain. Har
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

`Writable` Hadoop ka serializable data type hai: value network/task ke
beech ja sakti hai. `FloatWritable` edge ka `:1` weight hold karta hai; is
algorithm me edge weight ko calculation me use nahi karte. Isliye `2:10`
edge bhi fire ke liye ek hi hop hai, 10 rounds nahi.

## Configuration

`StrConfOption SOURCE_SEQUENCE` command ke
`-ca LearningGraphBurning.sourceSequence=3:8:6` value ko read karta hai.
`getSources()` colons par split karke `long[] {3, 8, 6}` banata hai. Giraph
`-ca` ke andar comma ko alag configuration setting maan leta hai. Array
order hi burning-round order hai.

Annotated idea (ye guide ka example hai, actual compiled source nahi):

```java
String configured = SOURCE_SEQUENCE.get(getConf()).trim(); // command se 3:8:6 lo
String[] tokens = configured.split(":");              // ["3", "8", "6"]
long[] sources = new long[tokens.length];               // 3 IDs ke liye jagah
for (int index = 0; index < tokens.length; index++) {   // har text ID par jao
  sources[index] = Long.parseLong(tokens[index].trim()); // "3" ko number 3 banao
}
```

`long[]` ordered list hai. `sources[0]=3` means first round me 3; `sources[1]=8`
means second round me 8. Index 0 se start hota hai, burning rounds 1 se.

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

`1.7976931348623157E308` isi marker ka printed form hai. Isko distance,
probability, ya burn time **mat** samajhna. Example `2:8` on nine-node path:
round 2 tak vertices 4–7 aur 9 unburned rehte hain. Unka huge output isi
marker ki wajah se hota hai.

## Two ways a vertex can burn

1. It receives a fire message from a neighbour that burned in the previous
   round.
2. Its ID equals the scheduled source for the current round.

The program takes the minimum value, so a vertex already reached by spreading
cannot later be overwritten with a worse round.

Key variables line-by-line:

```java
double earliestRound = vertex.getValue().get(); // purana first-burn round
for (DoubleWritable message : messages) {      // padosi se aayi har fire
  earliestRound = Math.min(earliestRound, message.get()); // sabse jaldi wala
}
if (superstep < sources.length &&
    vertex.getId().get() == sources[(int) superstep]) {
  earliestRound = Math.min(earliestRound, currentRound); // yeh source hai
}
```

`vertex` = Giraph ne jo **ek** point is `compute` call ko diya hai.
`vertex.getId()` = us point ka number. `vertex.getValue()` = usme abhi saved
burn round. `messages` = is point ko pichhle superstep me bheje gaye messages.
`Math.min` isliye hai ki agar do taraf se fire aaye to pehle pahunchne ka
round store ho. Source check har vertex me hota hai, lekin match sirf chosen
ID ke liye true hota hai.

## Why only newly burned vertices send messages

Fire crosses one edge per round. A vertex only starts its outgoing fire wave
when it first burns. Purana burned vertex har round same messages bhejega to
network traffic waste hoga.

```java
boolean newlyBurned = earliestRound < vertex.getValue().get();
if (newlyBurned) {
  vertex.getValue().set(earliestRound); // first-burn round save
  // Har outgoing edge ke target ko next round ka message bhejo.
}
```

`<` comparison important hai: equal value par dobara burn nahi hua. `set` se
Giraph output me bhi wahi round dikhega. `edge.getTargetVertexId()` us
padosi ka ID hai jisko message bhejna hai. Giraph messages ko next superstep
me deliver karega; Java loop neighbour ka value turant change nahi karta.

## Why the last round sends no further fire

A sequence containing `k` sources defines `k` burning rounds. Fire produced in
round `k` would arrive in round `k+1`, outside the sequence being evaluated.
Therefore messages are sent only when `earliestRound < sources.length`.

## Why vertices do not halt immediately

In ordinary BFS, a halted vertex is reactivated by an incoming message. A
future burning source might receive no message, but it must still execute in
its scheduled round. Therefore all vertices remain active until the final
configured round. After that they call `voteToHalt()`.

`voteToHalt()` ka matlab Java process ko kill karna nahi hai. Vertex bolta
hai: "ab meri calculation complete hai." Giraph ko sab vertices ke halt aur
pending messages dekhkar job finish karna hota hai. Agar round 1 me future
source 8 halt ho jaye aur use koi incoming fire na mile, to round 2 me 8
khud source select nahi ho paayega; isliye final round tak active rakhte hain.

## Ek vertex ke compute call ka pura flow

1. Giraph current vertex aur uske messages deta hai.
2. `getSources()` source list read karta hai; `getSuperstep()` round nikalta hai.
3. Sirf first superstep me vertex ko UNBURNED marker milta hai.
4. Messages aur source selection se earliest possible burn round nikalta hai.
5. Agar pehli baar burn hua, vertex value save hoti hai.
6. Agar ek aur round bacha hai, har outgoing neighbour ko `round+1` bhejte hain.
7. Last round par vertex halt vote karta hai.

Ye steps **har vertex** ke liye Giraph workers par hote hain. Ek `compute`
call poore graph ka loop nahi hai. Isi message model ko vertex-centric
computation bolte hain.

## Expected nine-node result

For path `1—2—3—4—5—6—7—8—9` and sequence `3:8:6`:

- round 1: vertex 3;
- round 2: vertices 2, 4 and source 8;
- round 3: vertices 1, 5, 7, 9 and source 6.

All vertices burn in three rounds. Output value `3.0` means “first burned in
round 3”; it is not a shortest-path weight.

## Present limitation

The program evaluates a supplied sequence. Next research stage me source
selection heuristic add hoga. Chhote graphs ke liye alag Python exact checker
ab hai, lekin Java Giraph job me automatic source selection abhi nahi hai.
Sirf successful Java output ko optimality ka proof mat bolna.

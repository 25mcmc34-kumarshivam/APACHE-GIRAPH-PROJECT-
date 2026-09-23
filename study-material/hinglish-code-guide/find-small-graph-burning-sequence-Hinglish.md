# Python exact Graph Burning checker — very detailed Hinglish guide

Original executable file: [`scripts/find_small_graph_burning_sequence.py`](../../scripts/find_small_graph_burning_sequence.py).
Ye Markdown **sirf samajhne ke liye** hai. Isme Hinglish comments wale chhote
code snippets hain; Python run karne ke liye original `.py` file use karo.

## Sabse pehle: Java aur Python ka farq

Giraph Java program ko hum sources `3:8:6` dete hain. Woh batata hai kis vertex
ko kis round me fire lagi. Python checker ulta kaam karta hai: ek **small**
graph ko padhkar source sequence dhundta hai. Python local machine par chalta
hai; HDFS, YARN, Maven ya Java JAR iske liye zaroori nahi. Python ka result
Giraph me test karna alag experiment hai.

Ab script ke **teen modes** hain:

| Mode | Kaam | Minimum prove karta hai? |
|---|---|---|
| No flag | Chhote graph me all source orders check | Haan, agar limit hit na ho |
| `--greedy` | Jaldi useful sources propose karo | Aam taur par nahi |
| `--check-sequence 3:8:6` | Di hui list valid/complete hai kya | Nahi; sirf list ko check karta hai |

## Input line ka meaning

```text
1 2:1 3:1
2 1:1
3 1:1
```

Pehla number = line ka vertex ID. `2:1` = vertex 2 tak edge jiska weight 1
hai. Burning weights ignore karta hai: ek edge cross karne me ek round lagta
hai. Undirected graph me reverse line bhi likho: agar `1 2:1` hai, vertex 2
ki line me `1:1` hona chahiye. Folder me kai `.txt` part files ho sakti hain;
milkar woh ek graph banti hain. Ek vertex ki line do files me repeat na karo.

## Imports aur command-line values

```python
import argparse              # command me diye graph path aur options read karo
from collections import deque # BFS ki first-in-first-out queue
from pathlib import Path     # file/folder path ko handle karo
```

`python3 script.py datasets/graph-burning-path-9` me folder path argument
hai. `argparse` isko `args.graph` banata hai. Optional `--max-states 500000`
batata hai kitne guesses ke baad rukna hai. Limit hit hone par **exact answer
claim nahi hota**.

## `read_graph(path)` — files se graph banana

```python
files = sorted(path.glob("*.txt")) if path.is_dir() else [path]
graph = {}                       # vertex -> set of neighbours
```

Folder diya to `*.txt` ki sab files lo. Ek file diya to wahi lo. `sorted`
result repeatable banata hai. `graph` dictionary example: `{1: {2, 3},
2: {1}}`. Curly-brace neighbour set duplicate neighbour pakadta hai.

Har line par code ye karta hai:

```python
line = raw.strip()              # newline/outer spaces hatao
fields = line.split()           # "1 2:1" -> ["1", "2:1"]
vertex = int(fields[0])         # "1" text ko numeric ID 1 banao
neighbours = set()              # is vertex ke padosi
```

Blank line aur `#` comment ignore hoti hai. `fields[1:]` har edge token hai.
`field.split(":", 1)` se neighbour ID aur weight alag hote hain. `float(weight)`
sirf format valid hai ya nahi check karta hai; calculation me weight use nahi
hota. Missing vertex line, repeated vertex, repeated neighbour, ya missing
reverse edge par clear error milta hai. Isse galat dataset ko exact answer
samajhne se bachate hain.

## `distances_from(graph, source)` — BFS ka matlab

BFS = Breadth-First Search. Source se pahle 1-edge wale neighbours, phir
2-edge wale, phir 3-edge wale explore hote hain. `deque` queue me pehle dala
vertex pehle nikalta hai.

```python
distances = {source: 0}              # source se khud ki distance zero
queue = deque([source])              # starting point
while queue:                         # jab tak kuch explore karna baaki hai
    vertex = queue.popleft()         # queue ka sabse purana vertex lo
    for neighbour in graph[vertex]:  # uske saare neighbours dekho
        if neighbour not in distances:
            distances[neighbour] = distances[vertex] + 1
            queue.append(neighbour)
```

Path `1--2--3` me source 1 se distances: `{1:0, 2:1, 3:2}`. Agar dusra
component `4--5` hai, 4 aur 5 dictionary me nahi aayenge: un tak koi path
nahi. Search me missing distance ko infinity maana jata hai.

## `find_sequence` — exact search ka core

`vertices = sorted(graph)` possible source IDs hain. `distances` me har
possible source se BFS pehle se calculate kiya jata hai; search ke har guess
par BFS dobara nahi chalana padta.

```python
for rounds in range(1, len(vertices) + 1):
    # 1 round possible? Nahi to 2? Nahi to 3? ...
```

Pehla successful `rounds` minimum hai **agar search limit hit nahi hui**,
kyunki usse chhote sab round counts ko exhaustively check kiya hai. Example
`k=3`: round-1 source 2 edges tak pahunch sakta hai by final round; round-2
source 1 edge tak; round-3 source sirf apne aap ko cover karta hai.

```python
radius = rounds - round_number
```

### Bit mask ka easy meaning

3 vertices maan lo: `[1, 2, 3]`. Teen switches hain: `001` vertex 1,
`010` vertex 2, `100` vertex 3. Agar 1 aur 3 cover hue to switches `101`.
Sab covered = `111`. Python me ye binary patterns ordinary integers me store
hote hain. `1 << index[other]` ek vertex ka switch on karta hai. `|` (OR)
do sources ke covered vertices ko combine karta hai. `all_mask` me sab
switches on hote hain. Bit mask sirf efficient representation hai; graph
ka concept badalta nahi.

### `search(round_number, chosen, covered)`

- `round_number`: ab kaunsa source select karna hai (1, 2, 3...).
- `chosen`: ab tak ke ordered sources, jaise `(3, 8)`.
- `covered`: bit mask of vertices jo final round tak in sources se cover honge.
- `candidate`: agla possible vertex ID, sorted order me try hota hai.

Code ek candidate choose karta hai, `chosen + (candidate,)` se new tuple
banata hai, `covered | coverage[...]` se covered set badhata hai, aur
`search(...)` ko next round ke liye call karta hai. Agar branch fail hui to
next candidate try hota hai. Isko **backtracking** bolte hain. Giraph is
search ko distributed tarike se nahi kar raha; ye local Python reference hai.

Ek rule important hai: later source pehle ke round me jal chuka nahi hona
chahiye. Code distance compare karta hai:

```python
distance_from_old_source < current_round - old_source_round
```

True hua to candidate skip. Distance **equal** ho to candidate apne scheduled
round me hi fire se reach ho sakta hai; woh earlier round me nahi jala tha.
Isliye star test `1:2` allowed hai: centre 1 se leaf 2 ki distance 1 hai,
aur source rounds ka difference bhi 1.

`states` tries count karta hai. Bahut guesses hone par `SearchLimitReached`
error deta hai. Error ka matlab "minimum nahi pata", **not** "minimum
nahi hai". **Exact mode** ki input limit 10 vertices hai. 30-node graph
ke liye neeche wala greedy mode use kar sakte hain; very large graph ke
liye aage distributed method chahiye.

## `burn_rounds(graph, sequence)` — source list check

Ye function human ya Giraph sequence ko independently check karta hai.
Unknown source ID (jaise graph me 99 nahi), repeated source (`3:3`), aur
jo source apne selected round **se pehle** jal chuka tha, un par error.
Lekin usi round me kisi aur source ki fire pahunch rahi ho to source allowed
hai: round start hone par woh unburned tha. Star graph me `1:2` isi tarah
valid hai.

Har vertex ka arrival = `source_round + BFS_distance`. Sab possible
sources ke arrivals me minimum uska first-burn round hai. Agar minimum
total scheduled rounds ke baad hai, result `None` hota hai aur screen par
`UNBURNED` print hota hai. Java ka huge `Double.MAX_VALUE` yahan nahi.
**Java/Giraph job abhi khud invalid source sequence reject nahi karta**;
ye local Python pre-check hai.

## `greedy_sequence(graph)` — automatic, par general proof nahi

Greedy har proposed total length `k` ke liye ek sequence banata hai. Har
round me woh legal source chunta hai jo final round tak sabse zyada **naye**
vertices cover kare. `k=4` me round-1 source radius 3, round-2 radius 2,
round-3 radius 1, round-4 radius 0 cover kar sakta hai.

```python
for total_rounds in range(1, len(vertices) + 1): # 1, phir 2, phir 3...
    chosen = []                                      # is k ke sources
    covered = set()                                  # final tak covered nodes
    for round_number in range(1, total_rounds + 1):
        radius = total_rounds - round_number
        # Har legal candidate ka new coverage count karo.
        # Sabse bada count wala candidate choose karo.
```

Do candidates same score dein to chhota vertex ID choose hota hai; isliye
har run repeatable hai. Greedy ek branch choose karta hai, exact search
jaisa sab possible orders nahi dekhta. Complete sequence bhi normally
minimum rounds ka proof nahi. 30-node graph par use kar sakte hain:

```bash
python3 scripts/find_small_graph_burning_sequence.py \
  datasets/thirty-node-undirected-burning --greedy
```

Output `1:18:3:8` aur 30/30 burned **local** prediction hai. Original
30-node graph directed tha; naye folder me edge ko two-way banaya hai.
Original graph change nahi hua. Giraph cluster run alag se verify hoga.

## `main()` aur printed output

`main()` arguments read karta hai, file parser aur search call karta hai,
phir vertices, minimum rounds, chosen sequence aur checked states print
karta hai. `if __name__ == "__main__": main()` ka matlab: file directly
run hui to CLI chalao; tests import karein to automatic CLI mat chalao.

Example local command:

```bash
python3 scripts/find_small_graph_burning_sequence.py datasets/graph-burning-path-9
```

Uske baad printed sequence ko `run_graph_burning.sh` ke third argument me
do, lekin first output path se **alag naya HDFS output path** use karo. Python
sequence dhundta hai; Java/Giraph per-vertex burn rounds verify karta hai.

## Khud check karo

1. Path `1--2--3`: kya one round enough hai? Nahi: one source one round me
   sirf apne aap ko burn karta hai.
2. Source sequence `2:1`, two rounds: 2 round 1 me burn; 1 aur 3 round 2 me
   burn. Haan, two rounds enough.
3. Two disconnected groups me BFS ek group se doosre tak distance nahi deta.
   Isliye dono groups cover karne ke liye source placement sochna padega.

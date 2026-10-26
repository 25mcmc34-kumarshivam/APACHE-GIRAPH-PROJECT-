# 120-node grid practical: basic se samjho (Hinglish)

Is file mein **naya bada experiment** hai. Result ko verified tabhi bolenge
jab same four input files lab Giraph par chalenge aur Python `expected.tsv`
se actual HDFS output ka `diff` 0 aayega. Abhi repo mein Python prediction
hai; Giraph run pending hai. Yeh synthetic teaching graph hai, real social
network dataset nahin. Optimization bhi nahin chal rahi.

## Grid kya hai aur 120 kahan se aaye?

Socho 10 rows aur 12 columns ka chessboard-like network. Har cell ek
vertex hai: `10 × 12 = 120`. IDs row-wise hain. First row 1–12, second
13–24, last 109–120. Sirf up/down/left/right adjacent cells ka edge hai.
Diagonal connection nahin. Example: vertex 1 ke neighbours 2 aur 13;
vertex 14 ke neighbours 2, 13, 15 aur 26. Har undirected edge dono
vertices ki lines mein likhi jaati hai. Horizontal edges `10×11=110`,
vertical edges `12×9=108`, total **218**. Text mein two endpoint entries
hone ke kaaran 436 adjacency entries hain, lekin actual undirected
connections 218 hi hain.

`scripts/generate_grid_graph.py` mein `make_grid(rows, columns)` nested
loops se har vertex ID nikalta hai: `row * columns + column + 1`. Boundary
check karta hai: top row ka upar neighbour nahin, left column ka left
neighbour nahin, etc. `split_parts(graph, part_count)` sorted IDs ko four
groups of 30 mein divide karta hai. `main()` arguments leta hai, existing
output path overwrite nahin karta, four `part-*.txt` aur `topology.json`
likhta hai. `topology.json` sirf metadata hai; Giraph input **nahin**.

Original graph [`datasets/grid-120-unscheduled/`](../../datasets/grid-120-unscheduled/)
mein line `1 2:1 13:1` jaisi hai. `1` vertex ID; `2:1` neighbour 2 with
weight 1; `13:1` neighbour 13 with weight 1. Burning mein weight use nahin
hota; har edge traverse karne mein one round lagta hai.

## Source round kaise add hua?

`scripts/prepare_random_burning_input.py` (detail [main round-preview
guide](show-burning-rounds-Hinglish.md)) ne second column add kiya:
`vertex_id source_round neighbour:weight ...`. Eight rounds aur seed
`20261026` se `15:104:35:101:41:111:83:86` sequence mila. `0` in second
column ka matlab source nahin; vertex phir bhi kisi neighbour se burn ho
sakta hai. Source round positive ho to us round mein naya ignition hoga.
Har pick valid unburned vertex se random hai, **coverage optimize nahin**.
`selection.json` seed aur list save karta hai taaki choice bhool na jaayein.
Sirf four scheduled `part-*.txt` HDFS mein upload honge.

## Python ka kaam aur Giraph ka kaam alag

1. `validate_burning_schedule.py` input read karke duplicate IDs, missing
   reverse edges, galat round markers aur previously burned source reject
   karta hai. Yeh source choose nahin karta.
2. `show_burning_rounds.py` Python mein har round simulate karke
   `expected.tsv` aur per-round tables banata hai. Round 1 mein only
   source 15 burns. Next round old fire ek edge spread hoti hai aur source
   104 ignite hota hai. Same rule round 8 tak chalta hai.
3. `run_graph_burning_from_input.sh` HDFS input validate karke Java Giraph
   computation submit karta hai. Giraph output ko Python formatter readable
   `B`/`NB -1` banata hai. Yeh **actual cluster run** hai.
4. `diff -u expected.tsv actual.tsv` independent final answers compare
   karta hai. No output + exit 0 means same rows. `NB -1` means scheduled
   last round ke end tak vertex nahin jala, error nahin.

Current local Python prediction: rounds 1–8 mein newly burned counts
**1, 5, 12, 20, 26, 30, 20, 5**. Total 119 burned; vertex **85** `NB -1`.
Yeh number Giraph run se pehle sirf prediction hai. Graph ke size ki wajah
se terminal ka har-round print long hoga; files ko inspect karna aasaan hai.
`round-08-nodes.tsv` har vertex ka final state bhi dikhata hai.

## Lab par safe order

1. Four scheduled parts Windows se lab ke `mca2025` home mein transfer.
2. `python3 ~/giraph/validate_burning_schedule.py LOCAL_DIR` se counts check.
3. `show_burning_rounds.py` se lab-side expected files aur optional PNG.
4. `hdfs dfs -put` se **only** four parts fresh HDFS input dir mein.
5. `yarn node -list` se RUNNING worker check.
6. Fresh HDFS output path par `bash ~/giraph/run_graph_burning_from_input.sh
   HDFS_INPUT HDFS_OUTPUT`.
7. Actual `part-00000` ko local file mein copy, `diff` compare.
8. Actual output aur pictures result folder mein save; tab weekly report ko
   “verified” update.

Is study guide aur main result record ko future mein actual lab evidence
ke saath update karna hoga. Abhi Python prediction ko Giraph result bolna
galat hoga.

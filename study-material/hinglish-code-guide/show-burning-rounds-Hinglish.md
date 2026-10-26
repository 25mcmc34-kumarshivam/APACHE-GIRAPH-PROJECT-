# Round-by-round Graph Burning Python guide (Hinglish)

Yeh guide team ke learning ke liye hai. **Main experiment** ke files `datasets/`, `scripts/`, aur `results/` mein hain; yeh file sirf samajhne ke liye hai. Ismein Week 14 wala limited-neighbour model mix mat karna. Yahan **standard Graph Burning** hai: har round mein ek naya source ignite hota hai; pichhle round mein jo vertices *naye* jale the, unse fire ek edge aage jaati hai. Naye jale vertices usi round mein dobara spread nahin karte.

## 1. Hum kya prove/check kar rahe hain?

User graph aur ignition schedule deta hai. Abhi Python ya Giraph koi “best” source **nahin** dhoondhta. Python pehle har round ka expected answer banata hai. Giraph usi input par distributed job chalakar final answer deta hai. `diff` se dono final files compare hoti hain. Same result aane ka matlab is example par agreement hai; iska matlab har possible graph par proof nahin hai.

Week 15 mein humne pehle se successfully run hua nine-node Giraph output compare kiya, **naya Giraph job nahin chalaya**. `diff` exit code 0 tha. Agla practical bada graph aur fresh Giraph run hoga.

## 2. Input ka ek line ka matlab

Format: `vertex_id source_round neighbour_id:weight ...`

Example: `3 1 2:1 4:1` ka matlab vertex 3 ko round 1 mein **naya source** banao; uske neighbours 2 aur 4 hain. `5 0 4:1 6:1` ka matlab 5 ko source **nahin** chuna, par fire neighbours se aakar 5 ko jala sakti hai. Input mein `0` ka matlab “not a selected source” hai; output mein `NB -1` ka matlab “scheduled rounds ke end tak not burned” hai. Yeh alag meanings hain. `:1` edge weight reader ke format ke liye hai; current burning hops count karti hai, weight use nahin karti.

Graph [`datasets/graph-burning-path-9-scheduled/`](../../datasets/graph-burning-path-9-scheduled/) ke `part-01.txt`, `part-02.txt`, `part-03.txt` mein hai. Teeno milkar path `1--2--3--4--5--6--7--8--9` banate hain. Undirected edge dono endpoint ki line mein hona chahiye. Source rounds: `3→1`, `8→2`, `6→3`. Directory ko input dene par Python sab `.txt` parts padh leta hai; HDFS par Giraph bhi input directory ke files ko ek dataset ki tarah padhta hai.

## 3. Round ko haath se samjho

| Round | Naya source | Purane fire se aaye | Is round mein naye B | Ab tak B |
|---:|---:|---|---|---|
| 1 | 3 | koi nahin | 3 | 3 |
| 2 | 8 | 3 ke neighbours 2,4 | 2,4,8 | 2,3,4,8 |
| 3 | 6 | 2→1,3; 4→3,5; 8→7,9 | 1,5,6,7,9 | sab 1–9 |

Round 2 mein 2 aur 4 jalte hain, lekin 2 aur 4 se usi round mein aage fire nahin jaati. Isliye 1 aur 5 round 3 mein jalte hain. Jo vertex do raaston se same round mein reach ho, usko ek hi baar count karte hain. Final output `vertex B/NB first_burn_round` hai. Agar vertex end tak na jale, `NB -1`.

## 4. `validate_burning_schedule.py` kya karta hai?

[`scripts/validate_burning_schedule.py`](../../scripts/validate_burning_schedule.py) Python preview ka imported helper bhi hai aur shell runner ka preflight check bhi. `parse_lines(lines)` har non-empty line ko `split()` karke ID, source round aur `neighbour:weight` padhta hai. `graph` dictionary mein `vertex -> neighbours ka set` rakhta hai. `sources` dictionary mein `round -> source vertex` rakhta hai. Duplicate vertex, duplicate neighbour, missing source round, same round ke do sources, undefined neighbour, reverse edge missing, aur non-finite weight reject karta hai. Agar scheduled source uske round **se pehle** jal chuka ho, woh schedule bhi reject hota hai.

`distances_from(graph, source)` queue (`deque`) se BFS karke source se har reachable vertex ka **minimum hop distance** nikalta hai. `predicted_rounds(graph, sources)` har source ke liye `source_round + hop_distance` calculate karta hai, sabse pehle arrival ko leta hai, aur last round se baad pahunchne wale ko `-1` deta hai. Yeh independently expected final answer hai. Is script ka kaam sources **choose** karna nahin hai.

## 5. `show_burning_rounds.py` ka function-by-function walkthrough

[`scripts/show_burning_rounds.py`](../../scripts/show_burning_rounds.py) mein `argparse` command-line arguments samajhta hai, `Path` file paths handle karta hai, aur `validate_burning_schedule` se `parse_lines`/`predicted_rounds` import hote hain. Isliye dono `.py` files ek hi `scripts/` folder mein honi chahiye, jaise lab par `~/giraph/` mein thi.

### `load_input(path)`

Path ek file ho to wahi padhta hai. Directory ho to `sorted(path.glob("*.txt"))` saare text parts name order mein leta hai. Har file ki lines `parse_lines` ko deta hai. `yield from stream` ka matlab lines ko ek-ek karke aage pass karna; teeno files ko manually jodna zaroori nahin. Agar input file na mile, error deta hai.

### `simulate_rounds(graph, sources)` — actual round simulation

`burned = {}` dictionary: key vertex ID, value **pehli baar burn hua round**. `frontier = set()` mein **pichhle round mein naye jale** vertices hote hain. Starting mein dono empty hain.

Har round par:

1. `source = sources[round_number]`: input ka is round ka source padho.
2. `reached_from_old_fire`: `frontier` ke vertices ke neighbours ka union. `set().union(...)` repeats hata deta hai. Round 1 mein frontier empty hai, isliye fire spread nahin hoti.
3. `newly = (reached_from_old_fire | {source}) - burned.keys()`: purani fire se reach hue vertices **union** naya source, minus jo pehle hi burn ho chuke. `|` set union hai; `-` set difference hai. Kisi vertex ko dobara first-burn round nahin milta.
4. `burned.update({vertex: round_number for vertex in newly})`: naye vertices ka first burn round store karo.
5. `frontier = newly`: yeh log **agle** round mein spread karenge, isi round mein nahin.
6. `cumulative = set(burned)`: ab tak jale hue IDs.
7. `edges`: original graph mein jin edges ke **dono endpoints** `cumulative` mein hain, unki sorted list. `min/max` edge ko ek canonical pair banata hai taaki undirected edge twice na aaye.
8. `history.append(...)`: round, source, newly, cumulative aur edges save karo.

Finally `predicted_rounds` (BFS-distance method) ke result se simulation compare hoti hai. Dono methods disagree karein to `AssertionError` aata hai. Yeh useful self-check hai, Giraph comparison ka replacement nahin.

### `write_text_files(...)`

`expected.tsv` final sorted output hai: `1<TAB>B<TAB>3` jaisi rows. `.tsv` ka matlab tab-separated values. Isko Giraph ke readable `part-00000` se `diff` kar sakte hain. `round-01-nodes.tsv` mein **har vertex** ka us round ke end par state, first-burn round aur `new_this_round` (`yes/no`) hai. Jo us time tak unburned hai uska temporary round `-1` hai, bhale woh baad mein jale. `round-01-burned-edges.tsv` mein burned induced subgraph ki edges hain. Agle rounds ke liye bhi same files banti hain.

### `write_networkx_files(...)`

NetworkX se original full graph ek baar banta hai. `full.subgraph(cumulative).copy()` har round mein **sirf us time tak burned vertices** aur unke beech ki **saari original edges** nikalta hai; `nx.write_graphml` usko `round-01-burned.graphml` jaisi file mein save karta hai. Edge ka subgraph mein dikhna yeh **nahin** batata ki fire zaroor us particular edge se travelled thi. Yeh sirf current burned vertices ka graph structure hai.

`--png` dene par Matplotlib image save karta hai. `matplotlib.use("Agg")` server par display monitor ke bina PNG banane ke liye hai. `nx.spring_layout(full, seed=42)` ek reproducible layout banata hai aur har round mein wahi positions use hoti hain. Colours: **blue** current source, **orange** is round mein naye jale (source ko blue priority), **yellow** purane burned, **grey** unburned. Dark edge ke dono ends burned hain; light edge ka kam-se-kam ek end unburned hai. `plt.close(figure)` memory release karta hai.

### `main()`

Input path required hai. `--output-dir` na do to terminal par states print hoti hain; directory do to files bhi banti hain. `--networkx` GraphML mangta hai; `--png` image mangta hai. Program existing **non-empty** output directory reject karta hai taaki pehle experiment ki files overwrite na hon. Optional libraries ko output folder banane se pehle import/check karta hai. Error par exit code 2; success par printout.

## 6. Lab par exact workflow aur har command ka reason

`hduser` Hadoop daemons chalata hai: `start-dfs.sh`, `start-yarn.sh`, `jps`, `yarn node -list`. `mca2025` dataset, Python preview aur Giraph client chalata hai. Daemons band hon to HDFS/YARN calls `Connection refused` dete hain; yeh Python algorithm ka bug nahin.

```bash
# mca2025 terminal: ek temporary experiment folder; old files safe rahengi.
mkdir -p "$HOME/giraph_learning_burning"
case_dir=$(mktemp -d "$HOME/giraph_learning_burning/round-preview-XXXXXX")

# HDFS mein jo exact input Giraph ne padha tha, uska local copy lo.
hdfs dfs -get /user/mca2025/giraph_learning/graph_burning_path9_scheduled_input "$case_dir/input"

# Python expected rounds, TSV, NetworkX GraphML aur PNG banaye.
python3 "$HOME/giraph/show_burning_rounds.py" "$case_dir/input" \
  --output-dir "$case_dir/preview" --networkx --png

# Giraph ka pehle se saved readable output local comparison ke liye lo.
hdfs dfs -cat /user/mca2025/giraph_learning/graph_burning_path9_scheduled_output/part-00000 \
  > "$case_dir/actual.tsv"
diff -u "$case_dir/preview/expected.tsv" "$case_dir/actual.tsv"
echo "Comparison exit code: $?"
```

`mkdir -p` parent folder banata hai agar missing ho. `mktemp -d` unique folder banata hai, isliye purane results overwrite nahin hote. `hdfs dfs -get` HDFS→local copy karta hai. `>` shell output ko local file mein likhta hai. `diff -u` do files ke differences dikhata hai: **no diff + exit 0 = identical**. Week 15 mein yahi result mila. Yeh comparison saved Giraph result se tha; naya Giraph run nahin.

Lab PC par pehle `NetworkX: False`, `Matplotlib: False` tha. `python3 -m pip --version` ne pip 22.0.2/Python 3.10 confirm kiya. Phir `python3 -m pip install --user networkx matplotlib` se `mca2025` account ke liye NetworkX 3.4.2 aur Matplotlib 3.10.9 install kiye. `--user` system-wide Python ko change nahin karta. Plain SSH terminal PNG display nahin karta; Windows PowerShell se `scp -r` karke local PC par open kiya. Hadoop/Giraph ko in packages ki zaroorat nahin.

Verified files [`results/graph-burning-path-9-scheduled/round-preview/`](../../results/graph-burning-path-9-scheduled/round-preview/) mein hain: `expected.tsv`, har round ka `*-nodes.tsv`, `*-burned-edges.tsv`, `*-burned.graphml`, aur `round-01.png` to `round-03.png`. Original Giraph result uske parent folder mein `part-00000.txt` hai.

## 7. Common confusion aur next exercise

- **Round 1 mein source ke neighbours?** Nahin. Source pehle khud jalta hai; next round mein fire ek hop spread hoti hai.
- **`NB -1` kya error hai?** Nahin. Is schedule ke last round tak vertex unreachable/unburned hai.
- **PNG ka dark edge fire ka travelled path hai?** Nahin, woh burned induced subgraph ki edge hai.
- **Yeh Week 14 cap `2,1,0` hai?** Nahin. Standard burning mein pehle source ki radius 2 hops, doosre ki radius 1 hop, teesre ki radius 0 hop hai; direct neighbours ki count par cap nahin.
- **Python source choose karta hai?** Nahin. User `source_round` values likhta hai. Random aur optimized selection future phases hain. Agar random implement karein, seed save karenge taaki same run dobara mile.
- **Next khud se try:** pehle small graph par round-1/2/3 ka `frontier`, `newly`, `cumulative` paper par calculate karo. Python printout se check karo. Phir same input Giraph par fresh HDFS paths se run karke final `diff` karo. Large graph ke liye bhi yahi workflow hai, bas manual table ka size badhega.

## 8. Naya 30-node random-source preparer aur verified Giraph run

[`scripts/prepare_random_burning_input.py`](../../scripts/prepare_random_burning_input.py)
**input file banata hai**; Graph Burning calculation/Giraph job nahin chalata.
Iska source `datasets/thirty-node-undirected-burning/` hai: 30 vertices, 55
undirected edges, 3 parts, abhi source-round column nahin. Output
[`datasets/thirty-node-random-burning-seed-20261026/`](../../datasets/thirty-node-random-burning-seed-20261026/)
mein wohi edges aur naya second column hai. `selection.json` seed aur
chosen sequence ka record hai, graph input ka hissa nahin.

Functions samjho:

- `read_graph(input)` existing module ka **sirf parser** use karta hai;
  us module ka greedy/exact selection function call **nahin** hota.
- `select_sources(graph, rounds, seed)` `random.Random(seed)` banata hai.
  Har round mein sorted IDs se un vertices ki `eligible` list banti hai
  jo kisi previous source ki fire se **is round se pehle** nahin jale.
  `rng.choice(eligible)` unmein se ek ko randomly leta hai. Ismein degree,
  PageRank, coverage ya best-score check **nahin** hai. Same seed aur input
  se experiment repeat kiya ja sakta hai. Jab candidate na ho, error.
- `distances_from` sirf eligibility check ke liye BFS hops nikalta hai.
  Earlier source ke round `s` aur distance `d` se vertex ka arrival `s+d`
  hai. `s+d < current_round` ho to us vertex ko naya source nahin bana
  sakte; same-round arrival allowed hai. Yeh validity hai, optimization nahin.
- `prepare_parts` har original line `vertex neighbours...` ko
  `vertex source_round neighbours...` banata hai. Non-selected vertex ko
  `0` milta hai. Phir existing `parse_lines` se **poora** generated graph
  validate hota hai: edges unchanged, 30 vertices, correct markers.
- `main()` arguments padhta hai, existing output path overwrite nahin
  karta, parts aur `selection.json` likhta hai, seed/sequence print karta hai.

Is seed `20261026` aur four rounds se `4:27:12:15` mila. Local Python
preview ne 24 `B` aur six `NB -1` predict kiye; NB IDs 14,18,19,20,24,25.
Lab PC par **same** three parts upload karke Giraph job chalaya. Uska actual
output bhi exactly wahi 30 rows hai. Random ka matlab “guaranteed saara
graph burn” nahin; incomplete coverage bhi valid result hai.

### Is baar lab mein kaunse steps hue, aur kyun?

1. Windows laptop se `scp` ne generated `part-01.txt` se `part-03.txt`
   lab PC ke `~/giraph_learning_burning/week15_random30_input/` mein copy
   kiye. Sirf graph parts transfer hue; source-selection script Giraph job
   ke andar nahin chalta.
2. `python3 ~/giraph/validate_burning_schedule.py INPUT_DIR` ne 30
   vertices, 55 undirected edges, four consecutive source rounds aur
   `4:27:12:15` check kiya. Isse typo ya invalid schedule par expensive
   Giraph run shuru karne ki zaroorat nahin hoti.
3. `python3 ~/giraph/show_burning_rounds.py INPUT_DIR --output-dir PREVIEW_DIR
   --networkx --png` ne expected final rows aur har round ka TSV,
   GraphML, PNG banaya. Yeh Python calculation hai, cluster job nahin.
4. `hdfs dfs -mkdir -p HDFS_INPUT` HDFS mein input folder banata hai;
   `hdfs dfs -put LOCAL_DIR/part-*.txt HDFS_INPUT/` teen parts HDFS mein
   bhejta hai. `hdfs dfs -ls` se confirm hua ki teeno wahan hain.
5. `yarn node -list` ne ek RUNNING worker aur job se pehle 0 containers
   dikhaye. Isse pata chala ki Giraph ko worker mil sakta hai.
6. Neeche wala `bash` command shell runner chalata hai. Runner HDFS input
   dobara validate karta hai; Giraph Java computation run karta hai;
   numeric result ko readable `B`/`NB -1` mein format karta hai. Python
   preparer **is step mein source select nahin karta**: source rounds
   already input lines mein fixed hain.

```bash
bash "$HOME/giraph/run_graph_burning_from_input.sh" \
  /user/mca2025/giraph_learning/graph_burning_30_random_20261026_input \
  /user/mca2025/giraph_learning/graph_burning_30_random_20261026_output
```

7. `hdfs dfs -cat HDFS_OUTPUT/part-00000 > actual.tsv` ne Giraph ke real
   HDFS result ko local file mein copy kiya. `diff -u PREVIEW/expected.tsv
   actual.tsv` ne koi difference print nahin kiya aur exit code `0` diya.
   `0` comparison success hai, “0 burned vertices” nahin. Lab se actual
   file aur pictures Windows par copy karke repo mein save kiye.

Round details (new source ko newly-burned list mein count kiya hai):

| Round | Source | Newly burned | Total burned |
|---:|---:|---|---:|
| 1 | 4 | 4 | 1 |
| 2 | 27 | 3,5,9,27 | 5 |
| 3 | 12 | 1,2,8,10,11,12,22,26,28 | 14 |
| 4 | 15 | 6,7,13,15,16,17,21,23,29,30 | 24 |

Example: node 4 first round mein source ke roop mein jala; node 3 uske
direct neighbour ke roop mein round 2 mein; node 2 uske baad round 3 mein.
Node 14 ko source 15 ke neighbour hone par bhi round 4 mein fire nahin
milti, kyunki 15 **round 4 mein hi** jala aur round 5 allowed nahin hai.
Isliye 14 `NB -1` hai. Isi tarah 18,19,20,24,25 bhi scheduled horizon
mein nahin jale. `round-04.png` mein yeh grey dikhte hain.

Actual rows [`giraph-actual.tsv`](../../results/graph-burning-30-random-seed-20261026/giraph-actual.tsv)
mein hain. [`lab-round-preview/`](../../results/graph-burning-30-random-seed-20261026/lab-round-preview/)
mein four PNG/GraphML aur detailed tables hain. Yeh **one** random seed ka
verified result hai, optimized burning number ka proof nahin. Next study:
same graph par doosra recorded seed run karke compare karna, *without*
calling the better-looking seed globally optimal.

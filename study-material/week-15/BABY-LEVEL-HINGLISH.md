# Week 15: graph burning bilkul shuru se (Hinglish)

## 1. Hum solve kya kar rahe hain?

Graph mein **vertex/node** ek point hai aur **edge** do points ka connection. Hamara 120-node graph 10 rows × 12 columns ka grid hai. Har node apne up/down/left/right neighbours se connected hai, diagonal se nahin. Puri graph mein 218 *undirected* connections hain. Undirected ka matlab `1—2` ko dono taraf se traverse kar sakte hain. Input text mein isi edge ko node 1 ki line aur node 2 ki line, dono mein likhte hain; isliye text mein 436 neighbour mentions honge, par distinct edges 218.

Burning schedule ek list hai: round 1 mein node 15 se fire start, round 2 mein node 104 se, phir 35, 101, 41, 111, 83, 86. Yeh sequence **seeded random eligible choice** se bani hai. Eligible ka matlab us round ke shuru hone se pehle node nahin jala. Random ka matlab best/greedy/optimal **nahin**. Eight rounds ke baad kuch node na jale to woh bhi valid observation hai.

## 2. Fire ka exact rule

Round 1 mein **sirf** first source 15 ignite hota hai. Round 2 mein 15 ke adjacent nodes tak fire jaati hai, aur source 104 bhi ignite hota hai. Round 2 mein jo naye jale, unse fire **round 3 mein** aage jaati hai—same round mein second hop nahin. Aise eight rounds. Ek node kai jagah se fire receive kare to uska **sabse pehla** burn round likhte hain. Source jab ignite hota hai, us round mein apne neighbours ko turant burn nahin karta; uski fire agle round mein spread hoti hai.

Simple example: `1—2—3`. Agar node 1 round 1 source hai, to node 1 round 1, node 2 round 2, node 3 round 3 mein jalta hai. Round 1 mein sabko `B` kehna galat hoga.

## 3. Ek text line ka matlab aur four files kyun?

Scheduled input format: `vertex_id source_round neighbour_id:weight ...`. Example `15 1 3:1 14:1 16:1 27:1`: node 15 round 1 source hai; baaki IDs neighbours hain, `:1` weight hai. Current burning algorithm weight ka value use nahin karta, ek edge ko ek hop manta hai. `0` as **input second column** means “yeh node source nahin hai”; woh neighbour se fire aane par phir bhi jal sakta hai.

120 node lines ko [four files](../../datasets/grid-120-random-burning-seed-20261026/) mein 30–30 divide kiya. Yeh **one dataset** hai, four separate experiments nahin. Python directory ke saare `.txt` parts padhta hai; Giraph HDFS input directory ke chaar parts padhta hai. `selection.json` sirf record hai; HDFS input mein usse daalne par reader error ho sakta hai.

## 4. Python, HDFS, YARN, Giraph — kis ka kya kaam?

1. Windows laptop repo mein graph files aur Python scripts hain. `scp` (secure copy) four parts ko lab PC ke local Linux folder mein bhejta hai. Yeh abhi **HDFS upload nahin** hai.
2. Local Python validator typing mistakes, missing reverse edges, duplicate node IDs aur bad source schedule check karta hai. Python round-preview independent expected answer aur pictures banata hai. Yeh **Hadoop job nahin** hai.
3. `hdfs dfs -put` Linux local files ko HDFS input directory mein bhejta hai. HDFS distributed file system hai. Single-node teaching cluster par bhi Giraph isi path se read karta hai.
4. `hduser` DFS/YARN daemons chalata hai. YARN ka RUNNING NodeManager Giraph worker ko containers deta hai. `mca2025` job submit karta hai.
5. Giraph Java reader each text line ko vertex + edges + source round mein badalta hai. Java computation rounds mein fire messages bhejta hai. Shell runner output ko `B`/`NB` readable format mein likhta hai.
6. `hdfs dfs -cat ... > actual.tsv` HDFS ka actual answer Linux local file banata hai. `diff -u expected.tsv actual.tsv` independent Python aur Giraph answers compare karta hai. Exit **0** = lines same; yeh “zero burning” ka matlab nahin.

## 5. Result ko kaise padhein?

Output ki har line: `vertex_id<TAB>B_or_NB<TAB>first_burn_round`. `15 B 1` means node 15 round 1 mein pehli baar jala. `85 NB -1` means node 85 eight rounds ke end tak nahin jala. Output mein `-1` **result** hai; input mein second-column `0` se confuse mat karo.

Python preview ne 119 burned, 1 unburned predict kiya. Actual Giraph output ki **saari 120 rows** Python se match hui (`diff` exit 0). Lab Python pictures ke [round 1](../../results/grid-120-random-burning-seed-20261026/lab-round-preview/round-01.png) aur [round 8](../../results/grid-120-random-burning-seed-20261026/lab-round-preview/round-08.png) dekho: blue current source, orange current round mein naye burned, yellow pehle se burned, grey unburned. Round 8 mein 85 grey hai. Picture topology samajhne ki help karti hai, lekin proof of agreement `diff` hai.

Round-wise newly burned counts: 1, 5, 12, 20, 26, 30, 20, 5. Sum 119. Yeh chosen schedule ke liye hai. Isse yeh prove nahin hota ki eight rounds minimum hain, ya yahi best sources hain.

## 6. Hum khud kaise practice karein?

Pehle [week report ke repeat commands](../../weekly-reports/2026-10-29-week-15.md#repeat-the-120-node-practical-yourself) one by one follow karo. Har command ke baad expected check likha hai. Original HDFS output path ko dobara mat do—runner existing output ko overwrite nahin karta. New result ke liye **naya output directory name** do. Galti aaye to pehle account (`hduser` ya `mca2025`), current directory, HDFS path, aur `yarn node -list` check karo. Source choose karne ka optimization is experiment ka part nahin.

Code ka har important expression samajhne ke liye [commented-code companion](CODE-WITH-COMMENTS.md) padho; Sir ko explain karne ke liye [faculty brief](FACULTY-BRIEF.md) padho.

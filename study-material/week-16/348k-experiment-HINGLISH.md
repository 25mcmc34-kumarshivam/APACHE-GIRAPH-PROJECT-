# 348k Graph Burning experiment — Hinglish learning notes

Ye page hum dono (Shivam aur Archana) ke liye hai. Weekly report me sirf lab
ka factual record hai; yahan hum samajh rahe hain ki har file aur har step ka
meaning kya tha.

## 1. Is experiment me humne kya kiya?

Humne Stanford SNAP ka `web-Google.txt` liya. Original file bahut badi thi.
Humne converter ko `--max-node-id 500000` diya. Iska matlab exactly 500,000
vertices banana nahi tha; iska matlab tha ki is ID limit ke andar aane wali
edges ko consider karo. Uske baad converter ne:

1. comments aur header ignore kiye;
2. duplicate edges aur self-loop remove kiye;
3. directed SNAP edges ko undirected adjacency me badla;
4. largest connected component rakha; aur
5. graph ko 8 `part-*.txt` files me baanta.

Measured result **348,087 vertices** aur **1,128,693 undirected connections**
tha. Isliye hum report me 500,000 vertices nahi likhenge.

## 2. Source sequence ka meaning

Humne 8 rounds aur seed `20261105` use kiya. Seed ka fayda ye hai ki same
input par dobara same random source sequence mil sakti hai:

```text
96901:113758:455241:73976:310174:473800:320304:118094
```

Ye sequence random baseline hai, optimized ya greedy best sequence nahi hai.
Pehle source ko 7-hop tak, doosre ko 6-hop tak, ... aur aathve source ko
0-hop radius milta hai. Actual burning rule pehle sources ko jalne ke baad
har round me ek edge outward spread karne deta hai.

## 3. Python preview ne itna time kyon liya?

Python preview ka kaam sirf final answer banana nahi tha. Usne poore graph ko
read karke har round ka teaching record banaya. 8 rounds ke liye isne:

- `round-01-nodes.tsv` se `round-08-nodes.tsv` tak node states likhe;
- har round ka `round-XX-burned-edges.tsv` likha; aur
- final `expected.tsv` banaya.

348k vertices ke saath 8 complete node tables bahut bade hote hain. Isliye
preview ko lagbhag 20 minutes lage aur CPU lagbhag 100% dikh raha tha. Ye
stuck nahi tha; files ka size round by round badh raha tha.

Giraph job ka kaam alag tha. Giraph ne wahi calculation Hadoop/YARN ke
distributed vertex computation ke roop me chalayi aur final `part-00000`
likha. Is session me Giraph preview se kaafi jaldi complete hua. Humne Giraph
ka exact stopwatch time record nahi kiya, isliye exact seconds claim nahi
karne chahiye.

## 4. Preview har round me kya calculate karta hai?

Maan lo current round `r` hai.

1. Is round ka scheduled source dekha jata hai.
2. Source ko current round me burn mark kiya jata hai, agar woh pehle nahi
   jala hai.
3. Pichhle rounds me jal chuke vertices apne adjacent neighbours ko ek step
   aage burn karte hain.
4. Naye vertices ko unka **first burn round** diya jata hai. Agar vertex pehle
   hi jal chuka hai to uska round change nahi hota.
5. `burned so far` me union of all burned vertices rakha jata hai.
6. Jo IDs is set me nahi hain woh `unburned` list me rehte hain.
7. Dono endpoints burned hone wali edges ko burned-induced-subgraph file me
   likha jata hai.

Round 8 ke baad final table ka format hota hai:

```text
vertex_id    B-or-NB    first_burn_round
```

`B 4` ka matlab vertex round 4 me pehli baar jala. `NB -1` ka matlab woh
poore scheduled experiment me nahi jala.

## 5. Python aur Giraph ko compare kyon kiya?

Python preview hamara independent expected answer hai. Giraph hamara actual
distributed implementation hai. Agar dono files same hain to hume confidence
milta hai ki Java/Giraph computation ne input schedule ko sahi samjha.

Is experiment me dono files me **348,087 rows** the:

- Python: 243,095 burned, 104,992 unburned
- Giraph: 243,095 burned, 104,992 unburned
- complete file comparison: exit code `0`

Comparison ka matlab optimum solution mil gaya aisa nahi hai. Iska matlab sirf
ye hai ki random schedule ke liye Python prediction aur Giraph execution
ekdum same hain.

## 6. Files kahan hain?

Dataset ke 8 HDFS-ready parts:

`datasets/web-google-348k-burning-20261029/part-01.txt` ... `part-08.txt`

Python expected output aur round evidence:

`results/web-google-348k-burning-20261029/python-preview/`

Giraph ka actual output:

`results/web-google-348k-burning-20261029/giraph-actual.tsv`

Short factual summary:

`results/web-google-348k-burning-20261029/README.md`

Complete commands aur lab errors:

`weekly-reports/2026-11-05-week-16.md`

## 7. Hum khud kaise pehchanenge ki job stuck hai?

Python preview ke liye doosre terminal me `ps -p PID -o pid,etime,%cpu,rss,cmd`
dekh sakte hain. CPU high ho aur output files ka size/modified time badh raha
ho to process kaam kar raha hai. Giraph ke liye `yarn application -list
-appStates ACCEPTED,RUNNING` aur `yarn node -list` dekhna hai. Node RUNNING
ho aur application progress badhe to job chal rahi hai.

## 8. Sabse important learning

Python preview verification/reference model hai; Apache Giraph final
distributed graph computation hai. Preview ka detailed round evidence banana
slow ho sakta hai, lekin usi evidence se hum samajhte hain ki round 1, round 2
... round 8 me graph ka burned subgraph kaise badla. Giraph ka matching output
hamare implementation ko validate karta hai.


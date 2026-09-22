# `run_graph_burning.sh` — Hinglish line-by-line guide

Executable script: [`scripts/run_graph_burning.sh`](../../scripts/run_graph_burning.sh).
Is guide ke comments teaching ke liye hain; actual run hamesha `.sh` file
se karo. Script Java logic nahi banata. Yeh Java/Giraph job ko sahi input,
output aur options ke saath **launch** karta hai.

## Command me teen arguments

```bash
bash "$HOME/giraph/run_graph_burning.sh" INPUT_HDFS OUTPUT_HDFS 3:8:6
```

`bash` script chalata hai. `$HOME` mca2025 ka home directory hai. `$1` input
HDFS path, `$2` new output HDFS path, `$3` ordered sources. `3:8:6` ka matlab
round 1 source 3, round 2 source 8, round 3 source 6. Colon isliye use hota
hai kyunki Giraph `-ca` me comma settings separate karta hai.

## Safety line

```bash
set -euo pipefail # command fail, missing variable, ya failed pipeline par ruko
```

Isse galat input par script aage job submit nahi karega. `-e` command error,
`-u` unset variable, `pipefail` pipeline ke andar ka error pakadta hai.

## Environment

`JAVA_HOME` Java 8 ka folder hai. `HADOOP_HOME` Hadoop install folder.
`HADOOP_CONF_DIR` Hadoop XML configuration ka folder. `PATH` me Java/Hadoop
binary directories add karte hain taaki `java`, `hdfs`, `yarn`, `hadoop`
commands milen. `${JAVA_HOME:-default}` ka matlab: existing value ho to
use karo, warna lab ka known default use karo. Ye files install nahi karta.

## Input checks

```bash
test -f "$GIRAPH_JAR"      # compiled JAR local disk par hai?
hdfs dfs -test -e "$INPUT_PATH"   # HDFS input maujood hai?
hdfs dfs -test -e "$OUTPUT_PATH"  # output ALREADY hai? To naya naam do.
yarn node -list           # YARN ek RUNNING node report karta hai?
```

Existing output path par Hadoop overwrite nahi karta. Isliye har experiment
ka output alag naam lo. YARN ka `RUNNING` text check ek quick check hai;
stale record possible hai. Jab job `ACCEPTED` par atke, real NodeManager
process bhi check karo: `ps -ef | grep '[N]odeManager'`. Yeh known lab issue
hai; [daily startup guide](../../docs/DAILY-LAB-STARTUP.md) me recovery hai.

## Main `hadoop jar` command ka map

| Part | Matlab |
|---|---|
| `hadoop jar "$GIRAPH_JAR"` | built Giraph example JAR start karo |
| `org.apache.giraph.GiraphRunner` | Giraph ka command-line entry point |
| `org.apache.giraph.examples.LearningGraphBurningComputation` | hamara Java fire rule |
| `-vif ...LongDoubleFloatTextInputFormat` | text adjacency-list lines read karo |
| `-vip "$INPUT_PATH"` | HDFS input directory |
| `-vof ...IdWithValueTextOutputFormat` | vertex ID aur burn round print karo |
| `-op "$OUTPUT_PATH"` | naya HDFS output directory |
| `-w 1` | single-node lab me one Giraph worker |
| `-ca mapred.job.tracker=yarn` | is old Giraph/Hadoop combination ko YARN mode do |
| `-ca "LearningGraphBurning.sourceSequence=$SOURCE_SEQUENCE"` | Java ko sources pass karo |

End me `hdfs dfs -cat "$OUTPUT_PATH"/part-m-*` result files read karta hai,
aur `sort -n` vertex IDs numeric order me display karta hai. `cat` aur
`sort` HDFS result **change nahi** karte. Output me `1.0` = round 1,
`2.0` = round 2. Bahut bada `1.7976931348623157E308` = unburned marker.

## Kab rebuild karna hai?

- Sirf graph `.txt` badla: Java rebuild nahi.
- Sirf `3:8:6` sequence badla: Java rebuild nahi.
- Sirf shell script comment badla: Java rebuild nahi.
- `LearningGraphBurningComputation.java` ka executable logic badla: Maven
  rebuild aur naya JAR chahiye.

Detail: [Maven build workflow](../maven-build-workflow.md).

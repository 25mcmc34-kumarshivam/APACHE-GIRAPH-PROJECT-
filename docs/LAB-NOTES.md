# Giraph Lab Notes

## What was already installed

The server already contained Hadoop 2.7.7 under `/usr/local/hadoop`, Giraph source under `/home/mca2025/giraph`, Maven, Git and multiple Java versions. Hadoop data and daemons belong to `hduser`; Giraph development belongs to `mca2025`.

## Repairs completed

Java 8 was placed first in `PATH`, and Hadoop's `hadoop-env.sh` was corrected. HDFS and YARN were started and verified. Giraph initially failed because its Guava 21 API was incompatible with Hadoop's Guava 11.0.2. The build was changed to relocate Giraph's Guava classes into a private package. The verified runnable artifact is:

```text
/home/mca2025/giraph/giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar
```

## Daily startup check

Run Hadoop services as `hduser`, then verify:

```bash
jps
hdfs dfsadmin -report
yarn node -list
```

One NameNode, DataNode, SecondaryNameNode, ResourceManager and NodeManager should be running. `yarn node -list` should show exactly one `RUNNING` node before a job is submitted.

## NodeManager problem observed

NodeManager sometimes stopped during container cleanup, leaving a job in `ACCEPTED`. Repeatedly starting NodeManager created stale registrations. The reliable recovery used in the lab was a clean YARN restart as `hduser`:

```bash
stop-yarn.sh
start-yarn.sh
yarn node -list
```

## Result interpretation

`1.7976931348623157E308` is Java's `Double.MAX_VALUE`. In the shortest-path output it means that the vertex is unreachable from the selected source; it is not a real path length.

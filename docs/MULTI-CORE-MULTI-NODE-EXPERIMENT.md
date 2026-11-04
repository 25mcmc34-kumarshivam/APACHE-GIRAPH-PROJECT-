# Multi-core and multi-node experiment plan

This note explains what “more processing” means in our Giraph setup.

## Three different ideas

### More YARN containers on one computer

Our current lab PC is one physical machine with one registered NodeManager.
YARN can sometimes use several containers and CPU cores on that same machine,
but that is still one node and is limited by its RAM, CPU and disk.

### Multiple threads in one program

Java or Python threads share one machine's memory. Adding threads to a Giraph
vertex computation is not the same as creating a Hadoop cluster. Giraph already
divides work among task containers.

### A true multi-node YARN cluster

A distributed experiment has several worker machines. Each worker runs a
DataNode and NodeManager. `yarn node -list` must show several RUNNING
NodeManagers before we call a job multi-node.

## Why our current run used one node

Our lab installation is pseudo-distributed: Hadoop services run on one PC.
The 348,087-vertex job completed in about 55 seconds, but a 4-million-vertex
graph will not necessarily take exactly ten times as long. Edge count, rounds,
memory, disk and network all matter.

## Suggested experiment sequence

1. 348k vertices — already verified.
2. Approximately 1 million vertices — measure memory and wall-clock time.
3. Approximately 2 million vertices — check for YARN/container failures.
4. Only then attempt the 4-million-vertex graph.

For every run, record `real` time, vertex/edge counts, rounds,
burned/unburned counts, YARN node count and whether Python and Giraph match.

## What a multi-node test requires

- one NameNode/ResourceManager host;
- at least two worker hosts;
- passwordless SSH between Hadoop service accounts;
- matching Java, Hadoop and Giraph versions;
- consistent Hadoop configuration on every host;
- one DataNode and NodeManager process on every worker;
- enough aggregate RAM and local disk.

The current PC is not incapable of multi-core work; no additional worker
machines are configured. A GPU will not automatically accelerate Giraph:
Giraph runs in Hadoop Java containers on CPU. GPU use would require a separate
GPU-oriented implementation.

## Checks before a timed run

```bash
jps
yarn node -list
free -h
df -h "$HOME"
```

If zero nodes are RUNNING, fix YARN first. If one node is RUNNING, the run is
single-node. If several are RUNNING, record their IDs before calling it
multi-node.

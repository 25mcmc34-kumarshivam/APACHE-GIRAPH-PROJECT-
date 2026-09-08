# Hadoop and Giraph Installation Guide

This guide reproduces the software arrangement used in the lab. Read each verification result before continuing. Do not paste the whole document into a terminal at once.

## 1. Target arrangement

The reference machine uses two Linux accounts:

- `hduser` owns `/usr/local/hadoop`, Hadoop data, and the Hadoop daemons.
- `mca2025` owns `/home/mca2025/giraph`, builds Giraph, and submits jobs.

Software versions verified in the lab:

- Ubuntu 22.04 LTS, x86-64
- OpenJDK 8
- Hadoop 2.7.7
- Maven 3.6.3 or later
- Git 2.34.1 or later
- Giraph 1.4.0-SNAPSHOT, `trunk` branch

These are older components. Use the same versions for reproduction instead of silently replacing them with current releases.

## 2. Create the Hadoop account

Run from an administrator account:

```bash
sudo addgroup hadoop
sudo adduser hduser
sudo usermod -aG hadoop hduser
id hduser
```

`addgroup` creates the service group. `adduser` creates the account and home directory. `usermod -aG` adds the account to the group without removing its other group memberships.

## 3. Install basic tools

```bash
sudo apt update
sudo apt install git maven openssh-server wget tar unzip
```

OpenJDK 8 must also be installed. On some Ubuntu 22.04 installations it is not available from the enabled repositories, so do not substitute Java 21. Confirm the required result:

```bash
/usr/lib/jvm/java-8-openjdk-amd64/bin/java -version
/usr/lib/jvm/java-8-openjdk-amd64/bin/javac -version
```

Both commands must report version 1.8.

## 4. Configure passwordless localhost SSH

Start the SSH service:

```bash
sudo systemctl enable ssh
sudo systemctl start ssh
sudo systemctl status ssh
```

Switch to `hduser`, then create the local key:

```bash
su - hduser
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
ssh-keygen -t rsa -P '' -f "$HOME/.ssh/id_rsa"
cat "$HOME/.ssh/id_rsa.pub" >> "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"
ssh -o BatchMode=yes -o ConnectTimeout=5 localhost 'echo "Passwordless SSH works"'
```

Do not upload `.ssh`, `id_rsa`, passwords, or private keys to GitHub.

## 5. Install Hadoop 2.7.7

Download the exact archive from Apache and place it under `/usr/local`:

```bash
cd /tmp
wget https://archive.apache.org/dist/hadoop/common/hadoop-2.7.7/hadoop-2.7.7.tar.gz
sudo tar -xzf hadoop-2.7.7.tar.gz -C /usr/local
sudo mv /usr/local/hadoop-2.7.7 /usr/local/hadoop
sudo chown -R hduser:hadoop /usr/local/hadoop
```

Verify:

```bash
/usr/local/hadoop/bin/hadoop version
ls -ld /usr/local/hadoop
```

## 6. Set the hduser environment

Add these lines once at the end of `/home/hduser/.bashrc`:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=/usr/local/hadoop
export HADOOP_CONF_DIR="$HADOOP_HOME/etc/hadoop"
export PATH="$JAVA_HOME/bin:$HADOOP_HOME/bin:$HADOOP_HOME/sbin:$PATH"
```

Reload and verify:

```bash
source "$HOME/.bashrc"
hash -r
java -version
hadoop version
```

In `/usr/local/hadoop/etc/hadoop/hadoop-env.sh`, set:

```bash
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
```

## 7. Configure Hadoop

Before editing, back up `/usr/local/hadoop/etc/hadoop`:

```bash
cp -a /usr/local/hadoop/etc/hadoop "$HOME/hadoop-config-backup"
```

Use the following single-node configuration.

### `core-site.xml`

File: `/usr/local/hadoop/etc/hadoop/core-site.xml`

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>fs.defaultFS</name>
    <value>hdfs://localhost:9000</value>
  </property>
  <property>
    <name>hadoop.tmp.dir</name>
    <value>/home/hduser/hadoop_tmp</value>
  </property>
</configuration>
```

### `hdfs-site.xml`

File: `/usr/local/hadoop/etc/hadoop/hdfs-site.xml`

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:/home/hduser/hadoop_tmp/dfs/name</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:/home/hduser/hadoop_tmp/dfs/data</value>
  </property>
</configuration>
```

### `mapred-site.xml`

Create it from the supplied template if it does not exist:

```bash
cp /usr/local/hadoop/etc/hadoop/mapred-site.xml.template \
  /usr/local/hadoop/etc/hadoop/mapred-site.xml
```

File: `/usr/local/hadoop/etc/hadoop/mapred-site.xml`

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>mapreduce.framework.name</name>
    <value>yarn</value>
  </property>
</configuration>
```

### `yarn-site.xml`

File: `/usr/local/hadoop/etc/hadoop/yarn-site.xml`

```xml
<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>
<configuration>
  <property>
    <name>yarn.nodemanager.aux-services</name>
    <value>mapreduce_shuffle</value>
  </property>
  <property>
    <name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
    <value>org.apache.hadoop.mapred.ShuffleHandler</value>
  </property>
  <property>
    <name>yarn.resourcemanager.hostname</name>
    <value>localhost</value>
  </property>
  <property>
    <name>yarn.nodemanager.resource.memory-mb</name>
    <value>8192</value>
  </property>
  <property>
    <name>yarn.scheduler.maximum-allocation-mb</name>
    <value>8192</value>
  </property>
</configuration>
```

The `8192` MB values match the reference machine. Reduce both values on a machine with less available RAM.

The important settings are:

- `fs.defaultFS = hdfs://localhost:9000`
- `hadoop.tmp.dir = /home/hduser/hadoop_tmp`
- `dfs.replication = 1`
- `mapreduce.framework.name = yarn`
- one local YARN NodeManager

Create Hadoop's local data directory as `hduser`:

```bash
mkdir -p /home/hduser/hadoop_tmp
```

### One-time NameNode format

Only on a new installation with no HDFS data:

```bash
hdfs namenode -format
```

Never repeat this command on the working lab server. Formatting creates new NameNode metadata and can make existing HDFS data inaccessible.

## 8. Start and verify Hadoop

Run as `hduser`:

```bash
start-dfs.sh
start-yarn.sh
jps
hdfs dfsadmin -report
yarn node -list
```

Expected Java processes are NameNode, DataNode, SecondaryNameNode, ResourceManager, and NodeManager. `yarn node -list` should show exactly one `RUNNING` node.

## 9. Obtain and build Giraph

Run as `mca2025`:

```bash
cd "$HOME"
git clone https://github.com/apache/giraph.git
cd "$HOME/giraph"
git branch --show-current
```

The lab used the `trunk` branch. The unmodified Giraph build is not sufficient for this Hadoop 2.7.7 installation because Giraph expects Guava 21 while Hadoop supplies Guava 11.0.2. The lab repair included:

1. Setting `dep.guava.version` to `11.0.2` in the root `pom.xml`.
2. Rewriting incompatible formatted `Preconditions.checkState` calls in `AllWorkersInfo.java` using string concatenation.
3. Adding Maven Shade Plugin 3.2.4 to `giraph-examples/pom.xml`.
4. Relocating `com.google.common` to `org.apache.giraph.shaded.com.google.common`.
5. Producing the classifier `hadoop-guava-shaded`.

Build after applying those changes:

```bash
cd "$HOME/giraph"
mvn clean -Phadoop_2 -DskipTests -Dgiraph.maven.duplicate.finder.skip=true package
```

Verify the artifact:

```bash
ls -lh giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar
jar tf giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar | grep -m 1 '^org/apache/giraph/shaded/com/google/common/'
jar tf giraph-examples/target/giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar | grep -m 1 '^com/google/common/' || echo "No conflicting Guava classes"
```

## 10. Copy this repository's learning files

Clone the learning repository separately:

```bash
cd "$HOME"
git clone https://github.com/25mcmc34-kumarshivam/APACHE-GIRAPH-PROJECT-.git giraph-learning-lab
```

Copy the custom Java classes into Giraph before building:

```bash
cp "$HOME/giraph-learning-lab/src/"*.java \
  "$HOME/giraph/giraph-examples/src/main/java/org/apache/giraph/examples/"
```

Upload the example graph to HDFS:

```bash
hdfs dfs -mkdir -p /user/mca2025/giraph_learning/five_node_input
hdfs dfs -put "$HOME/giraph-learning-lab/datasets/five_node_graph.json" \
  /user/mca2025/giraph_learning/five_node_input/
hdfs dfs -cat /user/mca2025/giraph_learning/five_node_input/five_node_graph.json
```

## 11. Run PageRank

Make the script executable and provide a new output path:

```bash
chmod +x "$HOME/giraph-learning-lab/scripts/"*.sh
"$HOME/giraph-learning-lab/scripts/run_pagerank.sh" \
  /user/mca2025/giraph_learning/five_node_input/five_node_graph.json \
  /user/mca2025/giraph_learning/five_node_pagerank_output
```

Hadoop requires the output directory not to exist before job submission. Use a new name, or deliberately remove only the old experimental output after checking its exact path.

## 12. Troubleshooting sequence

Use these checks before changing configuration:

```bash
java -version
hadoop version
jps
hdfs dfsadmin -report
yarn node -list
yarn application -list -appStates ACCEPTED,RUNNING
```

If YARN shows zero nodes or duplicate/stale registrations, stop creating additional NodeManagers. As `hduser`, perform a clean restart:

```bash
stop-yarn.sh
start-yarn.sh
yarn node -list
```

Wait only when the application is `RUNNING`. If it remains `ACCEPTED`, check resource and NodeManager health instead of waiting indefinitely.

# Starting and Ending a Giraph Lab Session

This checklist is for normal work after the machine has already been installed
and configured. Hadoop daemons belong to `hduser`; Giraph development and job
submission belong to `mca2025`.

## 1. Find the server's current IP address

The CI Lab network assigns dynamic addresses, so the IP may change after a
restart or DHCP renewal. At the physical server, run:

```bash
hostname -I
ip -br address show up
```

The reference machine may show both:

- wired Ethernet interface `enp0s31f6`;
- Wi-Fi interface `wlp3s0`.

Prefer the wired address when the Ethernet cable is connected. An address from
a previous day must not be assumed to remain valid.

## 2. Connect from Windows

Replace `CURRENT_IP` with the address found above:

```powershell
& "C:\Windows\System32\OpenSSH\ssh.exe" mca2025@CURRENT_IP
```

Enter the password only in the terminal. Never save it in GitHub or project
documentation.

## 3. Start Hadoop as hduser

After login as `mca2025`:

```bash
su - hduser
```

Then start storage and resource services:

```bash
start-dfs.sh
start-yarn.sh
```

Verify:

```bash
jps
yarn node -list
```

Expected `jps` processes:

- NameNode
- DataNode
- SecondaryNameNode
- ResourceManager
- NodeManager

Expected YARN state: exactly one `RUNNING` node and zero containers before a
new job.

## 4. Return to mca2025

```bash
exit
```

The prompt should return to `mca2025`. Verify client access:

```bash
java -version
hadoop version
hdfs dfsadmin -report
yarn node -list
```

`jps` under `mca2025` normally shows only `Jps`. That is not a failure. Hadoop
daemons were started and are owned by `hduser`, and `jps` commonly lists JVMs
visible for the current user. Use cluster commands or this process check:

```bash
ps -fu hduser | grep -E 'NameNode|DataNode|ResourceManager|NodeManager'
```

## 5. Before every Giraph job

```bash
yarn application -list -appStates ACCEPTED,RUNNING
yarn node -list
```

Do not submit if NodeManager is missing, a stale node is displayed, or old
containers never clear.

## 6. Known NodeManager recovery

On the reference machine, NodeManager sometimes stops during container cleanup.
Symptoms include no real NodeManager process, a stale YARN node, three reported
containers, or a new application remaining in `ACCEPTED`.

Kill only the waiting application if necessary. Then, as `hduser`:

```bash
stop-yarn.sh
start-yarn.sh
yarn node -list
```

Submit again only after one `RUNNING` node with zero containers appears. Do not
start additional NodeManagers repeatedly.

## 7. End the lab session

First confirm no application is running:

```bash
yarn application -list -appStates ACCEPTED,RUNNING
```

If the machine must be shut down, switch to `hduser` and stop services cleanly:

```bash
stop-yarn.sh
stop-dfs.sh
```

Do not format the NameNode. `hdfs namenode -format` is an installation-time
operation and can make existing HDFS data inaccessible.

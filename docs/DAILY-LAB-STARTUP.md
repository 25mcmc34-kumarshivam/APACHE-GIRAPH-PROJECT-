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

## 6. Known NodeManager cleanup problem and recovery

On the reference machine, NodeManager has sometimes stopped during container
cleanup. The log
shows `RECEIVED SIGNAL 15: SIGTERM` inside
`DefaultContainerExecutor.killContainer`, followed by container exit code 143
and the NodeManager shutdown message. The containers were within their memory
limits, so this was not an out-of-memory failure or a Giraph algorithm error.

Symptoms include no real NodeManager process, a stale YARN node, three reported
containers, or a new application remaining in `ACCEPTED`. Confirm the real
process first:

```bash
ps -ef | grep '[N]odeManager'
```

If no process is printed but ResourceManager is still running, restart only
NodeManager as `hduser`:

```bash
yarn-daemon.sh start nodemanager
yarn node -list
```

After restarting NodeManager, `yarn node -list` may temporarily display two
`RUNNING` entries for the same host: the new node with zero containers and an
old registration still showing three. Do not assume this means two real
NodeManager processes. Compare it with the `ps` check above. On 22 September,
YARN showed nodes on ports `34713` and `43155`, but `ps` showed only one real
NodeManager (PID `12886`). Those numbers are examples, not fixed settings.

If YARN contains stale registrations or does not recover, first check for live
work:

```bash
yarn application -list -appStates ACCEPTED,RUNNING
```

Do not restart YARN while an application is active without deciding what to do
with that application. If no jobs are active, perform a clean YARN restart as
`hduser`:

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

# Weekly Project Timeline

## How this timeline is maintained

The project record begins on **17 July 2026**. Every reporting week runs from Friday through Thursday so that it closes at the weekly Thursday 9:00 AM meeting.

Entries below are reconstructed from terminal output, file timestamps, conversation records, and verified results. Work is never invented to fill an empty week. If earlier notes are unavailable, the entry says so and can be corrected when notebooks, messages, or supervisor notes are found.

Status labels:

- **Verified:** supported by a command result, file, commit, or saved output.
- **Reported:** supplied by a team member but not yet supported by repository evidence.

## Earlier faculty direction — 29 May 2026

Before the formal weekly record began, the supervisor shared the initial areas to learn:

- parallel computing with OpenMP and MPI;
- distributed computing;
- IntelliJ IDEA editor;
- MapReduce framework;
- Apache Giraph framework.

This direction established that the project required both conceptual study and practical implementation.

## Semester milestones

| Period | Milestone | Status |
|---|---|---|
| 17 July 2026 | Project record begins | Reported |
| July–September 2026 | Common setup and graph-processing foundations | In progress |
| Late November/early December 2026 | First major/internal evaluation (6 credits) | Exact date to be announced |
| May 2028 | Second major/external evaluation (6 credits) | Confirmed by the team; official notice remains authoritative |

## Week 1 — 17–23 July 2026

**Status:** Reported by the team

- Began by understanding the approved project title, expected outcome, and why distributed graph processing is needed.
- Studied basic Linux terminal ideas and commands because the implementation environment was Linux.
- Discussed graphs, social-network problems, vertices, edges, and the broad purpose of Giraph.
- Identified the need to learn continuously instead of only installing software.
- Next direction: collect introductory material on Java, Hadoop, MapReduce, parallel/distributed computing, Pregel, and Giraph.

## Week 2 — 24–30 July 2026

**Status:** Reported by the team

- Collected introductory learning material from the internet.
- Studied the difference between ordinary programs, parallel computing, and distributed computing.
- Learned the basic roles of Java, Git, Maven, Hadoop, MapReduce, HDFS, YARN, Pregel, and Apache Giraph.
- Noted that much of the available Giraph setup material was old, often dating from around 2013 and using obsolete Hadoop/Java combinations.
- Began identifying a compatible software stack instead of following old commands unchanged.
- Next direction: start installation and test it on an available Linux machine.

## Week 3 — 31 July–6 August 2026

**Status:** Reported and partly verified

- The faculty provided access to one Linux system in the CI Lab, SCIS.
- Began converting this machine into the shared project environment.
- Installed and checked basic requirements including Java, Git, Maven, Hadoop, SSH, and Giraph source/build dependencies.
- Compared older online instructions with the actual Ubuntu system and adjusted versions and paths where required.
- Created the `mca2025` development location and began building Giraph.
- Giraph artifacts dated 5 August and source commit `14a74297` confirm that the build work reached a working stage during this period.
- Next direction: configure Hadoop users, HDFS/YARN, remote access, and shared working arrangements.

## Week 4 — 7–13 August 2026

**Status:** Reported and supported by the 14 August progress email

- Created the Hadoop group and configured the team accounts available on the shared system.
- Kumar Shivam, Archana Kumari, and Suyash Singh used accounts on the lab system; Aman Chaudhary had the setup on his own laptop.
- Configured the lab computer as a shared SSH-accessible server so members could work from their laptops instead of crowding around one machine.
- Created separate user spaces in HDFS while keeping users under the common Hadoop group.
- Tested Hadoop services, HDFS, YARN, Giraph, and remote login from different accounts.
- Examined available Giraph examples, including connected-components-related material.
- Sent a written project progress update on 14 August summarizing the first month.
- Next direction: attempt an actual graph program from personal accounts and solve access problems.

## Week 5 — 14–20 August 2026

**Status:** Reported by the team

- Continued remote SSH access and tried to run work from individual accounts/laptops.
- Faced permission restrictions because the Giraph source and some directories under `mca2025` were not accessible in the way other users expected.
- Learned that Linux user ownership, Hadoop-group membership, local filesystem permissions, and HDFS permissions are separate concerns.
- Attempted a PageRank program but encountered multiple setup/runtime problems.
- During the 20 August meeting, the supervisor asked the team to try working with the Pregel model/framework.
- Next direction: study Pregel and find a usable setup or implementation path.

## Week 6 — 21–27 August 2026

**Status:** Reported by the team; meeting skipped

- Searched for a practical Pregel setup and tried to understand its relationship with Giraph.
- Could not find a directly usable standalone Pregel setup because Pregel is primarily Google's graph-processing model/system, while Giraph is the open-source framework available for this project.
- Continued dealing with multi-user access and installation complexity.
- The Thursday meeting on 27 August was skipped because of internal examinations in regular MCA subjects.
- Next direction: return to the working Giraph environment, simplify account usage, and diagnose the PageRank failure systematically.

## Week 7 — 28 August–3 September 2026

**Status:** Reported and verified

- Simplified the work by concentrating Hadoop service operations under `hduser` and Giraph source/build work under `mca2025`.
- Connected through SSH and audited the installed software, files, accounts, environment, HDFS, and YARN.
- Confirmed Hadoop 2.7.7, Giraph `trunk`, existing build artifacts, and passwordless localhost SSH.
- Found Java 8/Java 21 path inconsistency, malformed `hadoop-env.sh`, and duplicated `.bashrc` lines.
- Backed up configuration files before correcting Java and Hadoop environment settings.
- Restarted services and confirmed that Hadoop daemons used Java 8.
- Checked HDFS health and created a clean learning directory.
- Reported the current status in the 3 September meeting.
- Next direction: run one small graph from input to output and explain every step.

## Week 8 — 4–10 September 2026

**Status:** Verified

### Dataset and first PageRank work

- Created and uploaded a tiny social graph in Giraph JSON format.
- Verified the example Giraph classes in the existing JAR.
- Learned the difference between local storage and HDFS paths.
- Confirmed that `hduser` operates Hadoop and `mca2025` owns/builds Giraph.

### Errors diagnosed

- Giraph initially selected LocalJobRunner because `mapred.job.tracker` resolved to `local`.
- Jobs remained `ACCEPTED` when no healthy NodeManager was registered.
- Repeated NodeManager starts produced stale/duplicate node registrations.
- The first YARN execution failed with a Guava `NoSuchMethodError` involving `Preconditions.checkState`.
- Removing Guava classes from the fat JAR did not solve the API mismatch.

### Compatibility repair

- Aligned the Guava dependency with Hadoop 2.7.7 where necessary.
- Rewrote incompatible formatted `Preconditions.checkState` calls.
- Added Maven Shade Plugin relocation for Giraph's Guava classes.
- Built and verified `giraph-examples-1.4.0-SNAPSHOT-hadoop-guava-shaded.jar`.
- Confirmed relocated Guava classes exist and conflicting original package classes do not.

### Algorithms completed

- PageRank on the four-node and five-node graphs.
- Custom out-degree computation.
- Custom in-degree computation using two supersteps and messages.
- Single-source shortest paths from vertices 1 and 5.
- Created reusable PageRank and shortest-path scripts.
- Manually interpreted unreachable distance as Java `Double.MAX_VALUE`.

### Documentation and version control

- Updated the detailed Google installation/learning manual.
- Created the GitHub repository.
- Added datasets, source, scripts, verified results, installation instructions, lab notes, and study guides.

### Presentation plan

- Prepared the week's main progress for presentation in the 10 September meeting.
- The key outcome was not only a successful command: the team isolated Java, YARN, NodeManager, permission, LocalJobRunner, and Guava compatibility problems and recorded their fixes.

## Week 9 — 11–17 September 2026

**Status:** Planned

- [ ] Confirm the exact project title and approved problem statement.
- [x] Record the approved project title and supplied problem statement.
- [ ] Confirm the exact internal evaluation date when announced.
- [ ] Add the actual Hadoop configuration files to the repository.
- [ ] Add reusable in-degree and out-degree scripts.
- [ ] Create an automated tiny-graph result checker.
- [ ] Begin the Linux and Java foundation checklist.
- [ ] Prepare a concise demonstration for the Thursday meeting.

## Future weekly entry template

Copy this section for every new week:

```markdown
## Week N — DD–DD Month YYYY

**Group:** A / B / Shared  
**Meeting:** Thursday, 9:00 AM, supervisor's chamber  
**Status:** Planned / In progress / Verified / Blocked

### Goal agreed in the previous meeting

- 

### Concepts studied

- 

### Work completed

- 

### Commands, code, dataset, and results

- Commit:
- Dataset/version:
- Command/script:
- Output:

### Problem faced

- Symptom:
- Cause:
- Fix:
- Evidence that the fix worked:

### What we can explain without copying

- 

### Supervisor feedback/decision

- 

### Tasks before next Thursday

- [ ] Task — owner — due date
```

## Continuous weekly process

The project is expected to progress every week, not only immediately before evaluation. Each weekly cycle includes:

- learning the concepts needed for the assigned task;
- teaching and clarification during supervision;
- implementation and experiments during the week;
- an honest status update, including unfinished work;
- evidence through commits, commands, datasets, and results;
- feedback from the supervisor;
- a defined task for the following week.

The team should update the report before every Thursday meeting, then add the supervisor's feedback after the meeting.

## Reporting rule

A weekly report is complete only when it contains evidence. “Installed Hadoop” is not enough. Record the version command, daemon check, relevant configuration, error if any, and the output that proved success.

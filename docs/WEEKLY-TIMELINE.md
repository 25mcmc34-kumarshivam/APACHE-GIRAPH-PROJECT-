# Weekly Project Timeline

## How this timeline is maintained

The project record begins on **17 July 2026**. Every reporting week runs from Friday through Thursday so that it closes at the weekly Thursday 9:00 AM meeting.

Entries below are reconstructed from terminal output, file timestamps, conversation records, and verified results. Work is never invented to fill an empty week. If earlier notes are unavailable, the entry says so and can be corrected when notebooks, messages, or supervisor notes are found.

Status labels:

- **Verified:** supported by a command result, file, commit, or saved output.
- **Reported:** supplied by a team member but not yet supported by repository evidence.
- **Record needed:** no reliable activity record is currently available.

## Semester milestones

| Period | Milestone | Status |
|---|---|---|
| 17 July 2026 | Project record begins | Reported |
| July–September 2026 | Common setup and graph-processing foundations | In progress |
| Late November/early December 2026 | First major/internal evaluation (6 credits) | Exact date to be announced |
| May 2028 | Second major/external evaluation (6 credits) | Confirmed by the team; official notice remains authoritative |

## Week 1 — 17–23 July 2026

**Status:** Record needed

- Project starting discussions occurred around this period.
- Exact title, problem statement, assigned reading, and meeting decisions still need to be recovered.
- No command output from this week is presently stored in the repository.

## Week 2 — 24–30 July 2026

**Status:** Record needed

- Add details from personal notebooks, WhatsApp/email discussions, or supervisor meeting notes.
- Do not claim installation or experiments without evidence.

## Week 3 — 31 July–6 August 2026

**Status:** Partly verified

- Giraph source existed under `/home/mca2025/giraph`.
- Repository branch was `trunk` at commit `14a74297` (`GIRAPH-1253`).
- Giraph build artifacts had timestamps from 5 August 2026.
- Initial Hadoop/Giraph setup work had therefore started by this period.
- Exact commands and division of work still need to be recovered.

## Week 4 — 7–13 August 2026

**Status:** Partly verified

- HDFS directories `/tmp`, `/user`, `/input`, and `/team` existed.
- `/user/hduser` and YARN staging data were present.
- The system was being used as a single-node Hadoop environment.
- Exact weekly meeting decisions require earlier notes.

## Week 5 — 14–20 August 2026

**Status:** Record needed

- No reliable chronological record is currently available.
- Add only evidence-backed activities.

## Week 6 — 21–27 August 2026

**Status:** Record needed

- No reliable chronological record is currently available.
- Add only evidence-backed activities.

## Week 7 — 28 August–3 September 2026

**Status:** Verified

- Connected to the Ubuntu server through SSH.
- Inspected Giraph source, branch, commit, working tree, and build artifacts.
- Confirmed Hadoop 2.7.7 and passwordless localhost SSH.
- Found that `JAVA_HOME` pointed to Java 8 while `java` selected Java 21.
- Found a malformed `hadoop-env.sh` assignment and duplicated `.bashrc` entries.
- Backed up the environment files and corrected Java/Hadoop environment values.
- Restarted Hadoop services and confirmed all HDFS/YARN daemons used Java 8.
- Checked HDFS health; no corrupt or missing blocks were reported.
- Removed old experimental staging paths and created a fresh learning directory.

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

## Week 9 — 11–17 September 2026

**Status:** Planned

- [ ] Confirm the exact project title and approved problem statement.
- [ ] Confirm evaluation dates and assessment requirements.
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

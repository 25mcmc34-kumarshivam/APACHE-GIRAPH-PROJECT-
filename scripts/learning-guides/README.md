# Beginner-friendly script copies

This folder contains teaching copies of every executable script in `scripts/`.
The files outside this folder are the operational versions used in the lab.
These copies add English and Hinglish comments but keep the same logic, so a
student can read them without changing the tested commands.

## Recommended reading order

1. `check_environment_explained.sh` — variables, functions, loops, exit codes.
2. `run_pagerank_explained.sh` — one fixed Giraph job using JSON input.
3. `run_shortest_path_explained.sh` — positional arguments and source vertex.
4. `run_text_graph_algorithm_explained.sh` — reusable selection with `case`.
5. `generate_graphviz_from_text_explained.py` — validation, BFS and DOT output.

## Symbols used in the shell scripts

| Syntax | English meaning | Hinglish explanation |
|---|---|---|
| `#!/usr/bin/env bash` | Run with Bash found in `PATH`. | System ko batata hai ki file Bash se chalani hai. |
| `$HOME` | Current user's home directory. | Login user ka personal folder. |
| `$1`, `$2`, `$3` | First, second and third command-line arguments. | Command ke baad diye gaye values. |
| `"$VALUE"` | Use a variable without unsafe word splitting. | Space ho tab bhi value ek hi argument rahegi. |
| `$(command)` | Capture command output. | Command ka result variable me rakhta hai. |
| `$?` | Exit status of the previous command. | `0` success; non-zero error/difference. |
| `>/dev/null 2>&1` | Hide normal output and error output. | Check karna hai, screen par output nahi dikhana. |
| `||` | Run the right side if the left side fails. | Pehla command fail ho to recovery/error command chalega. |
| `&&` | Run the right side only after success. | Pehla command successful ho tab agla chalega. |
| `! command` | Reverse success/failure for a condition. | Result ko ulta karta hai. |
| `\` at line end | Continue one command on the next line. | Long command ko readable lines me likhne ka tarika. |

## Important Giraph options

| Option | Purpose |
|---|---|
| `-vif` | Vertex input-format class: how each input record is parsed. |
| `-vip` | HDFS vertex input path; a directory may contain multiple part files. |
| `-vof` | Vertex output-format class. |
| `-op` | New HDFS output directory. It must not already exist. |
| `-w 1` | Use one Giraph worker on this single-node learning cluster. |
| `-ca key=value` | Add a custom Giraph/Hadoop configuration value. |
| `-mc` | PageRank master-compute class. |
| `-wc` | PageRank worker-context class. |

Do not edit these teaching copies and assume the server automatically uses
them. Run the tested files one directory above unless an experiment explicitly
asks for an explained copy.

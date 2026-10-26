# Week 15 learning hub — read separately from the work record

The [weekly work report](../../weekly-reports/2026-10-29-week-15.md) records **what we did**, the commands, file transfers, evidence and result. This folder is **for understanding and presenting** the work. Nothing here is executed by Giraph.

| If you need... | Read |
|---|---|
| The experiment from zero, in easy Hinglish | [BABY-LEVEL-HINGLISH.md](BABY-LEVEL-HINGLISH.md) |
| Code expressions with many explanatory comments | [CODE-WITH-COMMENTS.md](CODE-WITH-COMMENTS.md) |
| A compact explanation for Sir, with honest limitations | [FACULTY-BRIEF.md](FACULTY-BRIEF.md) |
| Exact commands and which account runs each | [Week 15 work report — reproduce section](../../weekly-reports/2026-10-29-week-15.md#repeat-the-120-node-practical-yourself) |

Read in this order: baby-level concept → commented code → reproduce the commands → faculty brief. Do not confuse this week's **standard Graph Burning** with the separate Week 14 **limited-neighbour** Python teaching model.

## Which files are operational?

- [Grid generator](../../scripts/generate_grid_graph.py) creates the unscheduled graph.
- [Random schedule preparer](../../scripts/prepare_random_burning_input.py) adds source-round markers; it is **not** an optimizer.
- [Input validator](../../scripts/validate_burning_schedule.py) checks the graph and schedule.
- [Round preview](../../scripts/show_burning_rounds.py) independently predicts the result and draws pictures.
- [Giraph runner](../../scripts/run_graph_burning_from_input.sh) submits the actual distributed job; [input reader](../../src/BurningScheduleTextInputFormat.java) and [computation](../../src/LearningGraphBurningFromInputComputation.java) are its Java classes.
- [Formatter](../../scripts/format_burning_output.py) converts Giraph's numeric state to `B`/`NB -1`.

Use the files above when running. The explanations in this folder do not replace them. For older work, use the [full study-material index](../README.md) or [weekly-report index](../../weekly-reports/README.md).

# Gamy AI v0.7 — Self-improvement and tool use

## Design goal

Gamy should improve through an evidence loop, not by changing itself blindly:

**Observe → Validate → Diagnose → Propose one experiment → Human approval → Train candidate → Evaluate on fixed seeds → Test on holdout seeds → Promote or rollback.**

The current implementation provides the report-validation, diagnosis, plan-generation, and comparison steps. It does not silently edit policy source code, execute shell commands, or auto-promote a model.

## Skills

- **Report validation:** detect missing or invalid metrics; missing data is never silently converted to zero.
- **Metric interpretation:** read survival, reward, zone-loss, and loot measurements.
- **Failure triage:** rank likely issues using transparent thresholds and show the evidence.
- **Experiment design:** propose a one-variable-at-a-time experiment, metrics, acceptance criteria, and rollback rule.
- **Evaluation discipline:** require fixed-seed comparison and a separate holdout set before making generalization claims.
- **Promotion gate:** reject a candidate if safety/navigation metrics regress, average survival falls more than 5%, or average reward worsens.

## Allow-listed tools

ResearchToolbox exposes only four structured-data tools:

1. validate_report(report=...)
2. diagnose_report(report=...)
3. make_experiment_plan(diagnosis=...)
4. compare_reports(baseline=..., candidate=...)

No arbitrary code execution, shell, network access, file traversal, or game input tool is registered. Unknown tool names fail closed.

## Current simulator diagnosis

For the observed v0.6 report (20 fixed-seed trials): average survival 16.1 steps, average reward approximately -0.976, outside-zone steps 8.85/trial, safe-zone HP loss 8.85/trial, loot 0.15/trial, and 0 wins. The first experiment should investigate safe-zone navigation and early episode termination, not merely increase the episode count.

## Candidate acceptance

A candidate can pass the software comparison gate only if:
- safe-zone HP loss does not increase;
- outside-zone steps do not increase;
- average survival remains at least 95% of baseline;
- average reward does not worsen;
- both reports confirm evaluation did not mutate the Q-table.

Passing this gate is a proposal, not an automatic production promotion. Re-run on a separately recorded holdout seed suite and review per-trial results.

## Important limitations

The diagnosis is a transparent heuristic, not an LLM, not general intelligence, and not proof of root cause. The browser simulator does not call an external AI model or access the internet. The tool registry is a local Python foundation for future controlled orchestration. All outcomes describe this toy simulator only.

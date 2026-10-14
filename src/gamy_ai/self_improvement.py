"""Evidence-driven self-improvement loop with explicit promotion gates.

This module proposes experiments; it never edits policy code, executes arbitrary
commands, or promotes a candidate without an explicit caller decision.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any


@dataclass(frozen=True)
class ExperimentPlan:
    title: str
    diagnosis: str
    hypothesis: str
    proposed_change: str
    metric_to_watch: str
    acceptance_criteria: tuple[str, ...]
    rollback_rule: str
    human_approval_required: bool = True

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["acceptance_criteria"] = list(self.acceptance_criteria)
        return result


def _number(mapping: dict[str, Any], key: str) -> float | None:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    value = float(value)
    return value if isfinite(value) else None


def validate_report(report: dict[str, Any]) -> list[str]:
    """Return report problems instead of silently treating missing data as zero."""
    problems: list[str] = []
    if report.get("schemaVersion") != 1:
        problems.append("Unsupported or missing schemaVersion (expected 1).")
    evaluation = report.get("evaluation")
    if not isinstance(evaluation, dict):
        problems.append("Missing evaluation object.")
        return problems
    trials = evaluation.get("trialCount")
    if not isinstance(trials, int) or isinstance(trials, bool) or trials < 1:
        problems.append("trialCount must be a positive integer.")
    for field in ("averageSurvivalSteps", "averageReward", "winRatePercent",
                  "outsideZoneStepsPerTrial", "safeZoneHpLossPerTrial"):
        if _number(evaluation, field) is None:
            problems.append(f"Missing or invalid numeric metric: {field}.")
    if report.get("qTableUnchanged") is not True:
        problems.append("Q-table immutability was not confirmed.")
    return problems


def diagnose_report(report: dict[str, Any]) -> dict[str, Any]:
    """Use transparent heuristics to rank the next experiment from measured data."""
    problems = validate_report(report)
    if problems:
        return {
            "status": "needs_valid_report",
            "problems": problems,
            "skills_used": ["report_validation"],
            "tool_calls": ["validate_report"],
        }

    m = report["evaluation"]
    survival = float(m["averageSurvivalSteps"])
    reward = float(m["averageReward"])
    win_rate = float(m["winRatePercent"])
    outside = float(m["outsideZoneStepsPerTrial"])
    zone_loss = float(m["safeZoneHpLossPerTrial"])
    loot = _number(m, "lootPerTrial")
    issues: list[dict[str, str]] = []

    if outside > 0 or zone_loss > 0:
        issues.append({
            "priority": "P0",
            "name": "safe_zone_navigation",
            "evidence": f"Outside-zone steps/trial={outside:.2f}; safe-zone HP loss/trial={zone_loss:.2f}.",
            "next_step": "Inspect zone-distance state bins and movement reward; run one-variable-at-a-time ablation.",
        })
    if survival < 30:
        issues.append({
            "priority": "P0",
            "name": "short_survival",
            "evidence": f"Average survival is only {survival:.2f} steps.",
            "next_step": "Plot survival by seed and inspect terminal conditions before increasing training volume.",
        })
    if loot is not None and loot < 0.5:
        issues.append({
            "priority": "P1",
            "name": "low_loot_collection",
            "evidence": f"Loot collected/trial={loot:.2f}.",
            "next_step": "Only after safe-zone behaviour improves, test whether loot-nearby state features are informative.",
        })
    if win_rate == 0:
        issues.append({
            "priority": "P2",
            "name": "no_wins_yet",
            "evidence": "No wins were recorded in this fixed-seed suite.",
            "next_step": "Treat wins as a later outcome; first improve survival and zone-loss metrics.",
        })
    if not issues:
        issues.append({
            "priority": "P2",
            "name": "generalization_check",
            "evidence": "No critical threshold triggered by the current heuristic rules.",
            "next_step": "Evaluate on a separate holdout seed suite before claiming improvement.",
        })

    top = issues[0]
    return {
        "status": "diagnosed",
        "summary": f"Highest-priority issue: {top['name']}.",
        "metrics": {
            "averageSurvivalSteps": survival,
            "averageReward": reward,
            "winRatePercent": win_rate,
            "outsideZoneStepsPerTrial": outside,
            "safeZoneHpLossPerTrial": zone_loss,
            "lootPerTrial": loot,
        },
        "issues": issues,
        "skills_used": ["report_validation", "metric_interpretation", "failure_triage"],
        "tool_calls": ["validate_report", "summarize_metrics", "rank_failure_modes"],
        "safety_note": "This is a heuristic diagnosis of the toy simulator, not proof of root cause.",
    }


def make_experiment_plan(diagnosis: dict[str, Any]) -> dict[str, Any]:
    """Turn a diagnosis into a reversible, human-approved experiment proposal."""
    if diagnosis.get("status") != "diagnosed" or not diagnosis.get("issues"):
        return {
            "status": "blocked",
            "reason": "A valid diagnosed report is required before proposing an experiment.",
            "human_approval_required": True,
        }
    top = diagnosis["issues"][0]
    if top["name"] == "safe_zone_navigation":
        plan = ExperimentPlan(
            title="Zone-navigation reward ablation",
            diagnosis=top["evidence"],
            hypothesis="A clearer zone-distance signal will reduce outside-zone steps without sacrificing survival.",
            proposed_change="In a separate candidate copy, change only the zone-progress reward coefficient; keep seeds, starting conditions, and all other parameters fixed.",
            metric_to_watch="outsideZoneStepsPerTrial and safeZoneHpLossPerTrial; secondary metrics are survival and averageReward.",
            acceptance_criteria=(
                "Use the same fixed validation seed suite for baseline and candidate.",
                "Reduce outside-zone steps and safe-zone HP loss by at least 20%.",
                "Average survival must not decrease by more than 5%.",
                "Q-table immutability must pass during evaluation.",
                "Confirm the improvement on a separate holdout seed suite before promotion.",
            ),
            rollback_rule="Keep the previous checkpoint if any acceptance criterion fails; never overwrite the best checkpoint during experimentation.",
        )
    elif top["name"] == "short_survival":
        plan = ExperimentPlan(
            title="Terminal-condition and survival audit",
            diagnosis=top["evidence"],
            hypothesis="A small number of early terminal conditions or poorly represented states may dominate the low survival score.",
            proposed_change="Inspect episode-end reasons by seed and add a terminal-reason histogram before changing rewards or training volume.",
            metric_to_watch="survival steps, terminal reason counts, safe-zone HP loss, and average reward.",
            acceptance_criteria=(
                "Every terminated episode has exactly one recorded terminal reason.",
                "Run baseline and candidate on identical validation seeds.",
                "Do not accept a reward increase if survival or zone safety regresses.",
            ),
            rollback_rule="Revert instrumentation or candidate changes if trial counts, seeds, or terminal accounting become inconsistent.",
        )
    elif top["name"] == "low_loot_collection":
        plan = ExperimentPlan(
            title="Loot-state observability experiment",
            diagnosis=top["evidence"],
            hypothesis="The current coarse loot-nearby flag may not provide enough information for useful navigation.",
            proposed_change="Test one additional non-combat feature in a separate candidate, then compare on fixed validation and holdout seeds.",
            metric_to_watch="lootPerTrial, survival, outsideZoneStepsPerTrial, and averageReward.",
            acceptance_criteria=(
                "Change only one feature at a time.",
                "Loot collection should improve without increasing zone-loss or reducing survival.",
                "Report all seeds and both validation and holdout results.",
            ),
            rollback_rule="Reject the candidate if safety/navigation metrics regress or the gain disappears on holdout seeds.",
        )
    else:
        plan = ExperimentPlan(
            title="Holdout generalization check",
            diagnosis=top["evidence"],
            hypothesis="A separate seed suite will reveal whether gains generalize beyond the tuning scenarios.",
            proposed_change="Run a never-used holdout seed suite without updating the policy or Q-table.",
            metric_to_watch="survival, average reward, win rate, and zone-loss metrics.",
            acceptance_criteria=(
                "Record holdout seed list before the run.",
                "Q-table must remain unchanged.",
                "Report uncertainty and per-trial results, not only the mean.",
            ),
            rollback_rule="Do not promote based only on training or validation results.",
        )
    return {"status": "proposal", "plan": plan.to_dict(), "human_approval_required": True}


def compare_reports(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    """Conservative promotion gate. Lower zone loss and higher survival are better."""
    bp, cp = validate_report(baseline), validate_report(candidate)
    if bp or cp:
        return {"status": "blocked", "baseline_problems": bp, "candidate_problems": cp,
                "promote": False, "reason": "Both reports must be valid and confirm Q-table immutability."}
    b, c = baseline["evaluation"], candidate["evaluation"]
    checks = {
        "zone_loss_not_worse": c["safeZoneHpLossPerTrial"] <= b["safeZoneHpLossPerTrial"],
        "outside_zone_not_worse": c["outsideZoneStepsPerTrial"] <= b["outsideZoneStepsPerTrial"],
        "survival_within_5_percent": c["averageSurvivalSteps"] >= b["averageSurvivalSteps"] * 0.95,
        "reward_not_worse": c["averageReward"] >= b["averageReward"],
    }
    return {
        "status": "compared",
        "promote": all(checks.values()),
        "checks": checks,
        "baseline": {k: b[k] for k in ("averageSurvivalSteps", "averageReward", "outsideZoneStepsPerTrial", "safeZoneHpLossPerTrial")},
        "candidate": {k: c[k] for k in ("averageSurvivalSteps", "averageReward", "outsideZoneStepsPerTrial", "safeZoneHpLossPerTrial")},
        "reason": "Candidate passes all conservative checks." if all(checks.values()) else "Keep baseline: one or more checks failed.",
        "human_approval_required": True,
    }

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gamy_ai.self_improvement import compare_reports, diagnose_report, make_experiment_plan
from gamy_ai.tools import ResearchToolbox, ToolError


def report(*, survival=16.1, reward=-0.976, outside=8.85, zone_loss=8.85, loot=0.15, win=0):
    return {
        "schemaVersion": 1, "qTableUnchanged": True, "qStatesBefore": 603, "qStatesAfter": 603,
        "evaluation": {
            "trialCount": 20, "averageSurvivalSteps": survival, "averageReward": reward,
            "winRatePercent": win, "outsideZoneStepsPerTrial": outside,
            "safeZoneHpLossPerTrial": zone_loss, "lootPerTrial": loot,
        },
    }


class SelfImprovementTests(unittest.TestCase):
    def test_diagnosis_prioritizes_zone_problem(self):
        result = diagnose_report(report())
        self.assertEqual(result["status"], "diagnosed")
        self.assertEqual(result["issues"][0]["name"], "safe_zone_navigation")

    def test_invalid_report_is_not_treated_as_zeroes(self):
        result = diagnose_report({"schemaVersion": 1, "evaluation": {}})
        self.assertEqual(result["status"], "needs_valid_report")
        self.assertTrue(result["problems"])

    def test_plan_requires_human_approval_and_rollback(self):
        diagnosis = diagnose_report(report())
        proposal = make_experiment_plan(diagnosis)
        self.assertTrue(proposal["human_approval_required"])
        self.assertIn("rollback_rule", proposal["plan"])
        self.assertTrue(proposal["plan"]["acceptance_criteria"])

    def test_promotion_gate_rejects_regression(self):
        result = compare_reports(report(), report(survival=10, reward=-2, outside=10, zone_loss=10))
        self.assertFalse(result["promote"])

    def test_promotion_gate_accepts_candidate_that_passes_all_checks(self):
        result = compare_reports(report(), report(survival=18, reward=0.1, outside=5, zone_loss=5))
        self.assertTrue(result["promote"])

    def test_toolbox_is_allow_list_only(self):
        tools = ResearchToolbox()
        self.assertIn("diagnose_report", tools.available_tools)
        with self.assertRaises(ToolError):
            tools.call("run_shell", command="echo unsafe")

    def test_toolbox_call_returns_structured_diagnosis(self):
        result = ResearchToolbox().call("diagnose_report", report=report())
        self.assertEqual(result["status"], "diagnosed")
        self.assertIn("metric_interpretation", result["skills_used"])


if __name__ == "__main__":
    unittest.main()

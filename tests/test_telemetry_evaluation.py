import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gamy_ai.evaluation import summarize_matches
from gamy_ai.telemetry import append_jsonl, read_jsonl


class TelemetryTests(unittest.TestCase):
    def test_jsonl_roundtrip(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "events.jsonl"
            rows = [{"record_type": "match_result", "match_id": "m1", "win": True}]
            self.assertEqual(append_jsonl(path, rows), 1)
            self.assertEqual(read_jsonl(path), rows)

    def test_evaluation_reports_missing_metrics_as_none(self):
        result = summarize_matches([
            {"record_type": "match_result", "match_id": "m1", "win": True, "survival_seconds": 120, "placement": 1},
            {"record_type": "recommendation_feedback", "accepted": True},
            {"record_type": "recommendation_feedback", "accepted": False},
        ])
        self.assertEqual(result["match_count"], 1)
        self.assertEqual(result["mean_survival_seconds"], 120.0)
        self.assertEqual(result["win_rate"], 1.0)
        self.assertEqual(result["recommendation_acceptance_rate"], 0.5)
        self.assertIsNone(result["mean_damage_dealt"])


if __name__ == "__main__":
    unittest.main()

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gamy_ai.models import Action, Observation
from gamy_ai.policy import RulePolicy


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = RulePolicy()

    def test_critical_zone_pressure_has_priority(self):
        obs = Observation(match_id="m1", health_ratio=0.1, healing_available=True,
                          safe_zone_pressure=0.9)
        self.assertEqual(self.policy.recommend(obs).action, Action.MOVE_TO_SAFE_ZONE)

    def test_critical_health_prefers_heal_if_available(self):
        obs = Observation(match_id="m2", health_ratio=0.1, healing_available=True)
        self.assertEqual(self.policy.recommend(obs).action, Action.HEAL)

    def test_low_health_without_cover_recommends_safer_position(self):
        obs = Observation(match_id="m3", health_ratio=0.2, has_cover=False)
        self.assertEqual(self.policy.recommend(obs).action, Action.SEEK_COVER)

    def test_recommendations_always_require_human_confirmation(self):
        rec = self.policy.recommend(Observation(match_id="m4"))
        self.assertTrue(rec.requires_human_confirmation)

    def test_observation_rejects_out_of_range_features(self):
        with self.assertRaises(ValueError):
            Observation(match_id="m5", health_ratio=1.5)


if __name__ == "__main__":
    unittest.main()

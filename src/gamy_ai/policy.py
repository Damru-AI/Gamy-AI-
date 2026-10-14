"""Non-combat baseline for safe-zone navigation and human-reviewed suggestions."""
from __future__ import annotations

from .models import Action, Observation, Recommendation


class RulePolicy:
    """Recommend a non-combat next step; never executes it."""

    version = "navigation-baseline-0.2"

    def recommend(self, obs: Observation) -> Recommendation:
        if obs.safe_zone_pressure >= 0.80:
            action, confidence = Action.MOVE_TO_SAFE_ZONE, 0.90
            rationale = ("Zone pressure is high; prioritize safe navigation.",)
        elif obs.health_ratio <= 0.25 and obs.healing_available:
            action, confidence = Action.HEAL, 0.86
            rationale = ("Health is low and a healing option is reported available.",)
        elif obs.health_ratio <= 0.25 and not obs.has_cover:
            action, confidence = Action.SEEK_COVER, 0.80
            rationale = ("Health is low; consider moving to a safer covered position.",)
        elif obs.safe_zone_pressure >= 0.55:
            action, confidence = Action.MOVE_TO_SAFE_ZONE, 0.76
            rationale = ("Zone pressure is rising; plan a safe route.",)
        elif obs.health_ratio <= 0.50 and obs.healing_available:
            action, confidence = Action.HEAL, 0.72
            rationale = ("Health is reduced and a healing option is reported available.",)
        elif not obs.has_cover:
            action, confidence = Action.SEEK_COVER, 0.58
            rationale = ("Consider a safer position; confirm the scene manually.",)
        else:
            action, confidence = Action.OBSERVE, 0.55
            rationale = ("Evidence is limited; continue observing and confirm manually.",)

        return Recommendation(
            match_id=obs.match_id,
            timestamp=obs.timestamp,
            action=action,
            confidence=confidence,
            rationale=rationale,
            policy_version=self.version,
            requires_human_confirmation=True,
        )
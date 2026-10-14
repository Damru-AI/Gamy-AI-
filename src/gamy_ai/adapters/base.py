"""Adapter boundaries: source observations in; human-reviewed suggestions out."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from gamy_ai.models import Observation, Recommendation


class ObservationSource(Protocol):
    def next_observation(self) -> Observation | None:
        """Return the next observation or None at end of replay."""
        ...


class RecommendationSink(Protocol):
    def publish(self, recommendation: Recommendation) -> None:
        """Publish a suggestion without issuing game controls."""
        ...


@dataclass
class HumanReviewSink:
    """Minimal sink used by CLI runs; it only prints a suggestion."""

    def publish(self, recommendation: Recommendation) -> None:
        print(
            f"[{recommendation.match_id}] {recommendation.action.value} "
            f"(confidence={recommendation.confidence:.2f}; human confirmation required)"
        )
        for reason in recommendation.rationale:
            print(f"  - {reason}")

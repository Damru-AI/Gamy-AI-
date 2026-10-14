"""Stable, game-agnostic contracts used between Gamy components."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class Action(str, Enum):
    HEAL = "heal"
    SEEK_COVER = "seek_cover"
    MOVE_TO_SAFE_ZONE = "move_to_safe_zone"
    OBSERVE = "observe"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class Observation:
    """A compact state estimate. Ratios/pressure are normalized to [0, 1].

    Observations can come from manual annotation, a video model, or an approved
    data feed; this object deliberately knows nothing about a game client.
    """

    match_id: str
    timestamp: str = field(default_factory=utc_now_iso)
    health_ratio: float = 1.0
    safe_zone_pressure: float = 0.0
    has_cover: bool = False
    healing_available: bool = False
    source_kind: str = "manual_annotation"
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.match_id.strip():
            raise ValueError("match_id must be non-empty")
        for name in ("health_ratio", "safe_zone_pressure"):
            value = getattr(self, name)
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {value}")

    @classmethod
    def from_dict(cls, obj: dict[str, Any]) -> "Observation":
        allowed = {
            "match_id", "timestamp", "health_ratio", "safe_zone_pressure", "has_cover",
            "healing_available", "source_kind", "extra",
        }
        values = {k: v for k, v in obj.items() if k in allowed}
        if "match_id" not in values:
            values["match_id"] = "unassigned"
        return cls(**values)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Recommendation:
    match_id: str
    timestamp: str
    action: Action
    confidence: float
    rationale: tuple[str, ...]
    policy_version: str = "rule-baseline-0.1"
    requires_human_confirmation: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be in [0, 1]")

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["action"] = self.action.value
        result["rationale"] = list(self.rationale)
        return result
"""Simple outcome metrics for permitted test sessions and offline evaluation."""
from __future__ import annotations

from statistics import mean
from typing import Any, Iterable


def summarize_matches(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize rows such as {match_id, placement, survival_seconds, win, kills}.

    The function ignores rows without `record_type='match_result'` when that key
    exists. Missing metrics remain null rather than silently being treated as 0.
    """
    all_rows = list(rows)
    matches = [r for r in all_rows if r.get("record_type", "match_result") == "match_result"]
    def numeric_values(key: str) -> list[float]:
        vals: list[float] = []
        for row in matches:
            value = row.get(key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                vals.append(float(value))
        return vals
    def avg(key: str) -> float | None:
        vals = numeric_values(key)
        return round(mean(vals), 3) if vals else None

    recs = [r for r in all_rows if r.get("record_type") == "recommendation_feedback"]
    feedback = [r for r in recs if isinstance(r.get("accepted"), bool)]
    accepted = sum(1 for r in feedback if r["accepted"])
    wins = [r for r in matches if isinstance(r.get("win"), bool)]
    return {
        "match_count": len(matches),
        "mean_survival_seconds": avg("survival_seconds"),
        "mean_placement": avg("placement"),
        "mean_kills": avg("kills"),
        "mean_damage_dealt": avg("damage_dealt"),
        "win_rate": round(sum(1 for r in wins if r["win"]) / len(wins), 4) if wins else None,
        "recommendation_feedback_count": len(feedback),
        "recommendation_acceptance_rate": round(accepted / len(feedback), 4) if feedback else None,
        "caveat": "Metrics are only as reliable as the source annotations; compare policies on the same held-out scenarios.",
    }

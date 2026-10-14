# Labelled training dataset schema

Use one JSON object per line (JSONL). Each row represents one observed decision point. This starter is intentionally limited to non-combat navigation, basic survival status, and human review.

```json
{
  "match_id": "match-001",
  "session_group": "recording-session-a",
  "state": {
    "health_ratio": 0.62,
    "safe_zone_pressure": 0.14,
    "has_cover": true,
    "healing_available": true
  },
  "action_label": "observe"
}
```

Allowed labels: `heal`, `seek_cover`, `move_to_safe_zone`, `observe`. Labels should reflect a documented rule or reviewed human judgement, not be inferred from noisy outcomes alone. Split train/validation data by `session_group` or match, not by random frame, so near-identical frames do not leak across splits. Remove player identifiers and private chat/voice unless there is a clear need and lawful permission to retain them.

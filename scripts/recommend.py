#!/usr/bin/env python3
"""Generate offline action recommendations from annotated observation JSONL."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gamy_ai.models import Observation  # noqa: E402
from gamy_ai.policy import RulePolicy  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="JSONL input with one observation per line")
    parser.add_argument("output", help="JSONL path to write recommendations")
    args = parser.parse_args()
    policy = RulePolicy()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with Path(args.input).open(encoding="utf-8") as source, out.open("w", encoding="utf-8") as target:
        for line_no, line in enumerate(source, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
                obs = Observation.from_dict(obj)
                rec = policy.recommend(obs)
            except (json.JSONDecodeError, TypeError, ValueError) as exc:
                parser.error(f"input line {line_no}: {exc}")
            target.write(json.dumps(rec.to_dict(), ensure_ascii=False) + "\n")
            total += 1
    print(f"Wrote {total} recommendations to {out}. No game inputs were issued.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

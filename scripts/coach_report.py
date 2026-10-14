#!/usr/bin/env python3
"""Diagnose an exported DropZone Lab v0.6+ evaluation JSON report."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gamy_ai.tools import ResearchToolbox


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path, help="Evaluation JSON downloaded from DropZone Lab")
    parser.add_argument("--out", type=Path, default=Path("gamy-improvement-plan.json"))
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        parser.error(f"Cannot read report JSON: {exc}")
    if not isinstance(report, dict):
        parser.error("Report root must be a JSON object.")
    tools = ResearchToolbox()
    diagnosis = tools.call("diagnose_report", report=report)
    plan = tools.call("make_experiment_plan", diagnosis=diagnosis)
    result = {"diagnosis": diagnosis, "experiment": plan}
    args.out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\nSaved plan to: {args.out}")
    return 0 if diagnosis.get("status") == "diagnosed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

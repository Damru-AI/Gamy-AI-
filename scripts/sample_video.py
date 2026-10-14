#!/usr/bin/env python3
"""Sample stills from a local gameplay recording for later human annotation."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gamy_ai.video import sample_video  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video")
    parser.add_argument("--out", default="frames")
    parser.add_argument("--every-seconds", type=float, default=2.0)
    args = parser.parse_args()
    try:
        result = sample_video(args.video, args.out, args.every_seconds)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Offline frame sampling from an existing video file; does not capture live screens."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def sample_video(video_path: str | Path, out_dir: str | Path, every_seconds: float = 2.0) -> dict[str, Any]:
    if every_seconds <= 0:
        raise ValueError("every_seconds must be positive")
    try:
        import cv2  # type: ignore
    except ImportError as exc:
        raise RuntimeError("Install the optional video extra: pip install -e '.[video]'") from exc

    source = Path(video_path)
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {source}")
    fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
    if fps <= 0:
        cap.release()
        raise ValueError("Video FPS metadata is missing or invalid")
    stride = max(1, int(round(fps * every_seconds)))
    frame_index = 0
    saved = 0
    index_path = output / "frames.jsonl"
    try:
        with index_path.open("w", encoding="utf-8") as index_file:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                if frame_index % stride == 0:
                    name = f"frame_{frame_index:09d}.jpg"
                    target = output / name
                    if not cv2.imwrite(str(target), frame):
                        raise OSError(f"Failed to write frame: {target}")
                    row = {"source_video": source.name, "frame_index": frame_index,
                           "time_seconds": round(frame_index / fps, 3), "frame_path": name}
                    index_file.write(json.dumps(row, ensure_ascii=False) + "\n")
                    saved += 1
                frame_index += 1
    finally:
        cap.release()
    return {"video": str(source), "frames_read": frame_index, "frames_saved": saved,
            "fps": round(fps, 3), "sample_every_seconds": every_seconds,
            "index_path": str(index_path)}

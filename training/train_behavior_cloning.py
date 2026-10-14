#!/usr/bin/env python3
"""Train a small behaviour-cloning baseline from human-labelled JSONL.

Example: python training/train_behavior_cloning.py --data labels.jsonl --out checkpoints/bc-v0
Requires optional dependencies: pip install numpy torch
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

FEATURES = ["health_ratio", "safe_zone_pressure", "has_cover", "healing_available"]
LABELS = ["heal", "seek_cover", "move_to_safe_zone", "observe"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--validation-fraction", type=float, default=0.2)
    args = parser.parse_args()
    if args.epochs < 1 or not 0.05 <= args.validation_fraction < 0.5:
        parser.error("epochs must be >= 1 and validation-fraction must be in [0.05, 0.5)")
    try:
        import numpy as np
        import torch
        from torch import nn
    except ImportError as exc:
        parser.error(f"Training dependencies missing: {exc}; run pip install numpy torch")

    rows = []
    with Path(args.data).open(encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
                state, label = row["state"], row["action_label"]
                if label not in LABELS:
                    raise ValueError(f"unknown label: {label}")
                vals = []
                for key in FEATURES:
                    val = state[key]
                    if key in ("has_cover", "healing_available"):
                        val = float(bool(val))
                    val = float(val)
                    if not 0.0 <= val <= 1.0:
                        raise ValueError(f"feature {key} must be in [0,1]")
                    vals.append(val)
                rows.append((row.get("session_group", row.get("match_id", f"line-{i}")), vals, LABELS.index(label)))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                parser.error(f"dataset line {i}: {exc}")
    if len(rows) < 20:
        parser.error(f"Need at least 20 labelled rows for a meaningful first experiment; found {len(rows)}")

    grouped: dict[str, list[tuple[str, list[float], int]]] = {}
    for row in rows:
        grouped.setdefault(row[0], []).append(row)
    groups = list(grouped)
    random.Random(args.seed).shuffle(groups)
    n_val = max(1, int(round(len(groups) * args.validation_fraction)))
    val_groups = set(groups[:n_val]) if len(groups) > 1 else set()
    train_rows = [r for r in rows if r[0] not in val_groups]
    val_rows = [r for r in rows if r[0] in val_groups]
    if not train_rows:
        parser.error("No training rows after split; add more recording groups")

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    class Net(nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = nn.Sequential(nn.Linear(len(FEATURES), 64), nn.ReLU(),
                                        nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, len(LABELS)))
        def forward(self, x):
            return self.layers(x)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = Net().to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    loss_fn = nn.CrossEntropyLoss()

    def tensors(part):
        x = torch.tensor(np.asarray([r[1] for r in part], dtype=np.float32), device=device)
        y = torch.tensor(np.asarray([r[2] for r in part], dtype=np.int64), device=device)
        return x, y
    x_train, y_train = tensors(train_rows)
    x_val, y_val = tensors(val_rows) if val_rows else (None, None)
    best_val = float("inf")
    best_state = None
    for epoch in range(1, args.epochs + 1):
        model.train()
        permutation = torch.randperm(len(x_train), device=device)
        for idx in permutation.split(64):
            optimizer.zero_grad(set_to_none=True)
            loss = loss_fn(model(x_train[idx]), y_train[idx])
            loss.backward()
            optimizer.step()
        model.eval()
        with torch.no_grad():
            train_acc = (model(x_train).argmax(1) == y_train).float().mean().item()
            val_loss, val_acc = None, None
            if x_val is not None:
                val_logits = model(x_val)
                val_loss = loss_fn(val_logits, y_val).item()
                val_acc = (val_logits.argmax(1) == y_val).float().mean().item()
                if val_loss < best_val:
                    best_val, best_state = val_loss, {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
        print(f"epoch={epoch:03d} train_acc={train_acc:.4f} val_loss={val_loss if val_loss is not None else 'NA'} val_acc={val_acc if val_acc is not None else 'NA'}")
    if best_state is not None:
        model.load_state_dict(best_state)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    torch.save(model.cpu().state_dict(), out / "model_state.pt")
    metadata = {"model": "GamyBCNet", "feature_order": FEATURES, "label_order": LABELS,
                "train_rows": len(train_rows), "validation_rows": len(val_rows),
                "validation_group_split": bool(val_rows), "best_validation_loss": best_val if val_rows else None,
                "seed": args.seed, "epochs": args.epochs, "trained_at_utc": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}
    (out / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model and metadata to {out}; evaluate on a separate held-out match set before promotion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

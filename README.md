# Gamy AI — Research Starter

Gamy is a **separate project** from Damru AI. This starter establishes a modular baseline for studying battle-royale decision-making from recorded gameplay, testing policies in a controlled simulator, learning from human-labelled examples, and evaluating match outcomes.

## What is included

- A typed observation/recommendation schema and a transparent, non-combat navigation baseline policy.
- Replay-first video frame sampling (optional OpenCV; reads files only).
- JSONL logging and evaluation metrics for recommendations and match outcomes.
- A human-review action sink. Recommendations are suggestions; this starter does not send game inputs.
- A Kaggle-friendly supervised behavior-cloning script for labelled observation/action data (optional PyTorch).
- The existing DropZone Lab HTML prototype under `simulator/` for local controlled experiments.
- A permission gate and adapter interfaces so a future **company-authorized** integration can be added at the boundary, not wired into the core.

## Important scope

This starter does not modify Free Fire, inject inputs, automate game controls, bypass anti-cheat, or claim to have permission to connect to a live game. Before any live control integration, obtain written authorization and implement the official/supported interface specified by the rights holder. Until then, use recorded footage, the simulator, and human-confirmed recommendations.

## Quick start (Python 3.10+)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m pytest -q
```

## Try the baseline policy

Create `observations.jsonl` with one JSON object per line; example:

```json
{"match_id":"demo-001","timestamp":"2026-10-14T08:00:00Z","health_ratio":0.22,"safe_zone_pressure":0.2,"has_cover":false,"healing_available":true,"source_kind":"manual_annotation"}
```

Then run:

```bash
python scripts/recommend.py observations.jsonl recommendations.jsonl
```

The output includes a non-combat navigation suggestion, confidence, and rationale. It does **not** perform the action.

## Training on Kaggle

1. Export or annotate a dataset as JSONL with `state` features and an `action_label` (see `training/DATASET_SCHEMA.md`).
2. Upload the dataset and this project to a Kaggle notebook.
3. Install `pip install torch numpy` if needed.
4. Run `python training/train_behavior_cloning.py --data /kaggle/input/YOUR_DATASET/labels.jsonl --out /kaggle/working/gamy_model`.
5. Keep train/validation splits grouped by match/session to reduce leakage. Compare against the baseline before promoting any checkpoint.

The current DropZone Lab is a compact browser Q-learning prototype; it is not a faithful Free Fire environment. This starter intentionally excludes combat tactics and live-game control automation.

## Project map

- `src/gamy_ai/models.py` — observation and recommendation contracts.
- `src/gamy_ai/policy.py` — interpretable fallback policy.
- `src/gamy_ai/adapters/` — replay and human-review interfaces.
- `src/gamy_ai/telemetry.py` — append-only JSONL records.
- `src/gamy_ai/evaluation.py` — held-out match metrics.
- `src/gamy_ai/video.py` — optional offline video sampling.
- `training/` — labelled dataset schema and behavior-cloning trainer.
- `docs/ARCHITECTURE.md` — module boundaries and permission-ready design.
- `docs/PERMISSION_GATE.md` — requirements for future authorized game integration.

## Development principle

Train in the simulator, learn from properly labelled recordings, validate on held-out matches, and keep the best known checkpoint unless a new version improves measured metrics without regressions. Do not claim real-game performance until independently measured on a permitted test setup.


## Self-improvement and tool use (v0.7)

DropZone Lab now includes a local Research Coach. After running the fixed-seed evaluation, tap **Diagnose + create experiment plan** to validate metrics, triage the highest-priority weakness, and draft a reversible experiment. The plan can be downloaded as JSON.

The Python research toolbox exposes allow-listed structured-data tools for report validation, diagnosis, experiment planning, and baseline/candidate comparison. It cannot execute arbitrary code, access a shell or network, or send game inputs.

To diagnose an exported evaluation report on a Python environment:

```bash
python scripts/coach_report.py gamy-ai-evaluation.json --out gamy-improvement-plan.json
python -m pytest -q
```

The coach uses transparent heuristics, not an external LLM. It proposes experiments but does not silently modify a policy or promote a candidate. Use the same validation seeds, a separate holdout seed suite, and rollback rules before accepting a change. See [docs/SELF_IMPROVEMENT_AND_TOOLS.md](docs/SELF_IMPROVEMENT_AND_TOOLS.md).


## v1.1 Dynamic Zone & Vision Lab (draft)

A separate experimental browser page is available at [simulator/gamy_ai_v1_1_vision_lab.html](simulator/gamy_ai_v1_1_vision_lab.html). It adds a six-phase shrinking safe zone, deterministic phase-based contact reduction, simulator-only movement and squad-support controls, local recorded-video playback, simple frame statistics, and JSON session export. See [docs/V1_1_DYNAMIC_ZONE_VISION.md](docs/V1_1_DYNAMIC_ZONE_VISION.md) for limitations and manual checks. The frame analyzer is not a trained vision model; no live-game controls are sent.


## v1.2 Autonomous Research Core (experimental)

The root-level [gamy_agent_core.py](gamy_agent_core.py) adds a PyTorch DQN policy, bounded replay memory, JSONL persistence, target-network updates, and checkpoint save/load for a controlled research simulator. See [GAMY_AI_V1_2_ARCHITECTURE.md](GAMY_AI_V1_2_ARCHITECTURE.md) for the design and Hugging Face artifact workflow.

Install the optional learning dependency with `pip install torch`. The policy is untrained until you run it against a simulator loop and evaluate it. This module has no screen capture, mobile accessibility, keyboard/mouse injection, or external-game control adapter. Its action set is limited to navigation, waiting, regrouping, and recovery in a controlled simulator.

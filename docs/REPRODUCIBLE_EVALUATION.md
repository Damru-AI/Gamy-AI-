# DropZone Lab v0.6 — Reproducible evaluation

## Purpose
Make evaluation auditable and ensure a test run does not mutate the learned Q-table.

## What changed
- Evaluation uses the fixed 20-seed suite: `7001 + i * 101`, for zero-based trial index `i=0..19`.
- Greedy evaluation reads an existing Q-table row or a temporary all-zero row for unseen states. It does not call `getQ()` during evaluation, avoiding insertion of new states.
- The report records Q-table state count before and after evaluation and includes a `qTableUnchanged` assertion.
- The simulator displays a compact first-five-trial summary and can export the full report as JSON, including per-trial seed, steps, reward, win, zone loss, obstacle hits, loot, and opponent hits.
- The page header is updated to v0.6.

## Mobile workflow
1. Open `simulator/dropzone_lab_android.html` from this branch and download the raw HTML.
2. Open it in a browser that supports local storage. Check that the expected learned Q-table is loaded.
3. Tap **Evaluate agent**. Confirm `Q-table unchanged: true` and that the before/after state counts match.
4. Tap **Download evaluation JSON** and save the report.
5. Repeat evaluation. The same trained policy and fixed seed suite should produce the same per-trial results because evaluation uses deterministic seeded worlds and greedy actions.
6. Compare JSON reports across code versions only when training episode count and policy provenance are known.

## Interpretation cautions
- Fixed-seed repeatability tests determinism, not generalization. A later benchmark should include a separate holdout seed suite.
- A Q-table may still be weak even if results are repeatable.
- This is a custom toy 2D simulator. Results do not imply performance in any commercial game.

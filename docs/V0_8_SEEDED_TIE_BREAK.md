# v0.8 seeded tie-breaking experiment

## Problem observed
The v0.6 evaluation report had 14 of 20 trials end after five steps. In the greedy evaluator, equal Q-values were resolved by choosing the first action index every time. Since North is action index 0, unseen states had a systematic North-first bias rather than a neutral greedy choice.

## Change
- Add `greedyIndex(values)`, which chooses among equal maximum Q-values using the simulator's seeded random generator.
- Use it in both training-time greedy choices and fixed-seed evaluation.
- Evaluation remains reproducible for the same seed and policy because the simulator RNG is initialized from each trial's seed.
- Evaluation still reads Q-values without creating missing entries; it must not mutate the Q-table.

## Validation plan
1. Open this candidate on mobile and run a fresh 2,000-episode training run (candidate has its own storage key, isolated from the v0.7 baseline).
2. Run fixed-seed evaluation and export JSON.
3. Repeat evaluation without training. Confirm the same seed suite produces the same report and that `qTableUnchanged` is true.
4. Compare against the v0.7 baseline on identical seeds. Check survival, reward, outside-zone steps, safe-zone HP loss, and loot; do not judge by average reward alone.
5. Keep this candidate separate unless results improve without regressions.

## Limits
This is a heuristic Q-learning simulator experiment only. It does not connect to Free Fire, send game inputs, or demonstrate real-game performance.

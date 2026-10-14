# DropZone Lab v0.2 — safe-zone experiment

## Hypothesis
The baseline Q-learning state did not expose the direction of the safe zone or nearby blocked cells. The reward only gave a strong signal when entering the safe zone, while health decreased each step outside it. This may make useful navigation difficult to learn.

## Changes in this experiment
- State features now include health, direction toward the zone, whether the agent is inside it, and blocked cells in the four cardinal directions.
- Reward shaping gives a small positive/negative signal for movement toward/away from the safe zone, reduces the per-step outside-zone penalty, and adds a modest survival bonus while inside.
- The browser storage key changes to `dropzone_lab_qlearning_v2`; this keeps the old v0.1 Q-table intact but starts a fresh table for the new state schema.

## How to evaluate on mobile
1. Open the v0.2 HTML file from this branch and run it in a browser that supports local storage.
2. Train to 1,300 episodes, then run the fixed-scenario evaluation.
3. Record survival steps, win rate, average test reward, and Q-table states.
4. Repeat at 2,000 episodes if time allows. Do not clear the old v0.1 saved data.
5. Compare results against the old baseline (20 trials, 5 average survival steps, 0% wins, -6.23 average test reward).

## Important limitations
This is a small stochastic 2D toy simulation. A 20-trial result has high variance; rerun evaluations and compare multiple fixed seeds before claiming improvement. This experiment only targets navigation/survival signals; it does not establish performance in any commercial game.

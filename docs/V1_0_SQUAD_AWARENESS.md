# Gamy AI v1.0 — Squad Awareness & Survival

## Scenario
- 54 simulated opponent/contact markers in the 2D arena (one existing primary interaction plus 53 ambient moving contacts).
- Three squadmates follow nearby as team-survival support.
- The policy prioritizes safe-zone navigation, obstacle-aware legal movement, and recovery after damage.
- Nearby squad support reduces the toy primary contact's damage probability from 0.25 to 0.12.
- A single primary-contact interaction no longer ends the episode as a victory. The scenario's win condition is surviving the full 150-step episode.

## Important limits
- The 53 ambient contacts are moving awareness markers; they do not independently attack, take damage, or receive targeting commands. This update does not implement automatic enemy elimination or live-game controls.
- Squadmates are simulator support entities, not trained independent agents with individual policies.
- This is a rule-based multi-contact simulator extension, not evidence of superintelligence or real Free Fire performance.

## Validation plan
1. Open the v1.0 candidate on mobile and train 2,000 episodes.
2. Run the fixed-seed 20-trial evaluation and download JSON.
3. Check scenario metadata (`opponentContacts: 54`, `squadmates: 3`), Q-table immutability during evaluation, survival, reward, outside-zone steps, zone damage, and obstacle hits.
4. Repeat evaluation without training; confirm the report is reproducible.
5. Compare only against a baseline with the same scenario rules. Keep v1.0 a draft until tests show no regressions.

# Gamy AI v0.9 — survival guardrails

## Evidence from v0.8
The uploaded 20-trial report recorded 16.9 outside-zone steps/trial, 16.9 zone-damage ticks/trial, average reward -9.67, and 0/20 wins. Many episodes ended after five steps. This suggests the toy simulator's one-health-point-per-outside-step penalty can eliminate a 5-HP agent before it can reach the zone.

## Changes in this candidate
- Adds a transparent safety shield to training, live simulator episodes, single-step mode, and fixed-seed evaluation.
- Outside the safe zone, the shield selects a legal move that most reduces distance to the zone.
- Inside the zone, it chooses recovery while health is below maximum (5/5 = 100%; 4/5 = 80%, above the requested 70% floor).
- It blocks a proposed move that would leave the safe zone when a legal in-zone move is available.
- Outside-zone damage now ticks once every three outside-zone steps, while outside-zone steps remain separately measured.
- The candidate uses its own storage key to keep learning data isolated from the baseline.

## Important interpretation
The safety shield is explicit rule-based logic layered over Q-learning; it is not proof of superintelligence and it does not itself demonstrate that the Q-table learned better behaviour. The existing toy simulator's opponent interaction is unchanged. This candidate does not add new offensive targeting, live-game controls, or a Free Fire connection.

## Validation
1. Run 2,000 fresh episodes on the candidate.
2. Run the fixed 20-seed evaluation and download JSON.
3. Repeat evaluation without training; check `qTableUnchanged: true` and repeatability.
4. Compare with the baseline on outside-zone steps, zone damage ticks, survival, reward, and health/recovery behaviour.
5. Do not promote unless results improve without regressions; retain the baseline otherwise.

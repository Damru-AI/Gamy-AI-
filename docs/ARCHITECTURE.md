# Gamy AI architecture and boundaries

```text
Recorded match files / DropZone simulation / future approved data feed
                              |
                              v
                  ObservationSource adapter
                              |
                              v
             Perception + normalized Observation
                              |
                              v
             Policy (rules now; model later)
                              |
                              v
                Recommendation + rationale
                      /               \
             Human review             Telemetry
                   |                     |
          human executes action      offline evaluation

Future authorized integration: implement a separate adapter behind the
interfaces above only after written permission and the approved interface exist.
It must not change the Observation/Recommendation contracts.
```

## Why this avoids a major rewrite later

1. Game I/O is kept outside policy logic. Policies consume a normalized `Observation` and return a `Recommendation`.
2. Training uses a stable feature/action schema. The simulator, labelled recordings, and a future permitted feed can map to the same schema.
3. Every recommendation includes policy version, confidence, timestamp and rationale.
4. Telemetry/evaluation is separate from the decision mechanism, so new models can be A/B tested on the same replay set.
5. Any future game-specific SDK, accessibility/test API or company-provided interface will be isolated behind an adapter. Its concrete design depends on the written authorization and the interface the rights holder permits.

## Development stages

- Stage 0: repo structure, schema, tests, telemetry, permission checklist.
- Stage 1: export stable observation/action traces from DropZone; make simulator scenarios reproducible.
- Stage 2: sample recorded footage and create reviewed labels; evaluate offline state estimation.
- Stage 3: train behaviour cloning in Kaggle and compare to the rule baseline on match-grouped holdouts.
- Stage 4: validate recommendations in shadow mode while a human retains control.
- Stage 5: if and only if written permission and an authorized control interface exist, implement and test a specific adapter behind the same boundary.

The existing DropZone HTML is an experimental tabular Q-learning toy environment (five movement/hold actions, simplified loot/enemy/zone dynamics). It should not be represented as a Free Fire physics model or proof of match performance.

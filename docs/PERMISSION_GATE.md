# Live-game permission gate

Live control is disabled in this starter. Do not enable an adapter until all items are checked with the rights holder and your project supervisor/adult contact where appropriate.

- [ ] Written authorization from the game company or designated program.
- [ ] Explicitly approved test environment and account type; a guest account by itself is not permission.
- [ ] Written scope: allowed game modes, test period, data capture/retention, account limits, distribution and reporting.
- [ ] Documented official/supported way to submit actions; no reverse engineering, client modification, input injection, or anti-cheat circumvention outside the written scope.
- [ ] Test fails closed if authorization/configuration is absent or expires.
- [ ] Rate limits, emergency stop, complete audit log, and human override are tested.
- [ ] Independent evaluation and regression suite pass before each version is proposed for the authorized environment.

Until this gate is satisfied, use simulator training, recordings, and human-confirmed recommendations only. Permission is not assumed from a test/guest account or from the fact that code can technically run.

## Scope restriction for this starter

The initial implementation only supports offline observation, non-combat navigation/survival suggestions, evaluation, and human confirmation. It does not include a live control adapter, touch injection, client modification, anti-cheat evasion, or combat automation. Any future adapter must be based on a documented, authorized interface from the game publisher and reviewed before it is enabled.

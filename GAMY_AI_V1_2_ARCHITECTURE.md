# Gamy AI v1.2 — Autonomous Research Core

## Goal
Move Gamy from a display-only demo toward a measurable learning system: observation contract, policy, persistent experience memory, training loop, checkpoint lifecycle, and evaluation gates.

## Components
1. Environment adapter for the controlled research simulator: returns a fixed-length numeric observation, applies one simulator action, and returns reward and termination.
2. Policy: gamy_agent_core.py provides a PyTorch DQN with online and target networks and a non-combat action vocabulary.
3. Episodic memory: transitions are kept in a bounded replay buffer and appended to JSONL so they survive process restarts. Each record contains state, action index, reward, next state, terminal flag, and episode ID.
4. Training: store a transition at each simulator step; once memory has enough examples, call train_step(). Sync the target network periodically.
5. Evaluation: compare a candidate and baseline on the same fixed seeds, then use separate holdout seeds. Track success rate, episode return, episode length, recovery events, and invalid actions.
6. Artifacts: save model checkpoints with action vocabulary and observation-size metadata. Store training traces as JSONL or Parquet; keep large datasets and checkpoints out of Git.

## Minimal integration example
~~~python
from gamy_agent_core import DQNAgent, EpisodicMemory, record_transition

memory = EpisodicMemory(path="data/experience.jsonl")
memory.load_recent()
agent = DQNAgent(observation_size=12, memory=memory)

# Inside a custom simulator episode:
# state = env.reset(seed=seed)
# action_index, action_name = agent.act(state)
# next_state, reward, terminated, info = env.step(action_name)
# record_transition(memory, state, action_index, reward, next_state, terminated, episode_id)
# loss = agent.train_step(batch_size=64)
# if terminated: agent.save("artifacts/gamy_candidate.pt", {"episode": episode_id})
~~~

The adapter is intentionally not connected to screen capture, mobile accessibility services, keyboard/mouse injection, or any external game. Actions are limited to navigation, waiting, regrouping, and recovery inside a controlled simulator.

## Hugging Face storage
Use a separate private Hugging Face Dataset repository for licensed training traces and a Model repository for checkpoints. Authenticate locally with the Hugging Face CLI; never put access tokens in GitHub, HTML, or a mobile bundle. Upload only after validating schema, consent, provenance, and license. See the official [dataset upload guide](https://huggingface.co/docs/hub/datasets-adding).

Suggested layout:
- Dataset: data/train.jsonl, data/validation.jsonl, README.md dataset card
- Model: config.json, model.pt, metrics.json, README.md model card
- Local only: raw videos, private tokens, personal data, and large temporary replay files

## Definition of done for v1.2
- [ ] Unit tests cover action validation, replay persistence, checkpoint save/load, and fixed-size observations.
- [ ] A deterministic simulator run can train for multiple episodes without manual action selection.
- [ ] Baseline and candidate are compared on the same seeds.
- [ ] A held-out evaluation report is saved with the checkpoint.
- [ ] The mobile wrapper remains a viewer for the research simulator, not a controller for another app.

## Current limitations
This commit provides the policy and memory core, not a trained model or finished autonomous player. The network starts untrained; real learning requires a simulator loop, reward design, training runs, and held-out evaluation. Do not claim performance until measured.

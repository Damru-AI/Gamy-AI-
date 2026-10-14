"""Gamy AI v1.2: simulator-only decision core.

No screen capture, operating-system input, or external-game control adapter is provided.
This module supplies a DQN policy and persistent episodic memory for a controlled
research environment with non-combat actions.
"""
from __future__ import annotations

import json
import random
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

import torch
from torch import nn
from torch.optim import Adam

ACTIONS: tuple[str, ...] = (
    "move_north", "move_south", "move_east", "move_west",
    "wait", "regroup", "recover",
)


@dataclass
class Experience:
    state: list[float]
    action: int
    reward: float
    next_state: list[float]
    terminated: bool
    episode_id: str


class EpisodicMemory:
    """Bounded replay buffer plus append-only JSONL persistence."""

    def __init__(self, capacity: int = 50_000, path: str | Path = "data/gamy_memory.jsonl"):
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        self.buffer: deque[Experience] = deque(maxlen=capacity)
        self.path = Path(path)

    def remember(self, item: Experience, persist: bool = True) -> None:
        self.buffer.append(item)
        if persist:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(asdict(item), separators=(",", ":")) + "\n")

    def sample(self, batch_size: int) -> list[Experience]:
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")
        if len(self.buffer) < batch_size:
            return []
        return random.sample(list(self.buffer), batch_size)

    def load_recent(self, limit: int = 50_000) -> int:
        """Load recent valid records, skipping malformed lines."""
        if limit < 1 or not self.path.exists():
            return 0
        valid: list[Experience] = []
        for line in self.path.read_text(encoding="utf-8").splitlines()[-limit:]:
            try:
                row = json.loads(line)
                item = Experience(
                    state=[float(x) for x in row["state"]],
                    action=int(row["action"]),
                    reward=float(row["reward"]),
                    next_state=[float(x) for x in row["next_state"]],
                    terminated=bool(row["terminated"]),
                    episode_id=str(row["episode_id"]),
                )
                if not 0 <= item.action < len(ACTIONS):
                    continue
                if len(item.state) != len(item.next_state):
                    continue
                valid.append(item)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                continue
        self.buffer.clear()
        self.buffer.extend(valid)
        return len(valid)


class QNetwork(nn.Module):
    def __init__(self, observation_size: int, action_count: int = len(ACTIONS), hidden_size: int = 128):
        super().__init__()
        if observation_size < 1:
            raise ValueError("observation_size must be >= 1")
        self.layers = nn.Sequential(
            nn.Linear(observation_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, action_count),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.layers(state)


class DQNAgent:
    """DQN policy for a custom simulator; not a real-game controller."""

    def __init__(
        self,
        observation_size: int,
        memory: EpisodicMemory | None = None,
        learning_rate: float = 1e-3,
        gamma: float = 0.98,
        epsilon: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        device: str | None = None,
    ):
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.online = QNetwork(observation_size).to(self.device)
        self.target = QNetwork(observation_size).to(self.device)
        self.target.load_state_dict(self.online.state_dict())
        self.target.eval()
        self.optimizer = Adam(self.online.parameters(), lr=learning_rate)
        self.memory = memory or EpisodicMemory()
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.observation_size = observation_size
        self.steps = 0

    def act(self, observation: Sequence[float], explore: bool = True) -> tuple[int, str]:
        if len(observation) != self.observation_size:
            raise ValueError(f"expected {self.observation_size} observation values")
        if explore and random.random() < self.epsilon:
            index = random.randrange(len(ACTIONS))
        else:
            with torch.no_grad():
                tensor = torch.tensor([list(observation)], dtype=torch.float32, device=self.device)
                index = int(self.online(tensor).argmax(dim=1).item())
        return index, ACTIONS[index]

    def train_step(self, batch_size: int = 64) -> float | None:
        batch = self.memory.sample(batch_size)
        if not batch:
            return None
        states = torch.tensor([x.state for x in batch], dtype=torch.float32, device=self.device)
        actions = torch.tensor([x.action for x in batch], dtype=torch.int64, device=self.device).unsqueeze(1)
        rewards = torch.tensor([x.reward for x in batch], dtype=torch.float32, device=self.device)
        next_states = torch.tensor([x.next_state for x in batch], dtype=torch.float32, device=self.device)
        terminals = torch.tensor([x.terminated for x in batch], dtype=torch.float32, device=self.device)
        q_values = self.online(states).gather(1, actions).squeeze(1)
        with torch.no_grad():
            next_q = self.target(next_states).max(dim=1).values
            targets = rewards + (1.0 - terminals) * self.gamma * next_q
        loss = nn.functional.smooth_l1_loss(q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.online.parameters(), max_norm=5.0)
        self.optimizer.step()
        self.steps += 1
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        if self.steps % 250 == 0:
            self.sync_target()
        return float(loss.detach().cpu().item())

    def sync_target(self) -> None:
        self.target.load_state_dict(self.online.state_dict())

    def save(self, path: str | Path, metadata: dict | None = None) -> None:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "online": self.online.state_dict(),
            "target": self.target.state_dict(),
            "observation_size": self.observation_size,
            "epsilon": self.epsilon,
            "steps": self.steps,
            "actions": list(ACTIONS),
            "metadata": metadata or {},
        }, destination)

    def load(self, path: str | Path) -> dict:
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        if checkpoint.get("actions") != list(ACTIONS):
            raise ValueError("checkpoint action vocabulary does not match this version")
        if int(checkpoint["observation_size"]) != self.observation_size:
            raise ValueError("checkpoint observation size does not match this agent")
        self.online.load_state_dict(checkpoint["online"])
        self.target.load_state_dict(checkpoint.get("target", checkpoint["online"]))
        self.epsilon = float(checkpoint.get("epsilon", self.epsilon))
        self.steps = int(checkpoint.get("steps", 0))
        return dict(checkpoint.get("metadata", {}))


def record_transition(
    memory: EpisodicMemory,
    state: Iterable[float],
    action_index: int,
    reward: float,
    next_state: Iterable[float],
    terminated: bool,
    episode_id: str,
) -> None:
    s = [float(x) for x in state]
    ns = [float(x) for x in next_state]
    if len(s) != len(ns):
        raise ValueError("state and next_state must have the same length")
    if not 0 <= action_index < len(ACTIONS):
        raise ValueError("action_index is outside the allowed simulator action set")
    memory.remember(Experience(s, action_index, float(reward), ns, bool(terminated), str(episode_id)))

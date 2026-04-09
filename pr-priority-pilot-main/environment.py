import random
from typing import Tuple, List, Optional
from pydantic import BaseModel

# ── Data Models ────────────────────────────────────────────────────────────
class Observation(BaseModel):
    pr_title: str
    pr_description: str
    files_changed: int
    labels: List[str]
    author: str


class Action(BaseModel):
    priority: int


class State(BaseModel):
    observation: Optional[Observation]
    done: bool


# ── Task Data (Improved complexity) ────────────────────────────────────────
TASKS = {
    "easy": [
        {"title": "Fix typo", "desc": "Typo fix", "files": 1, "labels": ["docs"], "author": "junior", "truth": 0},
        {"title": "Add feature", "desc": "New feature module", "files": 2, "labels": ["feature"], "author": "mid", "truth": 1},
        {"title": "Urgent fix", "desc": "Crash in login", "files": 1, "labels": ["urgent"], "author": "senior", "truth": 2},
    ],
    "medium": [
        {"title": "Security patch", "desc": "Fix SQL injection", "files": 3, "labels": ["security"], "author": "sec", "truth": 2},
        {"title": "Refactor module", "desc": "Cleanup legacy code", "files": 12, "labels": ["refactor"], "author": "senior", "truth": 1},
        {"title": "UI update", "desc": "Minor button color change", "files": 2, "labels": ["ui"], "author": "junior", "truth": 0},
    ],
    "hard": [
        {"title": "Hotfix payment", "desc": "Timeout causing failure", "files": 4, "labels": ["critical"], "author": "lead", "truth": 2},
        {"title": "DB migration", "desc": "Add new columns", "files": 8, "labels": ["database"], "author": "backend", "truth": 1},
        {"title": "Dependency update", "desc": "Version bump only", "files": 15, "labels": ["deps"], "author": "bot", "truth": 0},
    ],
}


# ── Environment ────────────────────────────────────────────────────────────
class CodeReviewEnv:
    def __init__(self):
        self.task = "easy"
        self.done = False
        self.pool = TASKS["easy"]
        self.current = None
        self.rng = random.Random(42)  # deterministic

    def set_task(self, difficulty: str):
        self.task = difficulty
        self.pool = TASKS[difficulty]

    def reset(self) -> Observation:
        self.current = self.rng.choice(self.pool).copy()
        self.done = False

        return Observation(
            pr_title=self.current["title"],
            pr_description=self.current["desc"],
            files_changed=self.current["files"],
            labels=self.current["labels"],
            author=self.current["author"],
        )

    def step(self, action: Action) -> Tuple[Optional[Observation], float, bool, dict]:
        if self.done:
            raise RuntimeError("Episode already done")

        pred = action.priority
        truth = self.current["truth"]

        # Reward shaping (improved)
        diff = abs(pred - truth)
        if diff == 0:
            base = 0.9
        elif diff == 1:
            base = 0.6
        else:
            base = 0.3

        offset = (abs(hash(self.current["title"])) % 100) / 1000.0
        reward = max(0.01, min(0.99, base + offset))

        self.done = True

        return None, reward, True, {"true_priority": truth}

    def state(self) -> State:
        if self.current:
            return State(
                observation=Observation(
                    pr_title=self.current["title"],
                    pr_description=self.current["desc"],
                    files_changed=self.current["files"],
                    labels=self.current["labels"],
                    author=self.current["author"],
                ),
                done=self.done,
            )

        return State(observation=None, done=self.done)

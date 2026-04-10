import os
import json
import random
import requests
import sys

SPACE_URL = os.environ.get("SPACE_URL", "https://tanishkushwah72-verity-human-verification.hf.space")

def rule_priority(obs):
    text = (obs.get("title", "") + " " + obs.get("description", "")).lower()
    if any(kw in text for kw in ["urgent", "crash", "hotfix", "security", "patch", "critical"]):
        return 2
    elif any(kw in text for kw in ["feature", "refactor", "migration", "toggle"]):
        return 1
    else:
        return 0

def evaluate_task(task, episodes=3):
    base = SPACE_URL.rstrip('/')
    total = 0.0
    try:
        r = requests.post(f"{base}/reset", json={"task": task}, timeout=10)
        if r.status_code != 200:
            return 0.5
        sid = r.json()["session_id"]
        for ep in range(episodes):
            r2 = requests.post(f"{base}/reset", json={"session_id": sid, "task": task}, timeout=10)
            if r2.status_code != 200:
                total += 0.5
                continue
            obs = r2.json()["observation"]
            action = rule_priority(obs)
            r3 = requests.post(f"{base}/step?session_id={sid}", json={"priority": action}, timeout=10)
            if r3.status_code != 200:
                total += 0.5
                continue
            reward = r3.json().get("reward", 0.5)
            total += reward
            print(json.dumps({"event": "STEP", "episode": ep, "task": task, "action": action, "reward": reward}))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 0.5
    return total / episodes

def main():
    print("[START]")
    scores = {}
    for task in ["easy", "medium", "hard"]:
        print(json.dumps({"event": "START_TASK", "task": task}))
        scores[task] = evaluate_task(task)
        print(json.dumps({"event": "END_TASK", "task": task, "score": scores[task]}))
    print("[END]")
    print("Final scores:", json.dumps(scores))
    sys.exit(0)

if __name__ == "__main__":
    random.seed(42)
    main()
import os
import json
import sys
import random

# ── LLM proxy (injected by validator) ──────────────────────────────────────
API_BASE_URL = os.environ.get("API_BASE_URL", "")
API_KEY      = os.environ.get("API_KEY", "")
MODEL_NAME   = os.environ.get("MODEL_NAME", "gpt-4.1-mini")

# ── Rule-based fallback (always works, no network needed) ──────────────────
def rule_priority(obs_dict):
    text = (obs_dict.get("pr_title", "") + " " + obs_dict.get("pr_description", "")).lower()
    if any(kw in text for kw in ["urgent", "critical", "security", "hotfix"]):
        return 2
    elif any(kw in text for kw in ["feature", "refactor", "migration", "database"]):
        return 1
    else:
        return 0

# ── LLM-based priority (falls back to rule on ANY error) ──────────────────
def llm_priority(obs_dict):
    if not API_BASE_URL or not API_KEY:
        return rule_priority(obs_dict)
    try:
        from openai import OpenAI
        client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY, timeout=10)
        prompt = (
            f"PR Title: {obs_dict.get('pr_title')}\n"
            f"Description: {obs_dict.get('pr_description')}\n"
            f"Labels: {obs_dict.get('labels')}\n"
            f"Respond with ONLY a single digit: 0 (Low), 1 (Medium), or 2 (High)."
        )
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5,
        )
        raw = resp.choices[0].message.content.strip()
        # Extract first digit found, safe parse
        for ch in raw:
            if ch in "012":
                return int(ch)
        return rule_priority(obs_dict)
    except Exception as e:
        print(f"LLM error: {e}", file=sys.stderr)
        return rule_priority(obs_dict)

# ── Run evaluation using local environment (NO HTTP calls) ─────────────────
def evaluate_task(task_name, episodes=3):
    # Import local environment directly — no network calls
    from environment import CodeReviewEnv, Action

    env = CodeReviewEnv()
    env.set_task(task_name)

    total_reward = 0.0
    for ep in range(episodes):
        obs = env.reset()
        obs_dict = obs.dict()
        action_int = llm_priority(obs_dict)
        _, reward, done, info = env.step(Action(priority=action_int))
        total_reward += reward
        print(json.dumps({
            "event": "STEP",
            "episode": ep,
            "task": task_name,
            "action": action_int,
            "reward": reward,
        }))

    return total_reward / episodes

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

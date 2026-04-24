import asyncio
import os
from typing import List, Optional
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

MAX_STEPS = 20


def log_start(task: str):
    print(f"[START] task={task} env=debug-env model={MODEL_NAME}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, observation: dict, error: Optional[str]):
    err = error if error else "null"
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err} "
        f"obs_error={observation.get('error')} "
        f"obs_logs={observation.get('logs')} "
        f"obs_metrics={observation.get('metrics')}",
        flush=True
    )


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_action(client: OpenAI, observation: dict, history: List[str]) -> str:
    prompt = f"""
You are an expert SRE debugging a distributed system.

Your goal:
1. Investigate the system
2. Identify root cause
3. Apply correct fix

Rules:
- Do NOT fix immediately
- First gather evidence using check_* actions
- Avoid repeating actions
- Root cause may NOT be in API
- Multiple services may be involved

Observation:
Error: {observation.get("error")}
Logs: {observation.get("logs")}
Metrics: {observation.get("metrics")}

Available actions:
check_api, check_auth, check_db, check_cache, check_queue, check_lb, check_app,
optimize_query, increase_pool, restart_db, cleanup_disk,
restart_auth, refresh_tokens, fix_invalid_token, increase_rate_limit,
clear_cache, scale_cache, restart_cache,
scale_consumers, restart_consumer, fix_ack_logic, restart_queue,
fix_routing, restart_lb,
restart_app, fix_memory, scale_app

Think step by step:
- What does the error suggest?
- Which service is most likely responsible?
- What should you inspect next?

Return ONLY the next action.
"""

    try:
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=20
        )

        action = res.choices[0].message.content.strip()

        return action

    except:
        return "check_logs"


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    # ✅ Run multiple tasks
    TASKS = [
        "auth_token_expired"
    ]

    for task_name in TASKS:

        rewards = []
        steps = 0
        success = False
        actions_taken = []   # ✅ NEW

        try:
            res = requests.post(f"{ENV_URL}/reset?task={task_name}").json()
        except Exception as e:
            print(f"[ERROR] Reset failed: {e}")
            continue

        observation = res.get("observation", {})
        log_start(task_name)

        for step in range(1, MAX_STEPS + 1):

            action = get_action(client, observation, actions_taken)

            # ✅ Safety: avoid repeat manually (backup protection)
            # if action in actions_taken:
            #     action = "check_metrics" if "check_metrics" not in actions_taken else "check_db"

            actions_taken.append(action)

            try:
                result = requests.post(
                    f"{ENV_URL}/step",
                    json={"action": action}
                ).json()

                reward = result.get("reward", 0.0)
                done = result.get("done", False)
                observation = result.get("observation", {})

                rewards.append(reward)
                steps = step

                log_step(step, action, reward, done, observation, None)

                if done:
                    break

            except Exception as e:
                log_step(step, action, 0.0, False, {}, str(e))
                break

        try:
            score_res = requests.get(f"{ENV_URL}/grade").json()
            score = score_res.get("score", 0.0)
        except:
            score = 0.0

        success = score > 0.4
        log_end(success, steps, score, rewards)
if __name__ == "__main__":
    asyncio.run(main())
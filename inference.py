import asyncio
import os
from typing import List, Optional
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

MAX_STEPS = 25


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
    prompt = f"""You are an expert SRE debugging a distributed microservice system.
System Flow : Client → Load Balancer → API → Auth → Database → Cache → Queue → Consumers
Load Balancer → Distributor (spreads traffic)
API → Gateway (entry point which routes requests across services)
Auth → Guard (checks identity)
Database → Storage (stores data)
Cache → Speedup (fast access)
Queue → Line (waits tasks)
Error: {observation.get("error")}
Logs: {observation.get("logs") or "No evidence gathered yet"}
Metrics: {observation.get("metrics") or "No metrics gathered yet"}
History(action taken so far): {', '.join(history) if history else "None yet"}
Rules:Do not repeat actions.Investigate before fixing
Choose the next action from below by carefully analyzing the logs, metrics, and current observations:
check_auth, check_db, check_cache, check_queue, check_lb, check_api
optimize_query, increase_pool, restart_db, cleanup_disk
restart_auth, refresh_tokens, fix_invalid_token, increase_rate_limit
clear_cache, scale_cache, restart_cache
scale_consumers, restart_consumer, fix_ack_logic
fix_routing, restart_lb
Return ONLY one action.
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
        "auth_token_expired",
        "invalid_token",
        "auth_service_down",
        "rate_limit_auth",
        "slow_query",
        "connection_pool_exhausted",
        "database_down",
        "disk_full",
        "stale_cache_issue",
        "cache_miss_issue",
        "cache_down",
        "queue_backlog",
        "consumer_down",
        "message_loss", 
        "uneven_routing", 
        "lb_down", 
        "auth_db_combined_issue",
        "cache_queue_dependency", 
        "full_system_failure" 
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

        # action_counts = {}
        for step in range(1, MAX_STEPS + 1):

            action = get_action(client, observation, actions_taken)

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
                    success = True
                    break

            except Exception as e:
                log_step(step, action, 0.0, False, {}, str(e))
                break

        try:
            score_res = requests.get(f"{ENV_URL}/grade").json()
            score = score_res.get("score", 0.0)
        except:
            score = 0.0
        
        log_end(success, steps, score, rewards)
if __name__ == "__main__":
    asyncio.run(main())
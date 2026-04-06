import asyncio
import os
from typing import List, Optional
from openai import OpenAI
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

MAX_STEPS = 10


def log_start(task: str):
    print(f"[START] task={task} env=debug-env model={MODEL_NAME}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    err = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={err}", flush=True)


def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)


def get_action(client: OpenAI, observation: dict) -> str:
    prompt = f"""
You are debugging a production issue.

Observation:
Error: {observation.get("error")}
Logs: {observation.get("logs")}
Metrics: {observation.get("metrics")}

Choose ONE action:
check_logs, check_db, check_memory, fix_db, optimize_query,
restart_service, check_service, check_cache, fix_cache,
check_auth_service, validate_token, fix_auth,
check_routing, check_lb, fix_lb,
restart_db, check_rate_limit, increase_limit,
analyze_traffic, block_ip

Return ONLY the action string.
"""

    try:
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=20
        )
        return res.choices[0].message.content.strip()
    except:
        return "check_logs"


async def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

    rewards = []
    steps = 0
    success = False

    # 1. RESET - Use .get() to prevent KeyError crashes
    try:
        res = requests.post(f"{ENV_URL}/reset").json()
    except Exception as e:
        print(f"[ERROR] Could not connect to Environment: {e}")
        return

    # Extract observation safely
    observation = res.get("observation", {})
    
    # Use a generic name for the log (Rules: LLM shouldn't know the task name)
    task_name = "openenv-debug-task" 
    
    log_start(task_name)

    # 2. STEP LOOP
    for step in range(1, MAX_STEPS + 1):
        action = get_action(client, observation)
        
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
            
            log_step(step, action, reward, done, None)
            
            if done:
                break
        except Exception as e:
            log_step(step, action, 0.0, False, str(e))
            break

    # 3. GET SCORE
    try:
        score_res = requests.get(f"{ENV_URL}/grade").json()
        score = score_res.get("score", 0.0)
    except:
        score = 0.0

    success = score > 0.5
    log_end(success, steps, score, rewards)


if __name__ == "__main__":
    asyncio.run(main())
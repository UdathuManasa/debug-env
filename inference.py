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
 
=== DEBUGGING PROCESS ===
 
Phase 1: IDENTIFY
- Read the initial hints to understand which services might be involved
- Plan which services to investigate
 
Phase 2: INVESTIGATE  
- Use check_* actions to gather evidence
- Each check reveals logs and metrics for that service
- You need evidence before applying fixes
 
Phase 3: FIX
- Once you have enough evidence, apply the correct fix
- Match the symptoms to the right solution
 
=== CURRENT SITUATION ===
 
Error: {observation.get("error")}
 
Hints/Logs: {observation.get("logs") if observation.get("logs") else "No evidence gathered yet"}
 
Metrics: {observation.get("metrics") if observation.get("metrics") else "No metrics gathered yet"}
 
Actions taken: {', '.join(history) if history else 'None yet'}
 
=== CRITICAL RULES ===
 
1. **Never repeat an action** - Each check should be done once
2. **Investigate before fixing** - Don't guess, gather evidence first
3. **Multiple services may be involved** - Check all suspicious services
4. **Match symptoms to solutions** - Use the mapping below
 
=== INVESTIGATION ACTIONS ===
 
check_auth    → Reveals: token issues, auth errors, rate limits
check_db      → Reveals: query performance, connection pools, disk space
check_cache   → Reveals: hit rates, stale data, cache status  
check_queue   → Reveals: backlog, consumer status, message processing
check_lb      → Reveals: routing distribution, traffic imbalance
check_api     → Reveals: overall API metrics (usually not the root cause)
 
=== SYMPTOM → FIX MAPPING ===
 
Authentication Issues:
  "Token validation failed" + "Expiry timestamp older" → refresh_tokens
  "JWT signature verification failed" → fix_invalid_token
  "Connection refused to auth service" → restart_auth
  "Too many requests" + "Rate limit" → increase_rate_limit
 
Database Issues:
  "Execution time exceeded" + "Sequential scan" → optimize_query
  "Pool limit reached" + "Timeout acquiring connection" → increase_pool
  "Connection refused" + "Database not reachable" → restart_db
  "Disk space full" + "Write operations failing" → cleanup_disk
 
Cache Issues:
  "Serving outdated data" + "invalidation delay" → clear_cache
  "Cache miss rate increasing" → scale_cache
  "Cache not reachable" → restart_cache
 
Queue Issues:
  "Message backlog increasing" + "unable to keep up" → scale_consumers
  "No active consumers" → restart_consumer
  "Message acknowledgment failures" → fix_ack_logic
 
Load Balancer Issues:
  "Traffic unevenly distributed" → fix_routing
  "Load balancer not responding" → restart_lb
 
=== DECISION LOGIC ===
 
**If logs are empty or just hints:**
→ You're in Phase 1 (IDENTIFY)
→ Look at the hints to decide which service(s) to check
→ Action: check_<service> based on hints
 
**If logs contain specific error messages but you haven't checked all relevant services:**
→ You're in Phase 2 (INVESTIGATE)
→ Continue checking services mentioned in hints
→ Action: check_<next_service>
 
**If logs clearly show a known issue pattern AND you've checked the affected service:**
→ You're in Phase 3 (FIX)
→ Match the symptoms to the fix using the mapping above
→ Action: <fix_action>
 
=== EXAMPLES ===
 
Example 1:
  Hints: "Authentication-related symptoms detected"
  Action: check_auth (investigate the hint)
 
Example 2:
  Logs: "Token validation failed | Expiry timestamp older than current time"
  Action: refresh_tokens (clear symptom match)
 
Example 3:
  Hints: "Database performance indicators | Authentication-related symptoms"
  History: []
  Action: check_db (start with first hint)
 
Example 4:
  Hints: "Database performance indicators | Authentication-related symptoms"  
  History: [check_db]
  Logs: "Execution time exceeded threshold"
  Action: check_auth (check second service before fixing)
 
Example 5:
  History: [check_db, check_auth]
  Logs: "Pool limit reached | Timeout acquiring connection"
  Action: increase_pool (both services checked, clear fix)
 
=== YOUR TASK ===
 
Based on the current situation above, what is the next action?
 
Think step by step:
1. What phase am I in? (Identify / Investigate / Fix)
2. What have I learned so far?
3. What's the next logical step?
 
Return ONLY the action name (e.g., "check_db" or "optimize_query").
Do not explain, just return the action.
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
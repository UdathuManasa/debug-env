"""
FIXED Gradio UI for Debug Environment

Problems in original:
1. Trying to get actions_taken from observation (doesn't exist there)
2. Not tracking task selection
3. State management issues
4. Output mismatches

This version WORKS!
"""

import gradio as gr
import requests
from typing import List, Tuple

# ==================== CONFIG ====================

BASE_URL = "http://localhost:7860"

ACTIONS = [
    "check_db", "check_auth", "check_cache", "check_queue", "check_lb", "check_api",
    "optimize_query", "increase_pool", "restart_db", "cleanup_disk",
    "restart_auth", "refresh_tokens", "fix_invalid_token", "increase_rate_limit",
    "clear_cache", "scale_cache", "restart_cache",
    "scale_consumers", "restart_consumer", "fix_ack_logic", "restart_queue",
    "fix_routing", "restart_lb",
    "restart_api", "scale_api"
]

# ==================== ENVIRONMENT CLIENT ====================

class DebugEnvClient:
    """Client for debug environment."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
    
    def get_tasks(self) -> List[str]:
        """Get available tasks."""
        try:
            response = requests.get(f"{self.base_url}/tasks", timeout=5)
            return response.json()["tasks"]
        except Exception as e:
            print(f"Error getting tasks: {e}")
            return ["auth_token_expired", "slow_query", "database_down"]
    
    def reset(self, task: str = None) -> dict:
        """Reset environment."""
        try:
            url = f"{self.base_url}/reset"
            if task:
                url += f"?task={task}"
            response = requests.post(url, timeout=5)
            return response.json()
        except Exception as e:
            print(f"Reset error: {e}")
            return {
                "observation": {
                    "error": f"Connection Error: {e}",
                    "logs": "",
                    "metrics": {}
                },
                "reward": 0,
                "done": False
            }
    
    def step(self, action: str) -> dict:
        """Execute action."""
        try:
            response = requests.post(
                f"{self.base_url}/step",
                json={"action": action},
                timeout=5
            )
            return response.json()
        except Exception as e:
            print(f"Step error: {e}")
            return {
                "observation": {
                    "error": f"Connection Error: {e}",
                    "logs": "",
                    "metrics": {}
                },
                "reward": 0,
                "done": False
            }
    
    def state(self) -> dict:
        """Get current state."""
        try:
            response = requests.get(f"{self.base_url}/state", timeout=5)
            return response.json()
        except Exception as e:
            print(f"State error: {e}")
            return {
                "task": "unknown",
                "actions_taken": [],
                "total_reward": 0,
                "done": False
            }
    
    def grade(self) -> float:
        """Get final score."""
        try:
            response = requests.get(f"{self.base_url}/grade", timeout=5)
            return response.json()["score"]
        except Exception as e:
            print(f"Grade error: {e}")
            return 0.0


# ==================== GLOBAL STATE ====================

env = DebugEnvClient(BASE_URL)

# UI state (separate from environment state)
ui_state = {
    "current_task": None,
    "action_history": [],
    "reward_history": [],
    "total_reward": 0.0,
    "done": False
}


# ==================== UI FUNCTIONS ====================

def reset_environment(task_name: str) -> Tuple[str, str, str, str, float, str, str]:
    """
    Reset the environment to a new task.
    
    Returns: (error, logs, metrics, history, reward, status, task_display)
    """
    global ui_state
    
    # Reset UI state
    ui_state = {
        "current_task": task_name,
        "action_history": [],
        "reward_history": [],
        "total_reward": 0.0,
        "done": False
    }
    
    # Reset environment
    result = env.reset(task_name)
    obs = result.get("observation", {})
    
    error = obs.get("error", "No error")
    logs = obs.get("logs", "No logs yet")
    metrics = str(obs.get("metrics", {}))
    history = "No actions yet"
    reward = 0.0
    status = f"✅ Task '{task_name}' reset successfully. Start debugging!"
    task_display = f"Current Task: {task_name}"
    
    return error, logs, metrics, history, reward, status, task_display


def execute_action(action: str) -> Tuple[str, str, str, str, float, str, str]:
    """
    Execute an action in the environment.
    
    Returns: (error, logs, metrics, history, reward, status, task_display)
    """
    global ui_state
    
    if ui_state["done"]:
        return (
            "Task completed",
            "Task is done",
            "{}",
            format_history(),
            0.0,
            "⚠️ Task already completed. Reset to start a new task.",
            f"Current Task: {ui_state['current_task']} (COMPLETED)"
        )
    
    # Execute action
    result = env.step(action)
    obs = result.get("observation", {})
    reward = result.get("reward", 0.0)
    done = result.get("done", False)
    
    # Update UI state
    ui_state["action_history"].append(action)
    ui_state["reward_history"].append(reward)
    ui_state["total_reward"] += reward
    ui_state["done"] = done
    
    # Format outputs
    error = obs.get("error", "No error")
    logs = obs.get("logs", "No logs")
    metrics = str(obs.get("metrics", {}))
    history = format_history()
    
    # Status message
    if done:
        score = env.grade()
        status = f"🎉 Task COMPLETED! Score: {score:.3f} | Total Reward: {ui_state['total_reward']:.2f}"
    else:
        status = f"Action '{action}' executed | Reward: {reward:.2f} | Total: {ui_state['total_reward']:.2f}"
    
    task_display = f"Current Task: {ui_state['current_task']}"
    if done:
        task_display += " (COMPLETED ✅)"
    
    return error, logs, metrics, history, reward, status, task_display


def format_history() -> str:
    """Format action history for display."""
    if not ui_state["action_history"]:
        return "No actions yet"
    
    lines = []
    for i, (action, reward) in enumerate(zip(ui_state["action_history"], ui_state["reward_history"]), 1):
        emoji = "✅" if reward > 0 else "❌"
        lines.append(f"{i}. {action:25s} → Reward: {reward:6.2f} {emoji}")
    
    lines.append(f"\nTotal Reward: {ui_state['total_reward']:.2f}")
    
    return "\n".join(lines)


# ==================== GRADIO UI ====================

with gr.Blocks(title="Debug Environment", theme=gr.themes.Soft()) as demo:
    
    gr.Markdown("""
    # 🛠️ Debug Environment - RL Agent Interface
    
    Debug a distributed microservice system by investigating services and applying fixes.
    """)
    
    # Task display
    task_display = gr.Markdown("**Current Task:** None (click Reset to start)")
    
    with gr.Row():
        # Left column: Controls
        with gr.Column(scale=1):
            gr.Markdown("### 🎯 Task Control")
            
            # Get tasks from server
            try:
                available_tasks = env.get_tasks()
            except:
                available_tasks = ["auth_token_expired", "slow_query", "database_down"]
            
            task_dropdown = gr.Dropdown(
                choices=available_tasks,
                label="Select Task",
                value=available_tasks[0] if available_tasks else None
            )
            
            reset_btn = gr.Button("🔄 Reset Task", variant="primary", size="lg")
            
            gr.Markdown("### 🎮 Action Control")
            
            action_dropdown = gr.Dropdown(
                choices=ACTIONS,
                label="Select Action",
                value=ACTIONS[0]
            )
            
            execute_btn = gr.Button("▶️ Execute Action", variant="secondary", size="lg")
            
            gr.Markdown("### 📊 Metrics")
            
            reward_display = gr.Number(
                label="Last Reward",
                value=0.0,
                precision=2,
                interactive=False
            )
        
        # Right column: Observation
        with gr.Column(scale=2):
            gr.Markdown("### 🔍 Current Observation")
            
            error_box = gr.Textbox(
                label="System Error",
                lines=2,
                interactive=False,
                value="Click 'Reset Task' to begin"
            )
            
            logs_box = gr.Textbox(
                label="System Logs",
                lines=5,
                interactive=False,
                value="No logs yet"
            )
            
            metrics_box = gr.Textbox(
                label="Metrics",
                lines=3,
                interactive=False,
                value="{}"
            )
    
    # Status bar
    status_box = gr.Textbox(
        label="Status",
        interactive=False,
        value="Ready. Select a task and click Reset."
    )
    
    # Action history
    with gr.Row():
        history_box = gr.Textbox(
            label="📝 Action History",
            lines=10,
            interactive=False,
            value="No actions yet"
        )
    
    # Event handlers
    reset_btn.click(
        fn=reset_environment,
        inputs=[task_dropdown],
        outputs=[error_box, logs_box, metrics_box, history_box, reward_display, status_box, task_display]
    )
    
    execute_btn.click(
        fn=execute_action,
        inputs=[action_dropdown],
        outputs=[error_box, logs_box, metrics_box, history_box, reward_display, status_box, task_display]
    )
    
    gr.Markdown("""
    ---
    ### 💡 Tips
    
    1. **Select a task** and click "Reset Task"
    2. **Investigate** using `check_*` actions to gather evidence
    3. **Apply fixes** once you understand the problem
    4. Higher scores = better investigation + correct fix!
    
    **Common Patterns:**
    - Auth issues → `check_auth` → identify symptom → apply auth fix
    - DB issues → `check_db` → identify symptom → apply DB fix
    - Multi-root → check BOTH services before fixing
    """)


# ==================== LAUNCH ====================

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7861,
        share=True  # Creates public link for hackathon demo!
    )
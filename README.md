---
title: Debug Env
emoji: 🔧
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

## 🛠️ The "Debug-Env" Task Registry (11 Scenarios)

This environment features a Registry-based Grader System designed to evaluate an LLM's ability to reason through complex, non-linear debugging scenarios. Unlike basic "error-match" tasks, these 11 scenarios include Agentic Traps and Multi-step Dependencies.

## 🚀 Key Features
- **11 Unique Scenarios:** Covering Infrastructure, Security, and Application Logic.
- **Agentic Traps:** Built-in "Red Herring" logs to test if the LLM trusts raw metrics over misleading text logs.
- **Stateful Sequential Logic:** Tasks are served via a rotating registry to ensure robustness across evaluation episodes.
- **Granular Reward Modeling:** Sparse reward signals that prioritize resolution efficiency and accuracy.

### 🏗️ Infrastructure & Performance
- **api_latency** → Detect middleware vs downstream latency.
- **db_performance** → Identify indexing vs connection issues.
- **database_down** → Service health + connectivity debugging.
- **load_balancer_issue** → Traffic imbalance across nodes.
### 🔐 Security & Compliance
- **auth_failure** → Token expiry vs IAM misconfiguration.
- **security_breach** → Hidden malicious activity behind system noise.
- **rate_limit_issue** → Detect 429 + suggest throttling fixes.
### 🧠 Agentic Reasoning & Observation Traps
- **misleading_logs (Hardest)** → Logs show success but metrics fail.
- **retry_trap_issue** → Infinite retry loop detection.
- **multi_root_issue** → Cascading failures.
- **misleading_cache_issue** → Stale cache vs fresh headers.

## 🏗️ Technical Architecture
The environment is built using a **Registry-based Design Pattern**, allowing for decoupled task logic and grader validation.

### System Flow
1. **Reset:** Agent requests a task (e.g., `api_latency`).
2. **Observe:** Server returns a JSON observation containing `logs`, `metrics`, and `error_states`.
3. **Step:** Agent selects an action (e.g., `fix_db`).
4. **Evaluate:** The custom **Grader Class** calculates the reward based on the state transition.

## 🔌 API Reference

The environment exposes four primary REST endpoints via **FastAPI** to facilitate the RL feedback loop.

### 1. `POST /reset`
**Purpose:** Initializes a new debugging session.
- **Returns:** A `StepResult` object containing:
    - `observation`: The initial state (logs, metrics, errors) of the task.
    - `reward`: Initialized to `0.0`.
    - `done`: Initialized to `False`.
    - `info`: Diagnostic metadata including `progress`, `remaining_steps`, and `total_steps_taken`.

### 2. `POST /step`
**Purpose:** Executes an agent action and transitions the environment state.
- **Request Body:** `{"action": "string"}`
- **Returns:** - `observation`: Updated logs/metrics after the action.
    - `reward`: Floating point value (e.g., `1.0` for success).
    - `done`: Boolean indicating if the issue is resolved.
    - `info` (Optional Metadata): Contains diagnostic data such as `total_steps_taken` and `remaining_steps`. 
      *(Note: Standard inference clients may choose to ignore this field during high-speed evaluation.)*

### 3. `GET /grade`
**Purpose:** Final evaluation of the agent's performance.
- **Returns:** `{"score": float}`
- **Technical Note:** Calculates the final score based on task completion and step efficiency. This endpoint is used by the **Meta Validator** to determine the final leaderboard standing.

### 4. `GET /state`
**Purpose:** System telemetry and observability.
- **Returns:** The current internal state, including the active task, history of actions taken, and cumulative rewards. Useful for real-time monitoring of the agent's "thought process."

## 🛠️ Installation & Execution
This project uses uv for fast, reproducible dependency management.
### Run the Environment Server
uv run python -m server.app
### Prerequisites
- Python 3.10+
- Docker
- Git
- OpenEnv CLI
- uv (dependency manager)
### Install dependencies
- pip install fastapi uvicorn requests
- pip install openenv
- pip install uv
- uv lock ( to generate lock file)
### 🐳 Docker Setup
 docker build -t debug-env .
### Validate Enviroment
openenv validate --url http://localhost:7860
### deployment (hugging face)
uv run openenv push --repo-id Udathu/debug-env
## 🧩 Tech Stack
- FastAPI (backend environment)
- Pydantic (typed models)
- Docker (containerization)
- OpenEnv (environment standard)
- Hugging Face (deployment)
- OpenAI-compatible LLM API (inference)


<img width="1536" height="1024" alt="d6354b5e-9636-468f-ac99-35095a6038a8" src="https://github.com/user-attachments/assets/95f420c0-27ea-4bd5-981c-91c42822b2d8" />

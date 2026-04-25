# 🔧 Debug-Env: Agentic Debugging for Distributed Systems

🚀 A reinforcement learning environment where agents learn to debug real-world distributed systems using reasoning, not pattern matching.

---

## 🌐 Live Demo

* 🔗 Hugging Face Space: **[ADD_YOUR_HF_SPACE_URL]**
* 📓 Training Notebook (Colab): **[ADD_COLAB_LINK]**
* 📊 Training Results (plots included below)

---

## 📌 Problem Statement

Debugging distributed systems is hard because:

* Failures propagate across services
* Logs can be misleading
* Metrics and symptoms don’t always match
* Root cause is often hidden behind downstream effects

👉 Traditional systems rely on rules.
👉 This environment trains agents to **reason like an SRE**.

---

## 🧠 Themes Covered

### ✅ Multi-Agent Interactions (Primary)

* Each service behaves like an independent agent
* Failures require cross-service reasoning

### ✅ Sequential Decision Making

* Multi-step debugging process (investigate → fix)

### ✅ Partially Observable Systems

* Agent never sees full system state at once

### ✅ Tool Use / Agentic Environments

* Actions like `check_*` and `fix_*` act as tools

---

## 🏗️ System Architecture

### 🔄 Request Flow

```text
Client → Load Balancer → API → Auth → App → DB ↔ Cache → Queue → Consumers
```

---

## 🔗 Service Responsibilities

### 🌐 Load Balancer

* Routes traffic
* Failure → no requests or uneven routing

### 🚪 API Gateway

* Entry point
* Shows symptoms (not root cause)

### 🔐 Auth Service

* Token validation
* Failures → 401 errors

### ⚙️ App Server

* Business logic layer
* Depends on Auth, DB, Cache

### 🗄️ Database

* Storage layer
* Issues → latency, connection failures

### ⚡ Cache

* Reduces DB load
* Issues → stale data, high latency

### 📬 Queue + Consumers

* Async processing
* Issues → backlog, delays, message loss

---

## ⚠️ Failure Propagation (Core Challenge)

Failures are interconnected:

* Auth failure → API shows 401
* DB failure → API latency spikes
* Cache miss → DB overload
* Queue backlog → delayed responses

👉 Agent must learn:

> **“Fix the root cause, not the symptom.”**

---

## 🤖 Agent Capabilities

The agent can:

* 🔍 Investigate (`check_auth`, `check_db`, etc.)
* 🧠 Correlate logs + metrics
* 🔗 Understand service dependencies
* 🛠️ Apply fixes (`restart_db`, `fix_routing`, etc.)
* 🚫 Avoid repeated or useless actions

---

## 🎯 Tasks (19 Scenarios)

### 🔐 Authentication

* auth_token_expired
* invalid_token
* auth_service_down
* rate_limit_auth

### 🗄️ Database

* slow_query
* connection_pool_exhausted
* database_down
* disk_full

### ⚡ Cache

* stale_cache_issue
* cache_miss_issue
* cache_down

### 📬 Queue

* queue_backlog
* consumer_down
* message_loss

### 🌐 Load Balancer

* uneven_routing
* lb_down

### 🧠 Complex Multi-Service

* auth_db_combined_issue
* cache_queue_dependency
* full_system_failure

---

## 🧮 Reward Model

| Action                  | Reward     |
| ----------------------- | ---------- |
| Useful investigation    | +3         |
| Wrong / repeated action | -2         |
| Correct fix             | +20 to +30 |

### 🎯 Goal

* Solve issue in minimum steps
* Avoid unnecessary actions

### 📊 Final Score

Retrieved via:

```
GET /grade
```

---

## 🔌 API Endpoints

### POST /reset

Start a new task

### POST /step

Take action:

```json
{"action": "check_db"}
```

### GET /grade

Final score

### GET /state

Debug internal state

---

## 🏗️ OpenEnv Compliance

* ✅ Gym-style `reset()` / `step()`
* ✅ OpenEnv YAML config
* ✅ MCPEnvironment compatible
* ✅ Fully deployable via Hugging Face

---

## 🧠 Training Strategy (TRL + GRPO)

We use:

* 🤗 TRL (Transformer Reinforcement Learning)
* GRPO (Group Relative Policy Optimization)

### Training Setup

* Environment used for rollouts
* Reward signals guide learning
* Dataset = repeated task prompts

---

## 📊 Training Results

### Reward Curve

![Reward Curve](./assets/reward_curve.png)

### Loss Curve

![Loss Curve](./assets/loss_curve.png)

👉 Results show:

* Faster convergence to correct actions
* Reduced repetition
* Improved multi-step reasoning

---

## 🔁 Post-Training Improvements

* Better root cause identification
* Handles multi-service failures
* Avoids redundant actions

---

## 🚀 How to Run

### Install

```bash
pip install fastapi uvicorn openenv requests
```

### Run Environment

```bash
uv run python -m server.app
```

### Validate

```bash
openenv validate --url http://localhost:7860
```

---

## 🐳 Docker

```bash
docker build -t debug-env .
```

---

## 🤖 Inference

```bash
python inference.py
```

---

## 🧩 Tech Stack

* FastAPI
* OpenEnv
* Hugging Face Spaces
* TRL (RL Training)
* Docker

---

## 🏆 Key Insight

This project moves beyond:

❌ Pattern matching
→
✅ **Causal reasoning in distributed systems**

---

## 📢 Why This Matters

This environment trains agents to:

* Debug production systems
* Understand system dependencies
* Make decisions under uncertainty

👉 This is directly applicable to:

* DevOps automation
* Incident response systems
* Autonomous SRE agents

---

## 📎 Submission Checklist

* ✅ Public Hugging Face Space
* ✅ OpenEnv compliant environment
* ✅ Training notebook (Colab)
* ✅ Reward + Loss plots (in repo)
* ✅ README with all links

---

## 👩‍💻 Author

Manasa U
Software Engineer | Distributed Systems | RL Systems

## 🛠️ The "Debug-Env" Task Registry (19 Scenarios)

This environment features a **Registry-based Grader System** designed to evaluate an agent’s ability to debug **realistic distributed system failures**.

Unlike simple error-classification tasks, these scenarios require:

* Multi-step reasoning
* Cross-service dependency understanding
* Distinguishing **root cause vs symptom**
* Handling **misleading or incomplete signals**

Each task is designed to simulate **production-grade debugging situations** faced by SREs.

---

## 🚀 Key Features

* **19 Realistic Scenarios:** Covering Authentication, Database, Cache, Queue, Load Balancer, and Multi-service failures
* **Stateful Sequential Logic:** Tasks evolve over steps; actions influence future observations
* **Cross-Service Dependencies:** Failures propagate across services (not isolated issues)
* **Sparse Reward Modeling:** Encourages efficient debugging and penalizes redundant actions
* **Partial Observability:** Agent must infer root cause from limited logs and metrics

---

## 🧠 Scenario Categories

### 🔐 Authentication & Security

* `auth_token_expired` → Expired credentials causing auth failures
* `invalid_token` → Signature / token validation issues
* `auth_service_down` → Auth service outage impacting entire system
* `rate_limit_auth` → Throttling due to excessive requests

---

### 🗄️ Database & Storage

* `slow_query` → Inefficient queries causing latency
* `connection_pool_exhausted` → DB connection limits reached
* `database_down` → Complete database outage
* `disk_full` → Storage exhaustion blocking writes

---

### ⚡ Cache Layer

* `stale_cache_issue` → Serving outdated data
* `cache_miss_issue` → Low hit rate increasing DB load
* `cache_down` → Cache service unavailable

---

### 📬 Queue & Async Processing

* `queue_backlog` → Messages accumulating faster than processing
* `consumer_down` → No active consumers
* `message_loss` → Acknowledgment failures causing retries

---

### 🌐 Load Balancer & Traffic Routing

* `uneven_routing` → Traffic skew across instances
* `lb_down` → Load balancer unavailable

---

### 🧠 Complex Multi-Service Failures

* `auth_db_combined_issue` → Authentication + DB dependency failure
* `cache_queue_dependency` → Cache inefficiency causing queue backlog
* `full_system_failure` → Cascading failure across multiple services

---

## 🏗️ Technical Architecture

The environment is built using a **Registry-based Design Pattern**, enabling:

* Decoupled task definitions
* Modular grading logic
* Scalable scenario addition
* Consistent evaluation across episodes

---

## 🔄 System Flow (RL Loop)

1. **Reset**
   Agent requests a new task → receives initial observation

2. **Observe**
   Observation includes:

   * Logs (text signals)
   * Metrics (quantitative signals)
   * Error states (symptoms)

3. **Step**
   Agent selects an action:

   * Investigation → `check_*`
   * Fix → `fix_*`

4. **Evaluate**
   A custom **Grader Engine**:

   * Updates environment state
   * Assigns reward
   * Determines if task is resolved

---

## 🔍 Observability Model

Each step returns structured signals:

* **Logs:** Human-readable but potentially misleading
* **Metrics:** Reliable but require interpretation
* **Errors:** Surface-level symptoms

👉 The agent must **correlate all three** to infer root cause.

---

## ⚠️ Core Challenge: Failure Propagation

This environment models **real distributed system behavior**:

* Upstream failures affect downstream services
* Symptoms appear far from root cause
* Multiple services may fail simultaneously

### Example:

```text
Auth failure → API returns 401 → Looks like API issue  
DB latency → API slow → Looks like API bottleneck  
Cache miss → DB overload → Cascading failure  
```

👉 The agent must learn:

> **"Where the issue originates, not where it appears."**

---

## 🔌 API Reference

The environment exposes four primary REST endpoints via **FastAPI** to facilitate the RL feedback loop.

### 1. `POST /reset`

**Purpose:** Initializes a new debugging session

Returns:

* `observation`
* `reward = 0.0`
* `done = False`
* `info` (diagnostics)

---

### 2. `POST /step`

**Purpose:**Executes an action

Request:

```json
{"action": "check_db"}
```

Returns:

* Updated `observation`
* `reward`
* `done`
* `info` (optional diagnostics)

---

### 3. `GET /grade`

**Purpose:**Returns final score:

```json
{"score": float}
```

Used by evaluation system.

---

### 4. `GET /state`

**Purpose:**Returns internal state:

* current task
* action history
* cumulative reward

Useful for debugging agent behavior.

---

## 🛠️ Installation & Execution

### Run Environment

```bash
uv run python -m server.app
```

---

### Prerequisites

* Python 3.10+
* Docker
* OpenEnv CLI
* uv

---

### Install Dependencies

```bash
pip install fastapi uvicorn requests openenv uv
uv lock
```

---

### 🐳 Docker

```bash
docker build -t debug-env .
```

---

### ✅ Validate Environment

```bash
openenv validate --url http://localhost:7860
```

---

### 🚀 Deploy to Hugging Face

```bash
uv run openenv push --repo-id Udathu/debug-env
```

---

## 🧩 Tech Stack

* FastAPI (backend)
* Pydantic (data models)
* OpenEnv (environment framework)
* Docker (deployment)
* Hugging Face Spaces
* OpenAI-compatible LLM API

---

## 💡 Key Insight

This environment evaluates whether an agent can:

* Understand **system design**
* Perform **causal reasoning**
* Handle **multi-step debugging**
* Distinguish **signal vs noise**

👉 It is not solving for pattern matching —
👉 It is solving for **real-world debugging intelligence**

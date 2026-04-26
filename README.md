# 🔧 Debug-Env: Training LLMs to Perform Root Cause Analysis in Distributed Systems

🚀 An OpenEnv-compatible RL environment where agents learn **production-grade debugging** through multi-step reasoning, cross-service interaction, and causal inference.

---

## 🏆 Elevator Pitch

> We built an environment that teaches LLMs to debug distributed systems like SREs — by investigating, reasoning across services, and fixing root causes under uncertainty.

---

## 🌐 Links

* 🔗 Hugging Face Space: **[ADD_URL]**
* 📓 Training Notebook (Colab): **[ADD_LINK]**
* 📊 Reward & Loss Plots: *(below)*
* 🎥 Demo / Blog: **[ADD_LINK]**

---

# 🎯 Problem

LLMs today struggle with **real-world debugging**:

* They repeat actions
* They fix symptoms, not root causes
* They fail in multi-service systems

👉 Debugging requires:

* long-horizon reasoning
* system-level understanding
* decision-making under uncertainty

---

# 🧠 Themes Covered (Direct Mapping)

## 🎯 Theme #1 — Multi-Agent Interactions (Primary)

Each service behaves like an independent agent:

* Auth
* Database
* Cache
* Queue
* Load Balancer

Failures propagate across services.

👉 The agent must:

* reason about dependencies
* distinguish upstream vs downstream
* coordinate across components

---

## ⏳ Theme #2 — Long-Horizon Planning & Instruction Following

Debugging requires **multi-step planning**:

```text
check_api → check_auth → identify failure → apply fix
```

The agent learns to:

* gather evidence before acting
* avoid premature fixes
* follow structured debugging instructions

---

## 🌍 Theme #3 — World Modeling

The environment simulates a **hidden system state**.

Agent only observes:

* logs (noisy)
* metrics (partial truth)
* errors (symptoms)

👉 The agent builds an internal model of:

* system dependencies
* failure propagation
* causal relationships

---

## 🔁 Theme #4 — Self-Improvement

Using GRPO training:

* Agent explores actions
* Receives reward feedback
* Improves policy over time

👉 Observed improvements:

* reduced repetition
* better action sequencing
* higher success rate

---

## 🎲 Theme #5 — Wild Card (Our Edge)

We introduce:

* **Misleading logs vs truthful metrics**
* **Cascading multi-service failures**
* **Reward shaping for reasoning quality**

👉 This tests **causal reasoning**, not pattern matching.

---

# 🏗️ Environment Design

## System Architecture

```text
Client → LB → API → Auth → App → DB ↔ Cache → Queue → Consumers
```

Failures propagate across layers.

---

## 🔄 Interaction Loop

```text
reset → observe → act → reward → repeat
```

Observation includes:

* Logs (misleading)
* Metrics (reliable)
* Errors (surface-level)

---

## 🤖 Action Space

### Investigation

`check_api, check_auth, check_db, check_cache, check_queue, check_lb`

### Fixes

* Auth → `fix_invalid_token, restart_auth`
* DB → `optimize_query, restart_db`
* Cache → `clear_cache, scale_cache`
* Queue → `scale_consumers`
* LB → `fix_routing`

---

# 🧩 Task Registry (19 Scenarios)

### Auth

auth_token_expired · invalid_token · auth_service_down · rate_limit_auth

### Database

slow_query · connection_pool_exhausted · database_down · disk_full

### Cache

stale_cache_issue · cache_miss_issue · cache_down

### Queue

queue_backlog · consumer_down · message_loss

### Load Balancer

uneven_routing · lb_down

### Multi-Service

auth_db_combined_issue · cache_queue_dependency · full_system_failure

---

# 🎯 Reward Design (Judging Criteria Focus)

| Behavior                | Reward     |
| ----------------------- | ---------- |
| Useful investigation    | +3         |
| Correct fix             | +20 to +30 |
| Repeated / wrong action | -2 to -5   |
| Faster resolution       | bonus      |

### Key Properties

* Dense signal (not just final reward)
* Encourages reasoning steps
* Penalizes shortcut exploitation
* Hard to game

Failures propagate across layers.

---

# 🧠 Training Pipeline (End-to-End)

* Environment → OpenEnv API
* Rollouts generated dynamically
* Dataset built from trajectories
* GRPO training using TRL

---

# 📊 Evidence of Learning (CRITICAL)

## Performance Improvement

| Metric           | Before | After   |
| ---------------- | ------ | ------- |
| Avg Reward       | -15    | +30     |
| Success Rate     | Low    | High    |
| Repeated Actions | High   | Minimal |
| Steps to Solve   | High   | Reduced |

---

## 📈 Reward Curve

![Reward Curve](./assets/reward_curve.png)

---

## 📉 Loss Curve

![Loss Curve](./assets/loss_curve.png)

---

# 🔍 Example: Real Learning

### Scenario: `cache_miss_issue`

**Observation:**

* Logs → “Cache working”
* Metrics → High DB load

---

### ❌ Before Training

```text
check_api → check_api → check_api
```

Fails (no reasoning)

---

### ✅ After Training

```text
check_cache → identify miss → scale_cache
```

✔ Correct root cause
✔ Minimal steps
✔ High reward

---

# 🏆 Why This Stands Out (Innovation - 40%)

* Realistic distributed system simulation
* Cross-service dependency reasoning
* Misleading signals (logs vs metrics)
* Multi-step decision making
* Not a toy environment

---

# 🎤 Story (Presentation - 30%)

> “We trained an agent to debug systems like an SRE — not by memorizing patterns, but by reasoning across services and identifying root causes.”

---

# 📊 Training Proof (20%)

* Reward curve shows improvement
* Behavior change demonstrated
* Before vs after comparison included

---

# ⚙️ Reward + Pipeline (10%)

* Dense, structured reward
* Environment-driven feedback
* Real interaction loop (not static data)

---

# 🚀 How to Run

```bash
pip install fastapi uvicorn openenv requests
```

```bash
uv run python -m server.app
```

```bash
openenv validate --url http://localhost:7860
```

---

# 🐳 Docker

```bash
docker build -t debug-env .
```

---

# 🧩 Tech Stack

* FastAPI
* OpenEnv
* Hugging Face Spaces
* TRL (GRPO)
* Docker

---

# 🧠 Key Insight

> Debugging is a **causal reasoning problem under uncertainty**, not a classification task.

---

# 🚀 Real-World Impact

* Autonomous SRE agents
* Incident response automation
* Self-healing systems

---

# 👩‍💻 Author

**Manasa Udathu**
Software Engineer | Distributed Systems | RL Systems


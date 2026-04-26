# 🛠️ DebugRL: A Structured System Debugging Agent

## 🚀 Overview

This project builds an intelligent debugging agent that identifies and fixes issues in a distributed system consisting of:

* Load Balancer
* API
* Authentication
* Database
* Cache
* Queue

The agent follows a structured reasoning process inspired by real-world debugging workflows.

Debugging is not about applying fixes — it is about understanding how failures propagate through a system.

In real-world distributed systems:

Errors appear in one service
But originate in another
And propagate across dependencies

👉 DebugRL trains agents to:

Investigate before acting
Use logs and metrics together
Identify root cause across services, not just symptoms

---

# 🧠 Core Idea

Instead of blindly applying fixes, the agent follows **three clear phases**:

## Phase 1: IDENTIFY

* Understand the problem using initial hints
* Decide which services might be involved

## Phase 2: INVESTIGATE

* Use `check_*` actions to gather evidence
* Analyze logs and metrics
* Avoid guessing

## Phase 3: FIX

* Match observed symptoms to known issues
* Apply the correct fix action

--- 

## 🌐 Links

* 🔗 Hugging Face Space: **https://huggingface.co/spaces/Udathu/debug-env**
* 📓 Training Notebook (Colab): **https://github.com/UdathuManasa/debug-env/tree/main/trainedmodel**
* 🎥 Demo / Blog: **https://youtu.be/0YBkrNQqh0c**

---

# 🏗️ System Architecture

```text
Client → Load Balancer → API → Auth → Database → Cache → Queue → Consumers
```

### Key Observations:

* Failures propagate downstream
* Symptoms often appear upstream
* Root cause is usually NOT the API

---

## 🔍 Service-Level Debugging

Each service exposes:

* **Logs** → surface-level symptoms
* **Metrics** → deeper system signals

The agent must combine both to act correctly.

---

### 🌐 API Layer

* **Role**: Entry point for requests

* **Issues**:

  * High error rate
  * Increased latency

* **Logs**:

  * “500 Internal Server Error”
  * “Service unavailable”

* **Metrics**:

  * Error spikes
  * Latency increase

* **Action Strategy**:

  * Rarely the root cause
  * Investigate downstream (Auth, DB, Cache)

---

### 🔐 Authentication (Auth)

* **Issues**:

  * Token expired / invalid
  * Rate limiting
  * Service downtime

* **Logs**:

  * “Invalid token”
  * “Authentication failed”

* **Metrics**:

  * Failed auth requests
  * Latency spikes

* **Actions**:

  * `refresh_tokens`
  * `fix_invalid_token`
  * `restart_auth`

---

### 🗄️ Database (DB)

* **Issues**:

  * Slow queries
  * Connection pool exhaustion
  * Disk full / downtime

* **Logs**:

  * “DB timeout”
  * “Connection limit reached”

* **Metrics**:

  * High query latency
  * Low throughput

* **Actions**:

  * `optimize_query`
  * `increase_pool`
  * `restart_db`

---

### ⚡ Cache

* **Issues**:

  * Cache miss
  * Stale data
  * Service failure

* **Logs**:

  * “Cache miss”
  * “Stale entry detected”

* **Metrics**:

  * Low hit rate
  * Increased DB load

* **Actions**:

  * `clear_cache`
  * `scale_cache`

---

### 📬 Queue

* **Issues**:

  * Backlog growth
  * Consumer failure

* **Logs**:

  * “Queue backlog increasing”
  * “Consumer not responding”

* **Metrics**:

  * High queue depth
  * Low processing rate

* **Actions**:

  * `scale_consumers`
  * `restart_consumer`

---

### 🌐 Load Balancer (LB)

* **Issues**:

  * Uneven routing
  * High latency

* **Logs**:

  * “Routing imbalance detected”

* **Metrics**:

  * Uneven traffic distribution
  * Response delays

* **Actions**:

  * `fix_routing`
  * `restart_lb`

---

## 🔥 Multi-Level Root Cause Reasoning (Key Differentiator)

In DebugRL, the **visible failure is often misleading**.

### Example 1

* API error observed
* Logs → Auth failure
* Metrics → DB latency high

👉 Root Cause: **Database issue**, not Auth

---

### Example 2

* High API latency
* Logs → Cache working
* Metrics → Low cache hit rate + high DB load

👉 Root Cause: **Cache inefficiency causing DB overload**

---

### Example 3

* Queue backlog increasing
* Logs → Consumer failure
* Metrics → CPU spike

👉 Root Cause: **Resource bottleneck**

---

## 🧠 Key Insight

> The system teaches agents to trace failures **across services**, not fix them locally.

This enables:

* Causal reasoning
* Dependency-aware debugging
* Real-world system understanding

---

## 🎯 What Makes This Strong

* Combines logs (symptoms) + metrics (truth)
* Requires cross-service reasoning
* Encourages investigation before action
* Captures real-world debugging behavior


# 🧭 Decision Logic

The agent follows strict rules:

1. Never repeat actions
2. Always investigate before fixing
3. Check all relevant services
4. Map symptoms to correct fixes

---

## Decision Flow

### If no logs available:

→ Phase 1 (Identify)
→ Perform `check_<service>`

### If partial logs:

→ Phase 2 (Investigate)
→ Continue checking relevant services

### If clear error pattern:

→ Phase 3 (Fix)
→ Apply correct fix action

---

# ⚡ Implementation

## Environment (`env.py`)

Simulates:

* Errors
* Logs
* Metrics
* Rewards

---

## Inference (`inference.py`)

* Builds structured prompt
* Uses LLM to decide next action
* Returns only action (no explanation)

---

## UI (`app.py`)

* Interactive debugging interface
* Displays:

  * Error
  * Logs
  * Metrics
  * Actions taken
  * Reward

---

# 🏆 Reward Design

The environment provides feedback to guide the agent toward correct debugging behavior.

## Reward Strategy

* ✅ +1 for correct fix
* ❌ -1 for incorrect action
* ⚠️ Small penalty for unnecessary checks
* 🚫 Penalty for repeating actions

## Key Idea

The reward encourages:

* Efficient investigation
* Correct root cause identification
* Minimal unnecessary actions

This ensures the agent learns to debug systematically rather than randomly.

---


# 🚧 Challenges Faced

* Slow inference causing UI timeouts
* Websocket failures in Gradio
* GRPO training latency

---

# ✅ Solutions

* Simplified inference pipeline
* Reduced prompt size
* Used lightweight models
* Separated training and UI

---

# 📊 Results

* Agent can diagnose system issues step-by-step
* Structured reasoning improves accuracy
* Stable interactive debugging interface

---

# 🔮 Future Work

* Multi-agent collaboration
* GRPO-based policy optimization
* Faster inference using optimized models
* Automated debugging without manual actions

---

# 📌 Conclusion

This project demonstrates how structured reasoning + LLMs can simulate real-world debugging workflows.

By enforcing:

* phased reasoning
* evidence-based decisions
* action constraints

we move closer to reliable autonomous system debugging.

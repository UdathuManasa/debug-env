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

# 🏗️ System Architecture

```text
Client → Load Balancer → API → Auth → Database → Cache → Queue → Consumers
```

### Key Observations:

* Failures propagate downstream
* Symptoms often appear upstream
* Root cause is usually NOT the API

---

# 🔍 Services & Failure Patterns

### Authentication

* Token expiry
* Invalid tokens
* Rate limits

### Database

* Slow queries
* Connection pool exhaustion
* Disk full

### Cache

* Low hit rate
* Stale data

### Queue

* Backlog
* Consumer failure

### Load Balancer

* Uneven routing
* High latency

---

# ⚙️ Action Space

## Investigation Actions

* `check_auth`
* `check_db`
* `check_cache`
* `check_queue`
* `check_lb`
* `check_api`

## Fix Actions

### Auth

* `refresh_tokens`
* `fix_invalid_token`
* `restart_auth`
* `increase_rate_limit`

### Database

* `optimize_query`
* `increase_pool`
* `restart_db`
* `cleanup_disk`

### Cache

* `clear_cache`
* `scale_cache`
* `restart_cache`

### Queue

* `scale_consumers`
* `restart_consumer`
* `fix_ack_logic`

### Load Balancer

* `fix_routing`
* `restart_lb`

---

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

# 🧪 Example Scenarios

### Example 1

**Hint:** Authentication issue
**Action:** `check_auth`

---

### Example 2

**Logs:** Token expired
**Action:** `refresh_tokens`

---

### Example 3

**Logs:** DB connection timeout
**Action:** `increase_pool`

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

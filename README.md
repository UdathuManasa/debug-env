---
title: Debug Env
emoji: 🔧
colorFrom: indigo
colorTo: blue
sdk: docker
pinned: false
app_port: 7860
---

Gemini said
Since you've already cleared Phase 2, the README is your chance to show the judges that your 11 tasks aren't just random—they are a deliberate "Stress Test" for AI agents.

Copy and paste this structured section into your README.md on GitHub. It uses professional engineering terminology (perfect for a ServiceNow/Juspay background) to highlight your Low-Level Design (LLD).

🛠️ The "Debug-Env" Task Registry (11 Scenarios)
This environment features a Registry-based Grader System designed to evaluate an LLM's ability to reason through complex, non-linear debugging scenarios. Unlike basic "error-match" tasks, these 11 scenarios include Agentic Traps and Multi-step Dependencies.

🏗️ Infrastructure & Performance
api_latency: Tests if the agent can identify bottlenecked middleware vs. downstream service delays.

db_performance: Requires the agent to differentiate between missing indexes and high connection overhead.

database_down: A baseline connectivity test involving connection string validation and service health.

load_balancer_issue: A routing complexity task where traffic is unevenly distributed across healthy nodes.

🔐 Security & Compliance
auth_failure: Evaluates the agent's ability to debug expired tokens vs. misconfigured IAM roles.

security_breach: A high-stakes scenario where the agent must identify unauthorized script execution hidden behind "High CPU" metrics.

rate_limit_issue: Tests if the agent can identify a 429 error and suggest traffic-shaping solutions.

🧠 Agentic Reasoning & "Observation Traps"
misleading_logs: (The Hardest Task) The logs report "Success 200," but the metrics show a 0% completion rate. Tests if the agent trusts raw data over string logs.

retry_trap_issue: A logic loop where a service keeps retrying a "Permanent Failure." The agent must break the loop rather than just "restarting."

multi_root_issue: A cascading failure where fixing the first error (e.g., Memory) reveals a second hidden error (e.g., Disk I/O).

misleading_cache_issue: Tests if the agent can identify stale data even when the origin server is returning "Fresh" headers.

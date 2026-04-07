

class Task:

    def __init__(self, name, observation, valid_actions, flow, solution, reward_config, step_weights):
        self.name = name
        self.observation = observation
        self.valid_actions = valid_actions
        self.flow = flow
        self.solution = solution
        self.reward_config = reward_config
        self.step_weights = step_weights

        self.step_index = 0
        self.done = False
        self.actions_taken = []
        self.rewards = []
        self.total_reward = 0

        self.related_actions = set(flow)

    def get_expected_action(self):
        if self.step_index < len(self.flow):
            return self.flow[self.step_index]
        return None

    def is_done(self):
        return self.done

    def apply_action(self, action):

        cfg = self.reward_config
        self.actions_taken.append(action)

        if action not in self.valid_actions:
            reward = cfg["invalid_action"]

        else:
            expected = self.get_expected_action()

            if action == expected:
                base = self.step_weights.get(action, cfg["default_weight"])
                reward = base + (self.step_index * cfg["progress_bonus"])
                self.step_index += 1

            elif action in self.flow:
                distance = abs(self.flow.index(action) - self.step_index)
                reward = max(cfg["min_partial"], cfg["partial_base"] - distance)

            elif action in self.related_actions:
                reward = cfg["related_wrong"]

            else:
                reward = cfg["irrelevant"]

        if self.actions_taken.count(action) > 1:
            reward += cfg["repeat_penalty"]

        if action == self.solution:
            if self.step_index >= len(self.flow) - 1:
                reward += cfg["final_bonus"]
                self.done = True
            else:
                reward += cfg["premature_penalty"]

        self.rewards.append(reward)
        self.total_reward += reward

        return reward


class TaskManager:
    _current_task_index = 0

    @classmethod
    def get_random_task(cls):

        base_config = {
            "default_weight": 3,
            "progress_bonus": 0.5,
            "partial_base": 2,
            "min_partial": 1,
            "related_wrong": -1,
            "irrelevant": -4,
            "invalid_action": -5,
            "final_bonus": 10,
            "premature_penalty": -6,
            "repeat_penalty": -2
        }

        tasks = [

            Task(
                name="api_latency",
                observation={
                    "error": "API timeout",
                    "logs": "High latency, DB slow",
                    "metrics": {"latency": 1500}
                },
                valid_actions=[
                    "check_logs", "check_db", "increase_timeout"
                ],
                flow=[
                    "check_logs", "check_db", "increase_timeout"
                ],
                solution="increase_timeout",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 4,
                    "increase_timeout": 6
                }
            ),

            Task(
                name="db_performance",
                observation={
                    "error": "Slow query",
                    "logs": "Full table scan",
                    "metrics": {"cpu": 90}
                },
                valid_actions=[
                    "check_logs", "check_db", "optimize_query"
                ],
                flow=[
                    "check_logs", "check_db", "optimize_query"
                ],
                solution="optimize_query",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 5,
                    "optimize_query": 7
                }
            ),

            Task(
                name="misleading_logs",
                observation={
                    "error": "Crash",
                    "logs": "Memory high but DB failed",
                    "metrics": {"memory": 90}
                },
                valid_actions=[
                    "check_logs", "check_memory", "check_db", "fix_db"
                ],
                flow=[
                    "check_logs", "check_db", "fix_db"
                ],
                solution="fix_db",
                reward_config={
                    **base_config,
                    "irrelevant": -5
                },
                step_weights={
                    "check_logs": 3,
                    "check_db": 5,
                    "fix_db": 8
                }
            ),

            Task(
                name="multi_root_issue",
                observation={
                    "error": "API latency high",
                    "logs": "DB slow, memory spikes observed",
                    "metrics": {"latency": 2000, "memory": 85}
                },
                valid_actions=[
                    "check_logs", "check_db", "check_memory",
                    "optimize_db", "optimize_memory"
                ],
                flow=[
                    "check_logs",
                    "check_db",
                    "check_memory",
                    "optimize_db",
                    "optimize_memory"
                ],
                solution="optimize_memory",  # last step completes
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 4,
                    "check_memory": 4,
                    "optimize_db": 6,
                    "optimize_memory": 7
                }
            ),

            Task(
                name="retry_trap_issue",
                observation={
                    "error": "Service unavailable",
                    "logs": "Retry attempts failed",
                    "metrics": {"failures": 5}
                },
                valid_actions=[
                    "retry_request", "check_logs",
                    "check_service", "restart_service"
                ],
                flow=[
                    "check_logs",
                    "check_service",
                    "restart_service"
                ],
                solution="restart_service",
                reward_config={
                    **base_config,
                    "repeat_penalty": -2  # stronger loop punishment
                },
                step_weights={
                    "check_logs": 3,
                    "check_service": 5,
                    "restart_service": 7,
                    "retry_request": 1  # low value action
                }
            ),
            Task(
                name="misleading_cache_issue",
                observation={
                    "error": "High latency",
                    "logs": "DB timeout errors",  # misleading
                    "metrics": {"latency": 1200, "cache_hit": 10}
                },
                valid_actions=[
                    "check_logs", "check_db", "check_cache",
                    "optimize_db", "fix_cache"
                ],
                flow=[
                    "check_logs",
                    "check_cache",
                    "fix_cache"
                ],
                solution="fix_cache",
                reward_config={
                    **base_config,
                    "irrelevant": -5  # stronger penalty
                },
                step_weights={
                    "check_logs": 3,
                    "check_cache": 5,
                    "fix_cache": 8
                }
            ),

            Task(
                name="auth_failure",
                observation={
                    "error": "401 Unauthorized",
                    "logs": "Token validation failed",
                    "metrics": {"auth_fail_rate": 70}
                },
                valid_actions=[
                    "check_logs", "check_auth_service",
                    "validate_token", "fix_auth"
                ],
                flow=[
                    "check_logs",
                    "check_auth_service",
                    "validate_token",
                    "fix_auth"
                ],
                solution="fix_auth",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_auth_service": 5,
                    "validate_token": 6,
                    "fix_auth": 8
                }
            ),

            Task(
                name="load_balancer_issue",
                observation={
                    "error": "Inconsistent responses",
                    "logs": "Requests routed unevenly",
                    "metrics": {"server_load_diff": 80}
                },
                valid_actions=[
                    "check_logs", "check_routing",
                    "check_lb", "fix_lb"
                ],
                flow=[
                    "check_logs",
                    "check_routing",
                    "check_lb",
                    "fix_lb"
                ],
                solution="fix_lb",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_routing": 5,
                    "check_lb": 6,
                    "fix_lb": 8
                }
            ),

            Task(
                name="database_down",
                observation={
                    "error": "DB connection failed",
                    "logs": "Connection refused",
                    "metrics": {"db_status": 0}
                },
                valid_actions=[
                    "check_logs", "check_db", "restart_db"
                ],
                flow=[
                    "check_logs",
                    "check_db",
                    "restart_db"
                ],
                solution="restart_db",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 6,
                    "restart_db": 9
                }
            ),

            Task(
                name="rate_limit_issue",
                observation={
                    "error": "429 Too Many Requests",
                    "logs": "Rate limit exceeded",
                    "metrics": {"drop_rate": 40}
                },
                valid_actions=[
                    "check_logs", "check_rate_limit", "increase_limit"
                ],
                flow=[
                    "check_logs",
                    "check_rate_limit",
                    "increase_limit"
                ],
                solution="increase_limit",
                reward_config=base_config,
                step_weights={
                    "check_logs": 3,
                    "check_rate_limit": 5,
                    "increase_limit": 7
                }
            ),

            Task(
                name="security_breach",
                observation={
                    "error": "Suspicious activity",
                    "logs": "Multiple failed logins",
                    "metrics": {"ip_requests": 1000}
                },
                valid_actions=[
                    "check_logs", "analyze_traffic", "block_ip"
                ],
                flow=[
                    "check_logs",
                    "analyze_traffic",
                    "block_ip"
                ],
                solution="block_ip",
                reward_config={
                    **base_config,
                    "irrelevant": -6  # stricter penalty
                },
                step_weights={
                    "check_logs": 3,
                    "analyze_traffic": 6,
                    "block_ip": 9
                }
            ),
        ]

        selected_task = tasks[cls._current_task_index]
        
        cls._current_task_index = (cls._current_task_index + 1) % len(tasks)
        
        return selected_task
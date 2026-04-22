

class Task:

    def __init__(self, name, observation, valid_actions, flow, solution, reward_config, step_weights,required_signals,optional_signals):
        self.name = name
        self.full_observation = observation
        self.observation = {
            "error": observation["error"],
            "logs": "",
            "metrics": {}
        }
        self.valid_actions = valid_actions
        self.flow = flow
        self.solution = solution
        self.reward_config = reward_config
        self.step_weights = step_weights

        self.done = False
        self.actions_taken = []
        self.rewards = []
        self.total_reward = 0

        self.required_signals = {action: 0 for action in required_signals}
        self.optional_signals = {action: 0 for action in optional_signals}


    def is_done(self):
        return self.done
    def reset_state(self):
        self.done = False
        self.actions_taken = []
        self.rewards = []
        self.total_reward = 0

        self.observation = {
            "error": self.full_observation["error"],
            "logs": "",
            "metrics": {}
        }
        self.required_signals = {k: 0 for k in self.required_signals}
        self.optional_signals = {k: 0 for k in self.optional_signals}

    def update_observation_for_tools(self, action):

        if action == "check_logs" and self.observation["logs"]=="":
            self.observation["logs"] = self.full_observation["logs"]

        if action == "check_metrics" and self.observation["metrics"]=={}:
            self.observation["metrics"] = self.full_observation["metrics"]

    def apply_action(self, action):
        if action in ["check_logs", "check_metrics"]:
            self.update_observation_for_tools(action)

        cfg = self.reward_config
        reward = 0
        self.actions_taken.append(action)

        if action not in self.valid_actions:
            reward += cfg["invalid_action"]

        elif action == self.solution:
            base = self.step_weights.get(action, 0)
            reward += base

            required_done = sum(self.required_signals.values())
            total_required = len(self.required_signals)

            optional_done = sum(self.optional_signals.values())

            if required_done == 0:
                reward += cfg["no_investigation_penalty"]

            elif required_done < total_required:
                reward += cfg["partial_investigation_reward"]

            else:
                reward += cfg["final_bonus"]

                if optional_done > 0:
                    reward += cfg["optional_bonus"]

            self.done = True

        else:
            # first time → reward
            if self.actions_taken.count(action) == 1:
                reward += self.step_weights.get(action, 0)
            else:
                reward += cfg["repeat_penalty"]

        if action in self.required_signals:
            self.required_signals[action] = 1

        if action in self.optional_signals:
            self.optional_signals[action] = 1

        self.rewards.append(reward)
        self.total_reward += reward

        return reward


class TaskManager:
    _tasks = None
    _current_task_index = 0
    _base_config = {
            "default_weight": 3,
            "progress_bonus": 0.5,
            "partial_base": 2,
            "min_partial": 1,
            "related_wrong": -1,
            "irrelevant": -4,
            "invalid_action": -5,
            "final_bonus": 10,
            "premature_penalty": -6,
            "repeat_penalty": -2,
            "partial_investigation_reward": 3,
            "no_investigation_penalty": -8,
            "optional_bonus": 3,
        }

    @classmethod
    def _init_tasks(cls):
        if cls._tasks is None:
            cls._tasks = [

            Task(
                name="api_latency",
                observation={
                    "error": "API timeout",
                    "logs": "High latency, DB slow",
                    "metrics": {"latency": 1500}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_db", "increase_timeout"
                ],
                flow=[
                    "check_logs","check_metrics", "check_db", "increase_timeout"
                ],
                solution="increase_timeout",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 4,
                    "increase_timeout": 6,
                    "check_metrics": 5
                },
                required_signals = ["check_logs", "check_metrics"],
                optional_signals = ["check_db"]
            ),

            Task(
                name="db_performance",
                observation={
                    "error": "Slow query",
                    "logs": "Full table scan",
                    "metrics": {"cpu": 90}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_db", "optimize_query"
                ],
                flow=[
                    "check_logs","check_metrics", "check_db", "optimize_query"
                ],
                solution="optimize_query",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 3,
                    "check_db": 5,
                    "optimize_query": 7,
                    "check_metrics": 4
                },
                required_signals = ["check_db", "check_metrics"],
                optional_signals = ["check_logs"]
            ),

            Task(
                name="misleading_logs",
                observation={
                    "error": "Crash",
                    "logs": "Memory high but DB failed",
                    "metrics": {"memory": 90}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_memory", "check_db", "fix_db"
                ],
                flow=[
                    "check_logs","check_metrics", "check_db", "fix_db"
                ],
                solution="fix_db",
                reward_config={
                    **cls._base_config,
                    "irrelevant": -5
                },
                step_weights={
                    "check_logs": 2,
                    "check_db": 5,
                    "fix_db": 8,
                    "check_metrics": 6
                },
                required_signals = ["check_logs", "check_db"],
                optional_signals = ["check_metrics", "check_memory"]
            ),

            Task(
                name="multi_root_issue",
                observation={
                    "error": "API latency high",
                    "logs": "DB slow, memory spikes observed",
                    "metrics": {"latency": 2000, "memory": 85}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_db", "check_memory",
                    "optimize_db", "optimize_memory"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_db",
                    "check_memory",
                    "optimize_db",
                    "optimize_memory"
                ],
                solution="optimize_memory",  # last step completes
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 4,
                    "check_db": 4,
                    "check_memory": 4,
                    "optimize_db": 6,
                    "optimize_memory": 7,
                    "check_metrics": 5
                },
                required_signals = ["check_logs", "check_metrics"],
                optional_signals = ["check_db", "check_memory"]
            ),

            Task(
                name="retry_trap_issue",
                observation={
                    "error": "Service unavailable",
                    "logs": "Retry attempts failed",
                    "metrics": {"failures": 5}
                },
                valid_actions=[
                    "retry_request", "check_logs", "check_metrics",
                    "check_service", "restart_service"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_service",
                    "restart_service"
                ],
                solution="restart_service",
                reward_config={
                    **cls._base_config,
                    "repeat_penalty": -2  # stronger loop punishment
                },
                step_weights={
                    "check_logs": 3,
                    "check_service": 5,
                    "restart_service": 7,
                    "check_metrics": 3,
                    "retry_request": 1  # low value action
                },
                required_signals = ["check_logs", "check_service"],
                optional_signals = ["check_metrics"]
            ),
            Task(
                name="misleading_cache_issue",
                observation={
                    "error": "High latency",
                    "logs": "DB timeout errors",  # misleading
                    "metrics": {"latency": 1200, "cache_hit": 10}
                },
                valid_actions=[
                    "check_logs", "check_metrics","check_db", "check_cache",
                    "optimize_db", "fix_cache"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_cache",
                    "fix_cache"
                ],
                solution="fix_cache",
                reward_config={
                    **cls._base_config,
                    "irrelevant": -5  # stronger penalty
                },
                step_weights={
                    "check_logs": 2,
                    "check_cache": 5,
                    "fix_cache": 8,
                    "check_metrics": 5
                },
                required_signals = ["check_logs", "check_cache"],
                optional_signals = ["check_metrics", "check_db"]
            ),

            Task(
                name="auth_failure",
                observation={
                    "error": "401 Unauthorized",
                    "logs": "Token validation failed",
                    "metrics": {"auth_fail_rate": 70}
                },
                valid_actions=[
                    "check_logs", "check_metrics","check_auth_service",
                    "validate_token", "fix_auth"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_auth_service",
                    "validate_token",
                    "fix_auth"
                ],
                solution="fix_auth",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 4,
                    "check_auth_service": 5,
                    "validate_token": 6,
                    "fix_auth": 8,
                    "check_metrics": 4
                },
                required_signals = ["check_logs", "check_auth_service"],
                optional_signals = ["check_metrics", "validate_token"]
            ),

            Task(
                name="load_balancer_issue",
                observation={
                    "error": "Inconsistent responses",
                    "logs": "Requests routed unevenly",
                    "metrics": {"server_load_diff": 80}
                },
                valid_actions=[
                    "check_logs", "check_metrics","check_routing",
                    "check_lb", "fix_lb"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_routing",
                    "check_lb",
                    "fix_lb"
                ],
                solution="fix_lb",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 3,
                    "check_routing": 5,
                    "check_lb": 6,
                    "fix_lb": 8,
                    "check_metrics": 5
                },
                required_signals = ["check_logs", "check_routing"],
                optional_signals = ["check_metrics", "check_lb"]
            ),

            Task(
                name="database_down",
                observation={
                    "error": "DB connection failed",
                    "logs": "Connection refused",
                    "metrics": {"db_status": 0}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_db", "restart_db"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_db",
                    "restart_db"
                ],
                solution="restart_db",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 4,
                    "check_db": 6,
                    "restart_db": 9,
                    "check_metrics": 6
                },
                required_signals = ["check_logs", "check_db"],
                optional_signals = ["check_metrics"]
            ),

            Task(
                name="rate_limit_issue",
                observation={
                    "error": "429 Too Many Requests",
                    "logs": "Rate limit exceeded",
                    "metrics": {"drop_rate": 40}
                },
                valid_actions=[
                    "check_logs","check_metrics", "check_rate_limit", "increase_limit"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "check_rate_limit",
                    "increase_limit"
                ],
                solution="increase_limit",
                reward_config=cls._base_config,
                step_weights={
                    "check_logs": 4,
                    "check_rate_limit": 5,
                    "increase_limit": 7,
                    "check_metrics": 4
                },
                required_signals = ["check_logs", "check_rate_limit"],
                optional_signals = ["check_metrics"]
            ),

            Task(
                name="security_breach",
                observation={
                    "error": "Suspicious activity",
                    "logs": "Multiple failed logins",
                    "metrics": {"ip_requests": 1000}
                },
                valid_actions=[
                    "check_logs","check_metrics", "analyze_traffic", "block_ip"
                ],
                flow=[
                    "check_logs",
                    "check_metrics",
                    "analyze_traffic",
                    "block_ip"
                ],
                solution="block_ip",
                reward_config={
                    **cls._base_config,
                    "irrelevant": -6  # stricter penalty
                },
                step_weights={
                    "check_logs": 3,
                    "analyze_traffic": 6,
                    "block_ip": 9,
                    "check_metrics": 5
                },
                required_signals = ["check_logs", "analyze_traffic"],
                optional_signals = ["check_metrics"]
            ),
        ]

    @classmethod
    def get_all_task_names(cls):
        cls._init_tasks()
        return [task.name for task in cls._tasks]

    @classmethod
    def get_task_by_name(cls, name):
        cls._init_tasks()
        for task in cls._tasks:
            if task.name == name:
                return task
        raise ValueError(f"Task {name} not found")

    @classmethod
    def get_random_task(cls):
        cls._init_tasks()
        task = cls._tasks[cls._current_task_index]
        cls._current_task_index = (cls._current_task_index + 1) % len(cls._tasks)
        return task
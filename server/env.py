from server.task import Task
from server.models import Observation, StepResult, State, GradeResponse
from server.taskmanager import TaskManager
from server.db_service import DatabaseService
from server.auth_service import AuthService
from server.cache_service import CacheService
from server.queue_service import QueueService
from server.ld_service import LoadBalancerService
from server.api_service import APIService
from server.appserver_service import AppServerService


class DebugEnv:
    """
    Debugging environment that simulates a microservice system.
    
    Services can have issues injected, and agents must:
    1. Investigate to understand the problem
    2. Apply the correct fix
    """
    
    def __init__(self):
        self._init_services()
        self._init_rewards()
        self._init_action_map()
        self.task = None
        self.done = False
        self.total_reward = 0
        self.actions_taken = []
        self.hidden_state = {}
        self.required_signals = {}
        self.optional_signals = {}

    def _init_services(self):
        """Initialize all microservices."""
        self.db = DatabaseService()
        self.auth = AuthService()
        self.cache = CacheService()
        self.queue = QueueService()
        self.lb = LoadBalancerService()
        self.api = APIService(self.db, self.auth)
        self.app = AppServerService()

    def _init_rewards(self):
        """Configure reward structure."""
        self.cfg = {
            "invalid_action": -5,
            "repeat_penalty": -2,
            "final_bonus": 10,
            "partial_investigation": 3,
            "no_investigation": -8,
            "optional_bonus": 2
        }

    def _init_action_map(self):
        """
        Map action names to (service, method_name) tuples.
        This allows dynamic routing of actions to service methods.
        """
        self.action_map = {
            # Investigation actions
            "check_db": (self.db, "check_db"),
            "check_auth": (self.auth, "check_auth_service"),
            "check_cache": (self.cache, "check_cache"),
            "check_queue": (self.queue, "check_queue"),
            "check_lb": (self.lb, "check_lb"),
            "check_api": (self.api, "check_api"),
            "check_app": (self.app, "check_app"),
            
            # Database fixes
            "optimize_query": (self.db, "optimize_query"),
            "increase_pool": (self.db, "increase_pool"),
            "restart_db": (self.db, "restart_db"),
            "cleanup_disk": (self.db, "cleanup_disk"),
            
            # Auth fixes
            "restart_auth": (self.auth, "restart_auth"),
            "refresh_tokens": (self.auth, "refresh_tokens"),
            "fix_invalid_token": (self.auth, "fix_invalid_token"),
            "increase_rate_limit": (self.auth, "increase_rate_limit"),
            
            # Cache fixes
            "clear_cache": (self.cache, "clear_cache"),
            "scale_cache": (self.cache, "scale_cache"),
            "restart_cache": (self.cache, "restart_cache"),
            
            # Queue fixes
            "scale_consumers": (self.queue, "scale_consumers"),
            "restart_consumer": (self.queue, "restart_consumer"),
            "fix_ack_logic": (self.queue, "fix_ack_logic"),
            "restart_queue": (self.queue, "restart_queue"),
            
            # Load balancer fixes
            "fix_routing": (self.lb, "fix_routing"),
            "restart_lb": (self.lb, "restart_lb"),
            
            # API actions (usually ineffective)
            "restart_api": (self.api, "restart_api"),
            "scale_api": (self.api, "scale_api"),

            # App Server
            "restart_app": (self.app, "restart_app"),
            "fix_memory": (self.app, "fix_memory"),
            "scale_app": (self.app, "scale_app"),
        }

    # ==================== RESET ====================
    def reset(self, task_name=None):
        """
        Reset the environment for a new task.
        
        Args:
            task_name: Optional specific task name. If None, picks random task.
            
        Returns:
            StepResult with initial observation
        """
        # Get task
        if task_name:
            self.task = TaskManager.get_task_by_name(task_name)
        else:
            self.task = TaskManager.get_random_task()
        
        # Reset environment state
        self.done = False
        self.total_reward = 0
        self.actions_taken = []
        self.hidden_state = {}
        
        # Initialize signal tracking
        self.required_signals = {sig: False for sig in self.task.required_signals}
        self.optional_signals = {sig: False for sig in self.task.optional_signals}
        
        # Reset all services to healthy state
        for service in [self.db, self.auth, self.cache, self.queue, self.lb, self.app]:
            service.reset()
        self.api.reset()
        
        # Inject issues according to task definition
        for service_name, issue_type in self.task.issues.items():
            service = getattr(self, service_name)
            service.inject_issue(issue_type)
        
        # API needs to reflect downstream issues
        self.api.inject_issue()
        
        # Build initial observation (only shows API-level error)
        initial_obs = self._build_observation()
        
        return StepResult(
            observation=Observation(**initial_obs),
            reward=0.0,
            done=False,
            info={}
        )

    # ==================== STEP ====================
    def step(self, action: str):
        """
        Execute an action in the environment.
        
        Args:
            action: Action name (e.g., "check_db", "optimize_query")
            
        Returns:
            StepResult with observation, reward, done flag, and info
        """
        if self.done:
            # Task already completed
            return StepResult(
                observation=Observation(**self._build_observation()),
                reward=0.0,
                done=True,
                info={"message": "Task already completed"}
            )
        
        reward = 0
        
        # Check if action is valid
        if action not in self.action_map:
            self.actions_taken.append(action)
            reward = self.cfg["invalid_action"]
            
            return StepResult(
                observation=Observation(**self._build_observation()),
                reward=float(reward),
                done=False,
                info={"message": f"Invalid action: {action}"}
            )
        
        # Penalize repeated actions
        if action in self.actions_taken:
            reward += self.cfg["repeat_penalty"]
        
        self.actions_taken.append(action)
        
        # Route action to appropriate service method
        service, method_name = self.action_map[action]
        method = getattr(service, method_name)
        result = method()
        
        # -------- INVESTIGATION ACTIONS --------
        if action.startswith("check_"):
            # Result is (observation_dict, reward)
            obs_data, action_reward = result
            reward += action_reward
            
            # Store in hidden state for observation building
            service_name = action.replace("check_", "")
            self.hidden_state[service_name] = obs_data
            
            # Track investigation signals
            if action in self.required_signals:
                self.required_signals[action] = True
            if action in self.optional_signals:
                self.optional_signals[action] = True
        
        # -------- FIX ACTIONS --------
        else:
            # Result is (reward, resolved)
            action_reward, resolved = result
            reward += action_reward
            
            # Check if this is the solution
            if action == self.task.solution and resolved:
                # Task solved! Add investigation bonus
                reward += self._calculate_investigation_bonus()
                self.done = True
        
        self.total_reward += reward
        
        return StepResult(
            observation=Observation(**self._build_observation()),
            reward=float(reward),
            done=self.done,
            info={}
        )

    # ==================== OBSERVATION ====================
    def _build_observation(self):
        """
        Build observation from current state.
        
        Initially shows only API-level error.
        As checks are performed, more details are revealed.
        """
        # Start with API error (always visible)
        error = self.api.logs[0] if self.api.logs else "Unknown error"
        
        # Accumulate logs and metrics from checked services
        all_logs = []
        all_metrics = {}
        
        for service_name, obs_data in self.hidden_state.items():
            if "logs" in obs_data:
                all_logs.extend(obs_data["logs"])
            if "metrics" in obs_data:
                all_metrics.update({
                    f"{service_name}_{k}": v 
                    for k, v in obs_data["metrics"].items()
                })
        
        return {
            "error": error,
            "logs": " | ".join(all_logs) if all_logs else "",
            "metrics": all_metrics
        }

    # ==================== INVESTIGATION BONUS ====================
    def _calculate_investigation_bonus(self):
        """
        Calculate bonus based on investigation thoroughness.
        
        Returns:
            Bonus reward amount
        """
        required_done = sum(self.required_signals.values())
        total_required = len(self.required_signals)
        optional_done = sum(self.optional_signals.values())
        
        # No investigation at all
        if required_done == 0:
            return self.cfg["no_investigation"]
        
        # Partial investigation
        elif required_done < total_required:
            return self.cfg["partial_investigation"]
        
        # Full investigation
        else:
            bonus = self.cfg["final_bonus"]
            
            # Extra bonus for optional checks
            if optional_done > 0:
                bonus += self.cfg["optional_bonus"]
            
            return bonus

    # ==================== STATE ====================
    def state(self):
        """
        Get current environment state.
        
        Returns:
            State object with task info and progress
        """
        return State(
            task=self.task.name if self.task else "none",
            actions_taken=self.actions_taken,
            total_reward=self.total_reward,
            done=self.done
        )

    # ==================== GRADE ====================
    def grade(self):
        """
        Calculate normalized score for the current episode.
        
        Returns:
            GradeResponse with score between 0.01 and 0.99
        """
        if not self.task or not self.actions_taken:
            return GradeResponse(score=0.01)
        
        # Estimate max possible score
        # Perfect: all required checks (3pts each) + optional (3pts each) + solution (20pts) + full bonus (10pts) + optional bonus (2pts)
        num_required = len(self.task.required_signals)
        num_optional = len(self.task.optional_signals)
        
        max_score = (
            num_required * 3 +  # Required checks
            num_optional * 3 +  # Optional checks
            20 +  # Solution reward
            self.cfg["final_bonus"] +
            self.cfg["optional_bonus"]
        )
        
        # Worst case: no investigation, wrong fix
        min_score = self.cfg["no_investigation"] + self.cfg["invalid_action"]
        
        # Normalize
        if max_score == min_score:
            normalized = 0.5
        else:
            normalized = (self.total_reward - min_score) / (max_score - min_score)
        
        # Clamp to [0.01, 0.99]
        score = max(0.01, min(0.99, normalized))
        
        return GradeResponse(score=round(score, 3))

from server.task import Task

class TaskManager:
    """Manages the collection of all available debugging tasks."""
    
    @staticmethod
    def get_all_tasks():
        """Returns all available tasks."""
        return [
            # ========== AUTHENTICATION ISSUES ==========
            Task(
                name="auth_token_expired",
                issues={"auth": "token_expired"},
                solution="refresh_tokens",
                required_signals=["check_auth"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="invalid_token",
                issues={"auth": "invalid_token"},
                solution="fix_invalid_token",
                required_signals=["check_auth"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="auth_service_down",
                issues={"auth": "auth_service_down"},
                solution="restart_auth",
                required_signals=["check_auth"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="rate_limit_auth",
                issues={"auth": "rate_limit_auth"},
                solution="increase_rate_limit",
                required_signals=["check_auth"],
                optional_signals=["check_api"]
            ),
            
            # ========== DATABASE ISSUES ==========
            Task(
                name="slow_query",
                issues={"db": "slow_query"},
                solution="optimize_query",
                required_signals=["check_db"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="connection_pool_exhausted",
                issues={"db": "connection_pool"},
                solution="increase_pool",
                required_signals=["check_db"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="database_down",
                issues={"db": "db_down"},
                solution="restart_db",
                required_signals=["check_db"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="disk_full",
                issues={"db": "disk_full"},
                solution="cleanup_disk",
                required_signals=["check_db"],
                optional_signals=["check_api"]
            ),
            
            # ========== CACHE ISSUES ==========
            Task(
                name="stale_cache_issue",
                issues={"cache": "stale_cache"},
                solution="clear_cache",
                required_signals=["check_cache"],
                optional_signals=["check_db", "check_api"]
            ),
            
            Task(
                name="cache_miss_issue",
                issues={"cache": "cache_miss"},
                solution="scale_cache",
                required_signals=["check_cache"],
                optional_signals=["check_db", "check_api"]
            ),
            
            Task(
                name="cache_down",
                issues={"cache": "cache_down"},
                solution="restart_cache",
                required_signals=["check_cache"],
                optional_signals=["check_api"]
            ),
            
            # ========== QUEUE ISSUES ==========
            Task(
                name="queue_backlog",
                issues={"queue": "queue_backlog"},
                solution="scale_consumers",
                required_signals=["check_queue"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="consumer_down",
                issues={"queue": "consumer_down"},
                solution="restart_consumer",
                required_signals=["check_queue"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="message_loss",
                issues={"queue": "message_loss"},
                solution="fix_ack_logic",
                required_signals=["check_queue"],
                optional_signals=["check_api"]
            ),
            
            # ========== LOAD BALANCER ISSUES ==========
            Task(
                name="uneven_routing",
                issues={"lb": "uneven_routing"},
                solution="fix_routing",
                required_signals=["check_lb"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="lb_down",
                issues={"lb": "lb_down"},
                solution="restart_lb",
                required_signals=["check_lb"],
                optional_signals=["check_api"]
            ),
            
            # ========== MULTI-ROOT ISSUES (ADVANCED) ==========
            Task(
                name="auth_db_combined_issue",
                issues={
                    "auth": "invalid_token",
                    "db": "connection_pool"
                },
                solution="increase_pool",  # Must fix both, but this completes it
                required_signals=["check_auth", "check_db"],
                optional_signals=["check_api"]
            ),
            
            Task(
                name="cache_queue_dependency",
                issues={
                    "queue": "queue_backlog",
                    "cache": "cache_miss"
                },
                solution="scale_consumers",
                required_signals=["check_queue", "check_cache"],
                optional_signals=["check_api", "check_db"]
            ),
            
            Task(
                name="full_system_failure",
                issues={
                    "db": "db_down",
                    "auth": "auth_service_down"
                },
                solution="restart_db",  # Critical path
                required_signals=["check_db", "check_auth"],
                optional_signals=["check_api"]
            ),
        ]
    
    @staticmethod
    def get_all_task_names():
        """Returns list of all task names."""
        return [task.name for task in TaskManager.get_all_tasks()]
    
    @staticmethod
    def get_task_by_name(name):
        """Get a specific task by name."""
        for task in TaskManager.get_all_tasks():
            if task.name == name:
                return task
        raise ValueError(f"Task '{name}' not found")
    
    @staticmethod
    def get_random_task():
        """Get a random task (cycles through all tasks)."""
        import random
        tasks = TaskManager.get_all_tasks()
        return random.choice(tasks)
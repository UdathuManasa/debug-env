class Task:
    """
    Defines a debugging task scenario.
    
    A task specifies:
    - Which services have issues
    - What investigation steps are required/optional
    - What the correct solution is
    """
    
    def __init__(self, name, issues, solution, required_signals, optional_signals):
        """
        Args:
            name: Unique task identifier
            issues: Dict mapping service names to issue types
                   e.g., {"db": "slow_query", "auth": "token_expired"}
            solution: The action that resolves the task
                     e.g., "optimize_query" or "refresh_tokens"
            required_signals: List of check actions that should be performed
                            e.g., ["check_db", "check_auth"]
            optional_signals: List of optional check actions for bonus points
                            e.g., ["check_api", "check_cache"]
        """
        self.name = name
        self.issues = issues
        self.solution = solution
        self.required_signals = required_signals
        self.optional_signals = optional_signals


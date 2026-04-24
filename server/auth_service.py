class AuthService:
    def __init__(self):
        self.name = "auth"
        self.reset()

    # ------------------------
    # Reset state
    # ------------------------
    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "auth_error_rate": 0.0,
            "latency": 50,
            "request_rate": 200
        }

    # ------------------------
    # Inject Issue
    # ------------------------
    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        if issue == "token_expired":
            self.logs = [
                "Token validation failed",
                "Expiry timestamp older than current time"
            ]
            self.metrics = {
                "auth_error_rate": 0.5,
                "latency": 100,
                "request_rate": 200
            }

        elif issue == "invalid_token":
            self.logs = [
                "JWT signature verification failed",
                "Malformed token received"
            ]
            self.metrics = {
                "auth_error_rate": 0.6,
                "latency": 80,
                "request_rate": 180
            }

        elif issue == "auth_service_down":
            self.status = "down"
            self.logs = [
                "Connection refused to auth service",
                "Timeout while contacting auth"
            ]
            self.metrics = {
                "auth_error_rate": 1.0,
                "latency": None,
                "request_rate": 0
            }

        elif issue == "rate_limit_auth":
            self.logs = [
                "Too many requests",
                "Rate limit exceeded for auth endpoint"
            ]
            self.metrics = {
                "auth_error_rate": 0.4,
                "latency": 150,
                "request_rate": 1000
            }

    # ------------------------
    # Actions (Investigation)
    # ------------------------
    def check_auth_service(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 3  # reward for investigation

    # ------------------------
    # Actions (Fixes)
    # ------------------------

    def restart_auth(self):
        if self.issue == "auth_service_down":
            self._resolve()
            return 20, True

        elif self.issue in ["token_expired", "invalid_token"]:
            return 1, False  # restart doesn't fix logic bugs

        return -5, False

    def refresh_tokens(self):
        if self.issue == "token_expired":
            self._resolve()
            return 20, True

        return -5, False

    def fix_invalid_token(self):
        if self.issue == "invalid_token":
            self._resolve()
            return 20, True

        return -5, False

    def increase_rate_limit(self):
        if self.issue == "rate_limit_auth":
            self._resolve()
            return 20, True

        return -5, False

    # ------------------------
    # Resolve helper
    # ------------------------
    def _resolve(self):
        self.issue = None
        self.status = "healthy"
        self.logs = []
        self.metrics = {
            "auth_error_rate": 0.0,
            "latency": 50,
            "request_rate": 200
        }
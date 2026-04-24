from server.base_service import BaseService

class APIService(BaseService):
    def __init__(self, db_service, auth_service):
        super().__init__("api")
        self.db = db_service
        self.auth = auth_service
        self.issue = None

    # ------------------------
    # Reset
    # ------------------------
    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "latency": 100,
            "error_rate": 0.0,
            "request_rate": 500
        }

    # ------------------------
    # Inject Issue (API reflects downstream problems)
    # ------------------------
    def inject_issue(self):
        self.reset()

        # API derives behavior from DB + Auth
        db_issue = self.db.issue
        auth_issue = self.auth.issue

        # -------- AUTH RELATED --------
        if auth_issue == "token_expired" or auth_issue == "invalid_token":
            self.status = "degraded"
            self.logs = [
                "401 Unauthorized responses increasing",
                "Authentication failures observed"
            ]
            self.metrics.update({
                "error_rate": 0.4,
                "latency": 120
            })

        elif auth_issue == "auth_service_down":
            self.status = "down"
            self.logs = [
                "Upstream auth service not responding",
                "Request timeout during authentication"
            ]
            self.metrics.update({
                "error_rate": 1.0,
                "latency": None
            })

        elif auth_issue == "rate_limit_auth":
            self.status = "degraded"
            self.logs = [
                "Too many authentication requests",
                "Rate limiting errors observed"
            ]
            self.metrics.update({
                "error_rate": 0.3,
                "latency": 150
            })

        # -------- DB RELATED --------
        elif db_issue == "slow_query":
            self.status = "degraded"
            self.logs = [
                "Request processing slower than expected",
                "Downstream latency increased"
            ]
            self.metrics.update({
                "latency": 900,
                "error_rate": 0.2
            })

        elif db_issue == "connection_pool":
            self.status = "degraded"
            self.logs = [
                "Service timeout errors observed",
                "Failed to fetch data intermittently"
            ]
            self.metrics.update({
                "error_rate": 0.3,
                "latency": 400
            })

        elif db_issue == "db_down":
            self.status = "down"
            self.logs = [
                "500 Internal Server Error",
                "Database dependency unreachable"
            ]
            self.metrics.update({
                "error_rate": 1.0,
                "latency": None
            })

        elif db_issue == "disk_full":
            self.status = "degraded"
            self.logs = [
                "Write operations failing",
                "Data persistence errors observed"
            ]
            self.metrics.update({
                "error_rate": 0.5,
                "latency": 300
            })

        # -------- MULTI ROOT (advanced) --------
        if db_issue and auth_issue:
            self.logs.append("Multiple downstream dependencies failing")
            self.metrics["error_rate"] = min(1.0, self.metrics["error_rate"] + 0.2)

    # ------------------------
    # Investigation
    # ------------------------
    def check_api(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 2  # slightly lower than deeper checks

    # ------------------------
    # Fixes (mostly WRONG fixes)
    # ------------------------
    def restart_api(self):
        if self.status == "down":
            # temporary recovery only
            self.status = "degraded"
            self.logs.append("API restarted but issue persists")
            return 2, False

        return -5, False

    def scale_api(self):
        # scaling doesn't fix root cause usually
        self.metrics["latency"] = max(150, self.metrics["latency"] - 100) if self.metrics["latency"] else None
        return 1, False

    def no_op(self):
        return -2, False
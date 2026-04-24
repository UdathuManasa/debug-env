from server.base_service import BaseService

class DatabaseService(BaseService):
    def __init__(self):
        super().__init__("database")
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
            "connections_used": 20,
            "disk_usage": 50
        }

    # ------------------------
    # Inject Issue
    # ------------------------
    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        # ---------- PERFORMANCE ----------
        if issue == "slow_query":
            self.status = "degraded"
            self.logs = [
                "Execution time exceeded threshold",
                "Sequential scan detected"
            ]
            self.metrics.update({
                "latency": 1000,
                "error_rate": 0.1
            })

        elif issue == "connection_pool":
            self.status = "degraded"
            self.logs = [
                "Pool limit reached",
                "Timeout acquiring connection"
            ]
            self.metrics.update({
                "connections_used": 100,
                "error_rate": 0.4
            })

        # ---------- AVAILABILITY ----------
        elif issue == "db_down":
            self.status = "down"
            self.logs = [
                "Connection refused",
                "Database not reachable"
            ]
            self.metrics.update({
                "latency": None,
                "error_rate": 1.0
            })

        # ---------- RESOURCE ----------
        elif issue == "disk_full":
            self.status = "degraded"
            self.logs = [
                "Disk space full",
                "Write operations failing"
            ]
            self.metrics.update({
                "disk_usage": 100,
                "error_rate": 0.6
            })

    # ------------------------
    # Investigation
    # ------------------------
    def check_db(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 3

    # ------------------------
    # Fixes
    # ------------------------

    def optimize_query(self):
        if self.issue == "slow_query":
            self._resolve()
            return 20, True
        return -5, False

    def increase_pool(self):
        if self.issue == "connection_pool":
            self._resolve()
            return 20, True
        return -5, False

    def restart_db(self):
        if self.issue == "db_down":
            self._resolve()
            self.logs.append("Database restarted successfully")
            return 20, True

        elif self.issue == "slow_query":
            # temporary improvement
            self.metrics["latency"] = max(200, self.metrics["latency"] - 300)
            return 2, False

        elif self.issue == "connection_pool":
            self.logs.append("Restart helped temporarily")
            return 1, False

        elif self.issue == "disk_full":
            self.logs.append("Restarted but disk still full")
            return 1, False

        return -5, False

    def cleanup_disk(self):
        if self.issue == "disk_full":
            self._resolve()
            self.metrics["disk_usage"] = 60
            return 20, True
        return -5, False

    # ------------------------
    # Resolve
    # ------------------------
    def _resolve(self):
        self.issue = None
        self.status = "healthy"
        self.logs = ["Issue resolved"]
        self.metrics = {
            "latency": 100,
            "error_rate": 0.0,
            "connections_used": 20,
            "disk_usage": 50
        }
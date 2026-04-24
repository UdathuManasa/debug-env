from server.base_service import BaseService
class AppServerService(BaseService):
    def __init__(self):
        super().__init__("app_server")
        self.issue = None

    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "latency": 100,
            "error_rate": 0.0,
            "memory_usage": 40
        }

    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        if issue == "instance_crash":
            self.status = "degraded"
            self.logs = ["One instance crashed"]
            self.metrics["error_rate"] = 0.3

        elif issue == "memory_leak":
            self.status = "degraded"
            self.logs = ["Memory usage increasing"]
            self.metrics.update({
                "memory_usage": 95,
                "latency": 500
            })

    # -------- Investigation
    def check_app(self):
        return {"logs": self.logs, "metrics": self.metrics, "status": self.status}, 3

    # -------- Fixes
    def restart_app(self):
        if self.issue == "instance_crash":
            self._resolve()
            return 20, True
        return -5, False

    def fix_memory(self):
        if self.issue == "memory_leak":
            self._resolve()
            return 20, True
        return -5, False

    def scale_app(self):
        # weak fix
        self.metrics["latency"] = max(150, self.metrics["latency"] - 100)
        return 1, False

    def _resolve(self):
        self.reset()
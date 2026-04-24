class BaseService:
    def __init__(self, name):
        self.name = name
        self.status = "healthy"  # healthy / degraded / down
        self.logs = []
        self.metrics = {}

    def get_logs(self):
        return self.logs

    def get_metrics(self):
        return self.metrics

    def get_status(self):
        return self.status

    def reset(self):
        self.status = "healthy"
        self.logs = []
        self.metrics = {}

    # Default actions (can be overridden)
    def check(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }

    def restart(self):
        self.status = "healthy"
        self.logs.append(f"{self.name} restarted")
        return 2  # small positive reward (generic)
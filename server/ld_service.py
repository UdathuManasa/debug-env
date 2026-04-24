from server.base_service import BaseService

class LoadBalancerService(BaseService):
    def __init__(self):
        super().__init__("load_balancer")
        self.issue = None

    # ------------------------
    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "traffic_skew": 0.1,
            "latency": 50
        }

    # ------------------------
    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        if issue == "uneven_routing":
            self.status = "degraded"
            self.logs = [
                "Traffic unevenly distributed",
                "One instance overloaded"
            ]
            self.metrics.update({
                "traffic_skew": 0.9,
                "latency": 300
            })

        elif issue == "lb_down":
            self.status = "down"
            self.logs = [
                "Load balancer not responding",
                "All requests failing"
            ]
            self.metrics.update({
                "latency": None
            })

    # ------------------------
    def check_lb(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 3

    # ------------------------
    def fix_routing(self):
        if self.issue == "uneven_routing":
            self._resolve()
            return 20, True
        return -5, False

    def restart_lb(self):
        if self.issue == "lb_down":
            self._resolve()
            return 20, True
        return 1, False

    # ------------------------
    def _resolve(self):
        self.reset()
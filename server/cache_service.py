from server.base_service import BaseService

class CacheService(BaseService):
    def __init__(self):
        super().__init__("cache")
        self.issue = None

    # ------------------------
    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "hit_rate": 0.8,
            "latency": 20
        }

    # ------------------------
    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        if issue == "cache_miss":
            self.status = "degraded"
            self.logs = [
                "Cache miss rate increasing",
                "Frequent DB fallback observed"
            ]
            self.metrics.update({
                "hit_rate": 0.2,
                "latency": 80
            })

        elif issue == "stale_cache":
            self.status = "degraded"
            self.logs = [
                "Serving outdated data",
                "Cache invalidation delay detected"
            ]
            self.metrics.update({
                "hit_rate": 0.7
            })

        elif issue == "cache_down":
            self.status = "down"
            self.logs = [
                "Cache not reachable",
                "Fallback to database"
            ]
            self.metrics.update({
                "hit_rate": 0.0,
                "latency": 200
            })

    # ------------------------
    def check_cache(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 3

    # ------------------------
    def clear_cache(self):
        if self.issue == "stale_cache":
            self._resolve()
            return 20, True
        return -5, False

    def scale_cache(self):
        if self.issue == "cache_miss":
            self._resolve()
            return 20, True
        return -5, False

    def restart_cache(self):
        if self.issue == "cache_down":
            self._resolve()
            return 20, True
        return 1, False  # weak fix otherwise

    # ------------------------
    def _resolve(self):
        self.reset()
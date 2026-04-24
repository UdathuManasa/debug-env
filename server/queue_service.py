from server.base_service import BaseService

class QueueService(BaseService):
    def __init__(self):
        super().__init__("queue")
        self.issue = None

    # ------------------------
    def reset(self):
        self.status = "healthy"
        self.issue = None
        self.logs = []
        self.metrics = {
            "queue_depth": 10,
            "processing_rate": 100,   # msgs/sec
            "lag": 1                  # seconds delay
        }

    # ------------------------
    def inject_issue(self, issue):
        self.reset()
        self.issue = issue

        # ---------- BACKLOG ----------
        if issue == "queue_backlog":
            self.status = "degraded"
            self.logs = [
                "Message backlog increasing",
                "Consumers unable to keep up"
            ]
            self.metrics.update({
                "queue_depth": 1000,
                "processing_rate": 50,
                "lag": 20
            })

        # ---------- CONSUMER DOWN ----------
        elif issue == "consumer_down":
            self.status = "down"
            self.logs = [
                "No active consumers",
                "Messages accumulating in queue"
            ]
            self.metrics.update({
                "queue_depth": 2000,
                "processing_rate": 0,
                "lag": 100
            })

        # ---------- MESSAGE LOSS ----------
        elif issue == "message_loss":
            self.status = "degraded"
            self.logs = [
                "Message acknowledgment failures",
                "Retry attempts increasing"
            ]
            self.metrics.update({
                "queue_depth": 200,
                "processing_rate": 80,
                "lag": 10
            })

    # ------------------------
    # Investigation
    # ------------------------
    def check_queue(self):
        return {
            "logs": self.logs,
            "metrics": self.metrics,
            "status": self.status
        }, 3

    # ------------------------
    # Fixes
    # ------------------------
    def scale_consumers(self):
        if self.issue == "queue_backlog":
            self._resolve()
            return 20, True
        return -5, False

    def restart_consumer(self):
        if self.issue == "consumer_down":
            self._resolve()
            return 20, True
        return -5, False

    def fix_ack_logic(self):
        if self.issue == "message_loss":
            self._resolve()
            return 20, True
        return -5, False

    def restart_queue(self):
        # weak / temporary fix
        self.metrics["lag"] = max(5, self.metrics["lag"] - 10)
        return 1, False

    # ------------------------
    def _resolve(self):
        self.reset()
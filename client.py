import openenv
import requests
from models import Observation, Action, StepResult, State, GradeResponse

class OpenEnvClient(openenv.OpenEnvClient):
    def __init__(self, url: str):
        # Ensure the URL doesn't have a trailing slash
        self.url = url.rstrip("/")
        self.timeout = 10

    def reset(self, task: str = None) -> StepResult:
        url = f"{self.url}/reset"
        if task:
            url += f"?task={task}"

        response = requests.post(url, timeout=self.timeout)
        response.raise_for_status()
        return StepResult(**response.json())

    def step(self, action: Action) -> StepResult:
        """Sends an action to the /step endpoint."""
        response = requests.post(f"{self.url}/step", json=action.model_dump(),timeout=self.timeout)
        response.raise_for_status()
        return StepResult(**response.json())

    def state(self) -> State:
        """Fetches the current state of the environment."""
        response = requests.get(f"{self.url}/state",timeout=self.timeout)
        response.raise_for_status()
        return State(**response.json())

    def grade(self) -> GradeResponse:
        """Calls the /grade endpoint to get the final score (0.0 - 1.0)."""
        response = requests.get(f"{self.url}/grade",timeout=self.timeout)
        response.raise_for_status()
        return GradeResponse(**response.json())
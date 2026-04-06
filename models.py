from pydantic import BaseModel
from typing import Dict, Any, List


class Observation(BaseModel):
    error: str
    logs: str
    metrics: Dict[str, Any]


class Action(BaseModel):
    action: str


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any] = {}


class State(BaseModel):
    task: str
    step_index: int
    actions_taken: List[str]
    total_reward: float
    done: bool


class GradeResponse(BaseModel):
    score: float
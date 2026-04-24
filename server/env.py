from server.models import Observation, StepResult, State, GradeResponse
from server.task import TaskManager


class DebugEnv:

    def __init__(self):
        self.task = None

    def _ensure_task(self):
        if self.task is None:
            self.task = TaskManager.get_random_task()

    # ---------------- RESET ----------------
    def reset(self, task_name=None):
        if task_name:
            self.task = TaskManager.get_task_by_name(task_name)
        else:
            self.task = TaskManager.get_random_task()

        self.task.reset_state()

        return StepResult(
            observation=Observation(**self.task.observation),
            reward=0.0,
            done=False,
            info={}
        )

    # ---------------- STEP ----------------
    def step(self, action: str):
        try:
            self._ensure_task()
            if  self.task.is_done():
                return StepResult(
                    observation=Observation(**self.task.observation),
                    reward=0.0,
                    done=True,
                    info={}
                )

            reward = self.task.apply_action(action)
            done = self.task.is_done()

            return StepResult(
                observation=Observation(**self.task.observation),
                reward=float(reward),
                done=done,
                info={}
            )
        except Exception as e:
            return StepResult(
                observation=Observation(
                    error=str(e),
                    logs="",
                    metrics={}
                ),
                reward=0.01,
                done=True,
                info={}
            )

    # ---------------- STATE ----------------
    def state(self):
        
        self._ensure_task()
        return State(
            task=self.task.name,
            actions_taken=self.task.actions_taken,
            total_reward=self.task.total_reward,
            done=self.task.done
        )

    # ---------------- GRADER ----------------
    def grade(self):
        try:
            self._ensure_task()

            if not self.task.actions_taken:
                return GradeResponse(score=0.01)

            cfg = self.task.reward_config

            relevant_actions = set(self.task.required_signals.keys()) | \
                            set(self.task.optional_signals.keys()) | \
                            {self.task.solution}

            max_possible = sum(
                self.task.step_weights.get(a, 0) for a in relevant_actions
            ) + cfg["final_bonus"] + cfg.get("optional_bonus", 0)

            min_possible = cfg["no_investigation_penalty"]

            score = (self.task.total_reward - min_possible) / (max_possible - min_possible)

            score = max(0.01, min(0.99, score))

            return GradeResponse(score=round(score, 3))

        except Exception:
            return GradeResponse(score=0.01)


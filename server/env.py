from server.models import Observation, Action, StepResult, State, GradeResponse
from server.task import TaskManager


class DebugEnv:

    def __init__(self):
        self.task = None

    def _ensure_task(self):
        # This 'if' is the most important line of code.
        # If self.task is NOT None (it's already been set), 
        # this function finishes instantly and does NOTHING.
        if self.task is None:
            from server.task import TaskManager
            self.task = TaskManager.get_random_task()

    # ---------------- RESET ----------------
    def reset(self):
        self.task = TaskManager.get_random_task()
 
        return StepResult(
            observation=Observation(**self.task.observation),
            reward=0.0,
            done=False,
            info = {
                "progress": self.task.step_index,
                "remaining_steps": len(self.task.flow) - self.task.step_index,
                "total_steps_taken": len(self.task.actions_taken)
            }
        )

    # ---------------- STEP ----------------
    def step(self, action: Action):
        try:
            self._ensure_task()
            if  self.task.is_done():
                return StepResult(
                    observation=Observation(**self.task.observation),
                    reward=0.0,
                    done=True,
                    info = {
                        "progress": self.task.step_index,
                        "remaining_steps": 0,
                        "total_steps_taken": len(self.task.actions_taken)
                    }
                )

            reward = self.task.apply_action(action)
            done = self.task.is_done()

            return StepResult(
                observation=Observation(**self.task.observation),
                reward=float(reward),
                done=done,
                info = {
                    "progress": self.task.step_index,
                    "remaining_steps": len(self.task.flow) - self.task.step_index,
                    "total_steps_taken": len(self.task.actions_taken)
                }
            )
        except Exception as e:
            observation={
                    "error": str(e),
                    "logs": "",
                    "metrics": {}
            }
            return StepResult(
                observation=Observation(observation),
                reward=0.01,
                done=True,
                info = {
                    "progress": 0,
                    "remaining_steps": 0,
                    "total_steps_taken": 0
                }
            )

    # ---------------- STATE ----------------
    
    def state(self):
        try: 
            self._ensure_task()
            return State(
                task=self.task.name,
                step_index=self.task.step_index,
                actions_taken=self.task.actions_taken,
                total_reward=self.task.total_reward,
                done=self.task.done
            )
        except Exception as e:
            return State(
                task=str(e),
                step_index=0,
                actions_taken=0,
                total_reward=0.01,
                done=True
            )
        
    

    # ---------------- GRADER ----------------
    def grade(self):
        try:
            self._ensure_task()

            if not self.task.actions_taken:
                return 0.0

            max_possible = 0

            for i, action in enumerate(self.task.flow):
                base = self.task.step_weights.get(action, self.task.reward_config["default_weight"])
                max_possible += base + (i * self.task.reward_config["progress_bonus"])

            max_possible += self.task.reward_config["final_bonus"]

            score = self.task.total_reward / max_possible

            cur_grade =  max(0.01, min(0.99, score))
            return GradeResponse(score=cur_grade)
        except Exception:
            return GradeResponse(score=0.01)


from server.models import Observation, Action, StepResult, State, GradeResponse
from server.task import TaskManager


class DebugEnv:

    def __init__(self):
        self.task = None

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

    # ---------------- STATE ----------------
    
    def state(self):
        return State(
            task=self.task.name,
            step_index=self.task.step_index,
            actions_taken=self.task.actions_taken,
            total_reward=self.task.total_reward,
            done=self.task.done
        )
    

    # ---------------- GRADER ----------------
    def grade(self):

        if not self.task.actions_taken:
            return 0.0

        max_possible = 0

        for i, action in enumerate(self.task.flow):
            base = self.task.step_weights.get(action, self.task.reward_config["default_weight"])
            max_possible += base + (i * self.task.reward_config["progress_bonus"])

        max_possible += self.task.reward_config["final_bonus"]

        score = self.task.total_reward / max_possible

        cur_grade =  max(0.0, min(1.0, score))
        return GradeResponse(score=cur_grade)
    


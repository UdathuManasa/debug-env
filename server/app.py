from fastapi import FastAPI, Query
from server.models import Action, StepResult, State, GradeResponse
from server.env import DebugEnv
from server.taskmanager import TaskManager
import uvicorn

app = FastAPI()

env = DebugEnv()


@app.get("/health")
def health():
    """Confirms the server is alive for the deployment platform."""
    return {"status": "healthy"}

@app.get("/metadata")
def metadata():
    """Identifies your project for the leaderboard."""
    return {
        "name": "OpenEnv Debug Project",
        "description": "Meta PyTorch Hackathon Environment"
    }

@app.get("/schema")
def schema():
    """Tells the AI agent what the Action and State structures look like."""
    return {
        "action": Action.model_json_schema(),
        "observation": StepResult.model_json_schema(),
        "state": State.model_json_schema()
    }

@app.post("/mcp")
def mcp():
    """Provides Model Context Protocol support."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"status": "connected"}
    }

#--------------------- GET Tasks --------------
@app.get("/tasks")
def get_tasks():
    return {"tasks": TaskManager.get_all_task_names()}

# ---------------- RESET ----------------
@app.post("/reset", response_model=StepResult)
def reset(task: str = Query(None)):
    return env.reset(task)



# ---------------- STEP ----------------
@app.post("/step", response_model=StepResult)
def step(action: Action):
    return env.step(action.action)
    


# ---------------- STATE ----------------
@app.get("/state", response_model=State)
def state():
    return env.state()


# ---------------- GRADE ----------------
@app.get("/grade", response_model=GradeResponse)
def grade():
    return env.grade()



def main():
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()


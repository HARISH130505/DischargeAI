from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional, Any, Dict
from engine.environment import DischargeAIEnv
from engine.models import Action

app = FastAPI(title="DischargeAI Environment API")

# Global environment state (acceptable for typical OpenEnv standalone Docker evaluation)
env_instance = DischargeAIEnv()

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <h1>🚀 DischargeAI API is Live</h1>
    <p>Your backend is running successfully.</p>
    <p>Go to <a href="/docs">/docs</a> to test the API.</p>
    """

class ResetRequest(BaseModel):
    task: str = "EASY"

class StepRequest(BaseModel):
    action: Dict[str, Any]

@app.post("/reset")
def reset(req: Optional[ResetRequest] = None):
    task_name = req.task if req else "EASY"
    try:
        obs = env_instance.reset(task_name=task_name)
        return {"observation": obs.dict(), "done": False, "reward": 0.0}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step")
def step(req: StepRequest):
    try:
        action_obj = Action(**req.action)
        result = env_instance.step(action_obj)
        return {
            "observation": result["observation"].dict(),
            "reward": result["reward"],
            "done": result["done"],
            "info": result["info"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
def state():
    try:
        obs = env_instance.state()
        return {
            "observation": obs.dict(),
            "done": env_instance.step_count >= env_instance.max_steps
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/tasks")
def list_tasks():
    """Return the list of available tasks with metadata."""
    return {
        "tasks": [
            {"id": "EASY", "name": "EASY", "difficulty": "easy", "max_steps": 5,
             "description": "Stable post-appendectomy patient with full home support. Correct action: discharge."},
            {"id": "MEDIUM", "name": "MEDIUM", "difficulty": "medium", "max_steps": 5,
             "description": "Hip replacement patient with high fall risk. Correct action: refer."},
            {"id": "HARD", "name": "HARD", "difficulty": "hard", "max_steps": 5,
             "description": "COPD patient with borderline vitals. Correct action: keep then discharge."},
        ]
    }

class GraderRequest(BaseModel):
    task_id: str
    state: Dict[str, Any] = {}
    reward: float = 0.0

@app.post("/grader")
def grader(req: GraderRequest):
    """Grade the agent's performance for a given task."""
    import graders as g
    grader_map = {
        "EASY": g.grade_easy,
        "MEDIUM": g.grade_medium,
        "HARD": g.grade_hard,
    }
    task_id = req.task_id.upper()
    if task_id not in grader_map:
        raise HTTPException(status_code=400, detail=f"Unknown task_id: {task_id}")
    score = grader_map[task_id](req.state, req.reward)
    return {"score": score, "task_id": task_id}

@app.get("/baseline")
def baseline():
    """Return a simple baseline agent description."""
    return {
        "model": "meta-llama/Llama-3.1-8B-Instruct",
        "strategy": "LLM-based discharge decision agent using Hugging Face Inference Router",
        "average_score": 0.82,
    }
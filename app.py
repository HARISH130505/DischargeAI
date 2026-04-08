from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict
from env.environment import DischargeAIEnv
from env.models import Action

app = FastAPI(title="DischargeAI Environment API")

# Global environment state (acceptable for typical OpenEnv standalone Docker evaluation)
env_instance = DischargeAIEnv()

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
        # Validate action
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
        return {"observation": obs.dict(), "done": env_instance.step_count >= env_instance.max_steps}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class PatientInfo(BaseModel):
    age: int
    condition: str
    vitals: str
    mobility: str
    home_support: str
    risk_level: str

class Observation(BaseModel):
    patient_info: PatientInfo
    day: int
    history: List[str]

class Action(BaseModel):
    decision: Literal["discharge", "keep", "refer"]
    instructions: str
    follow_up_days: int

class Reward(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    feedback: str

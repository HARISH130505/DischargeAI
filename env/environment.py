from typing import Optional, Dict, Any
from .models import Action, Observation, PatientInfo, Reward
from .tasks import TASKS
from .reward import calculate_reward

class DischargeAIEnv:
    def __init__(self):
        self.task_name: str = "EASY"
        self.current_obs: Optional[Observation] = None
        self.ideal_action: str = "discharge"
        self.step_count = 0
        self.max_steps = 5

    def reset(self, task_name: str = "EASY") -> Observation:
        if task_name not in TASKS:
            task_name = "EASY"
            
        self.task_name = task_name
        task_data = TASKS[task_name]
        
        self.ideal_action = task_data["ideal_action"]
        patient_info_copy = PatientInfo(**task_data["patient_info"].dict())
        
        self.current_obs = Observation(
            patient_info=patient_info_copy,
            day=1,
            history=[]
        )
        self.step_count = 0
        return self.current_obs

    def step(self, action: Action) -> Dict[str, Any]:
        if self.current_obs is None:
            raise ValueError("Environment must be reset before calling step.")
            
        self.step_count += 1
        
        # Calculate Reward
        score, feedback = calculate_reward(action, self.current_obs, self.ideal_action)
        reward = Reward(score=score, feedback=feedback)
        
        # Record history
        action_str = f"Day {self.current_obs.day}: Decision: {action.decision}, Instructs: {action.instructions[:20].strip()}..., Followup: {action.follow_up_days}d"
        self.current_obs.history.append(action_str)
        
        # Determine if done
        done = False
        if action.decision in ["discharge", "refer"]:
            done = True
        if self.step_count >= self.max_steps:
             done = True

        # State transition if kept
        if action.decision == "keep" and not done:
             self.current_obs.day += 1
             # Minor state adjustments based on task
             if self.task_name == "HARD" and self.current_obs.day == 2:
                 self.current_obs.patient_info.vitals = "Stabilizing (HR 85, BP 130/80, SpO2 95% on room air)"
                 self.current_obs.patient_info.risk_level = "Medium"
                 self.ideal_action = "discharge" # Patient improved!
        
        return {
            "observation": self.current_obs,
            "reward": reward.score,
            "done": done,
            "info": {"feedback": reward.feedback}
        }
        
    def state(self) -> Observation:
        if self.current_obs is None:
            raise ValueError("Environment must be reset before getting state.")
        return self.current_obs

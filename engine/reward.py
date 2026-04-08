from .models import Action, Observation

def calculate_reward(action: Action, obs: Observation, ideal_action: str) -> tuple[float, str]:
    score = 0.0
    feedback = ""
    
    # Check correctness of decision
    if action.decision == ideal_action:
        score += 0.6
        feedback += f"Correct decision to {ideal_action}. "
    else:
        # Penalties for mismatched actions
        if action.decision == "discharge" and ideal_action != "discharge":
            feedback += "Dangerous early discharge! "
            score += 0.0
        elif action.decision == "refer" and ideal_action == "discharge":
            feedback += "Unnecessary referral for stable patient. "
            score += 0.2
        elif action.decision == "keep" and ideal_action == "discharge":
            feedback += "Unnecessary prolonged hospital stay. "
            score += 0.2
        else:
            feedback += f"Suboptimal decision. Ideal was {ideal_action}. "
            score += 0.2
            
    # Check instructions quality
    if len(action.instructions.strip()) > 10:
        score += 0.2
        feedback += "Good instruction length. "
    else:
        feedback += "Instructions too short or empty. "
        
    # Check follow up
    if action.follow_up_days > 0 and action.follow_up_days <= 30:
        score += 0.2
        feedback += "Reasonable follow-up plan. "
    else:
        feedback += "Invalid or missing follow-up days. "
        
    # Clamp safety bounds explicitly
    score = max(0.0, min(1.0, float(score)))
    return score, feedback

from .models import Action, Observation

# Scores must be strictly between 0 and 1 (exclusive) per OpenEnv spec
_MIN_SCORE = 0.01
_MAX_SCORE = 0.99

def calculate_reward(action: Action, obs: Observation, ideal_action: str) -> tuple[float, str]:
    score = 0.0
    feedback = ""

    # Safety: Decision correctness (50% weight)
    if action.decision == ideal_action:
        score += 0.50
        feedback += f"Correct decision to {ideal_action}. "
    else:
        if action.decision == "discharge" and ideal_action != "discharge":
            feedback += "Dangerous early discharge! "
            score += 0.02  # severe penalty but not 0
        elif action.decision == "refer" and ideal_action == "discharge":
            feedback += "Unnecessary referral for stable patient. "
            score += 0.15
        elif action.decision == "keep" and ideal_action == "discharge":
            feedback += "Unnecessary prolonged hospital stay. "
            score += 0.15
        else:
            feedback += f"Suboptimal decision. Ideal was {ideal_action}. "
            score += 0.15

    # Instruction quality (30% weight) — partial credit for length
    instr_length = len(action.instructions.strip())
    if instr_length > 50:
        score += 0.30
        feedback += "Detailed instructions provided. "
    elif instr_length > 10:
        score += 0.15
        feedback += "Minimal instructions provided. "
    else:
        score += 0.02
        feedback += "Instructions too short or empty. "

    # Follow-up validity (20% weight)
    if 1 <= action.follow_up_days <= 14:
        score += 0.18
        feedback += "Appropriate short-term follow-up. "
    elif 15 <= action.follow_up_days <= 30:
        score += 0.12
        feedback += "Reasonable follow-up plan. "
    else:
        score += 0.02
        feedback += "Invalid or missing follow-up days. "

    # Clamp strictly to (0.01, 0.99) — never 0.0 or 1.0
    score = max(_MIN_SCORE, min(_MAX_SCORE, float(score)))
    return round(score, 4), feedback

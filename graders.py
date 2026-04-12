"""
graders.py — Grader functions for each task.
Each grader receives the final state dict and the reward float,
and returns a score strictly between 0.0 and 1.0 (exclusive).
"""

def _clamp(score: float) -> float:
    """Clamp score to strictly open interval (0.01, 0.99)."""
    return round(max(0.01, min(0.99, float(score))), 4)


def grade_easy(state: dict, reward: float) -> float:
    """
    EASY task grader: Stable post-appendectomy patient.
    Ideal action: discharge.
    """
    return _clamp(reward)


def grade_medium(state: dict, reward: float) -> float:
    """
    MEDIUM task grader: Hip replacement with high fall risk.
    Ideal action: refer.
    """
    return _clamp(reward)


def grade_hard(state: dict, reward: float) -> float:
    """
    HARD task grader: COPD patient with borderline vitals.
    Ideal action: keep (Day 1) then discharge (Day 2).
    """
    return _clamp(reward)

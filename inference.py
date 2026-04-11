import os
import requests
import textwrap
import json
from typing import List, Optional, Any, Dict
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY")

TASK_NAME = os.getenv("TASK_NAME", "EASY")
BENCHMARK = "DischargeAI"
SUCCESS_SCORE_THRESHOLD = 0.5
MAX_STEPS = 5
TEMPERATURE = 0.7
MAX_TOKENS = 250

# URL of our local / HF environment
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_val = error if error else "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )

def log_end(success: bool, steps: int, score: float, rewards: List[float]) -> None:
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rewards_str}", flush=True)

def build_system_prompt() -> str:
    return textwrap.dedent(
        """
        You are a hospital discharge planning assistant.
        You must decide whether to 'discharge', 'keep' (observation), or 'refer' (SNF/Rehab).
        You will receive patient information, day of stay, and history.
        You must reply with ONLY a JSON object exactly matching this schema:
        {
          "decision": "discharge" | "keep" | "refer",
          "instructions": "detailed instructions here",
          "follow_up_days": integer
        }
        Do not output any markdown code blocks, just raw JSON text.
        """
    ).strip()

def build_user_prompt(step: int, obs: Dict[str, Any], last_reward: float) -> str:
    return textwrap.dedent(
        f"""
        Step: {step}
        Observation: {json.dumps(obs, indent=2)}
        Last reward: {last_reward:.2f}
        Decide your next action and return the raw JSON object.
        """
    ).strip()

def get_model_message(client: OpenAI, step: int, obs: Dict[str, Any], last_reward: float) -> tuple[str, Optional[Dict[str, Any]], Optional[str]]:
    user_prompt = build_user_prompt(step, obs, last_reward)
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (completion.choices[0].message.content or "").strip()
        # strip markdown if present
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        action_dict = json.loads(text)
        # minimal validation
        assert "decision" in action_dict
        assert "instructions" in action_dict
        assert "follow_up_days" in action_dict
        return text.replace("\\n", " "), action_dict, None
    except Exception as exc:
        err_msg = str(exc).replace("\\n", " ")
        return "fallback", None, err_msg

def main():
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    history: List[str] = []
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=TASK_NAME, env=BENCHMARK, model=MODEL_NAME)
    
    try:
        # Reset environment
        reset_res = requests.post(f"{ENV_URL}/reset", json={"task": TASK_NAME})
        if reset_res.status_code != 200:
             raise Exception(f"Failed to reset: {reset_res.text}")
             
        result = reset_res.json()
        current_obs = result["observation"]
        done = result["done"]
        last_reward = result["reward"]

        for step in range(1, MAX_STEPS + 1):
            if done:
                break
                
            raw_action_str, action_dict, err = get_model_message(client, step, current_obs, last_reward)
            
            error_val = None
            if err:
                error_val = err
                # Create a fallback action just so we can step the env without breaking integration
                action_dict = {"decision": "keep", "instructions": "Fallback action due to JSON parsing error.", "follow_up_days": 1}
            
            # Step environment
            step_res = requests.post(f"{ENV_URL}/step", json={"action": action_dict})
            if step_res.status_code != 200:
                error_val = f"Env step error: {step_res.text}".replace("\\n", " ")
                # Break on environment failure to avoid infinite crash loops
                log_step(step=step, action=raw_action_str, reward=0.0, done=True, error=error_val)
                break
                
            result = step_res.json()
            current_obs = result["observation"]
            reward = result["reward"]
            done = result["done"]
            
            rewards.append(reward)
            steps_taken = step
            last_reward = reward
            
            log_step(step=step, action=json.dumps(action_dict).replace("\\n", ""), reward=reward, done=done, error=error_val)
            
            if done:
                break
                
        if rewards:
             score = sum(rewards)/len(rewards)
        else:
             score = 0.0
             
        score = min(max(score, 0.0), 1.0)
        success = score >= SUCCESS_SCORE_THRESHOLD

    except Exception as e:
        print(f"[DEBUG] error: {e}", flush=True)

    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

if __name__ == "__main__":
    main()

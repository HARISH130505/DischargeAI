---
title: DischargeAI
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---

# DischargeAI: Safe Patient Transition Environment

DischargeAI is a hospital discharge planning simulation where an AI agent decides whether to 'discharge', 'keep', or 'refer' a patient based on their condition, progression, and external factors like home support. This tests the agent's ability to balance patient safety, efficiency, and context-awareness.

## Task Setup
- **EASY:** Stable patient with robust support; safe to discharge immediately.
- **MEDIUM:** Highly vulnerable patient with high fall risk but stable viables; expects referral or prolonged stay.
- **HARD:** Patient requiring continued monitoring due to borderline vitals; expects 'keep' (observation) until condition stabilizes on day 2.

## Output Format
The agent interacts with the environment and must output a strict JSON payload:
```json
{
  "decision": "discharge",
  "instructions": "Follow up with PCP in 2 weeks. Take medications as prescribed in discharge instructions.",
  "follow_up_days": 14
}
```

## Agent Capabilities Evaluated
- Safety and protocol following vs. unwarranted discharge penalty.
- Instruction generation length and quality.
- Long-horizon planning (keeping a patient until vitals stabilize).

## Deployment Instructions

### Local Testing
```bash
pip install -r requirements.txt
uvicorn app:app --port 7860
```
Then, in another terminal, run:
```bash
python inference.py
```

### OpenEnv Validation
Use the provided `validate-submission.sh` script against your HF Space.
1. Push this repository to a Hugging Face Space using the Docker template.
2. In your Space **Settings**, add the following:
    *   **Secret**: `HF_TOKEN` (Your Hugging Face API key)
    *   **Variable**: `MODEL_NAME` with value `Qwen/Qwen2.5-72B-Instruct`
3. Once the build is complete and the Space is "Running", run the validation script with your HF space URL.

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

DischargeAI is a hospital discharge planning simulation where an AI agent decides whether to `discharge`, `keep` (observation), or `refer` (SNF/Rehab) a patient based on their condition, recovery progress, and external factors like home support. This tests the agent's ability to balance patient safety, efficiency, and context-awareness.

## Baseline Model

This environment uses **`meta-llama/Llama-3.1-8B-Instruct`** via the [Hugging Face Inference Router](https://router.huggingface.co/v1) as the baseline agent. No OpenAI key required — only a Hugging Face token with **"Make calls to Inference Providers"** permission.

## Task Setup

| Task | Patient Profile | Correct Action |
|------|----------------|----------------|
| **EASY** | Stable post-op patient, full home support, low risk | `discharge` |
| **MEDIUM** | Hip replacement patient, high fall risk, lives alone | `refer` (to rehab/SNF) |
| **HARD** | COPD patient, borderline SpO2 (93%), poor home setup | `keep` until Day 2, then `discharge` |

## Output Format

The agent must return a strict JSON payload:
```json
{
  "decision": "discharge",
  "instructions": "Follow up with PCP in 2 weeks. Take medications as prescribed.",
  "follow_up_days": 14
}
```

## Scoring

Each decision is scored on **3 criteria**, clamped to `[0.0, 1.0]`:
- **Safety (60%):** Correct decision relative to patient condition.
- **Instructions (20%):** Length and quality of care instructions.
- **Follow-up (20%):** Reasonable follow-up window (1–30 days).

## Agent Capabilities Evaluated

- Safety and protocol following vs. unwarranted discharge penalty.
- Instruction generation length and quality.
- Long-horizon planning (keeping a patient until vitals stabilize on day 2).

## Example Baseline Run

```
[START] task=EASY env=DischargeAI model=meta-llama/Llama-3.1-8B-Instruct
[STEP] step=1 action={"decision": "discharge", "instructions": "Discharge the patient as they are recovering well, have full support at home...", "follow_up_days": 7} reward=1.00 done=true error=null
[END] success=true steps=1 score=1.000 rewards=1.00
```

## Deployment Instructions

### Prerequisites
```bash
pip install requests openai "httpx<0.28.0"
```

### Run the Server Locally
```bash
uvicorn app:app --port 7860
```

### Run the Baseline Agent
```bash
# Set environment variables
export ENV_URL="https://h8j10-dischargeai.hf.space"   # or http://localhost:7860
export HF_TOKEN="<your-huggingface-token>"

# Run
python inference.py
```

> **Windows (PowerShell):**
> ```powershell
> $env:ENV_URL = "https://h8j10-dischargeai.hf.space"
> $env:HF_TOKEN = "<your-huggingface-token>"
> $env:TASK_NAME = "EASY"   # or MEDIUM, HARD
> python inference.py
> ```

### Deploying to Hugging Face Spaces (Docker)
1. Push this repository to a Hugging Face Space using the **Docker** template.
2. In your Space **Settings → Variables and Secrets**, add:
    - **Secret**: `HF_TOKEN` — your Hugging Face token (needs "Make calls to Inference Providers" permission)
    - **Variable**: `MODEL_NAME` — `meta-llama/Llama-3.1-8B-Instruct` (optional, this is the default)
3. Once the Space status shows **Running**, validate with:
    ```bash
    ./validate-submission.sh https://h8j10-dischargeai.hf.space
    ```

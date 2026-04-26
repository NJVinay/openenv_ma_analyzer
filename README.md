---
title: M&A Due Diligence RL Environment
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# M&A Due Diligence RL Environment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NJVinay/openenv_ma_analyzer/blob/master/training/grpo_training.ipynb)

This is an OpenEnv-compliant environment designed to train agents for M&A due diligence tasks. The goal is to advance model capabilities from simple risk identification to complex legal reasoning and clause negotiation.

## Technical Stack
* **Model:** Qwen2.5-7B-Instruct (optimized via Unsloth)
* **Training:** GRPO (Group Relative Policy Optimization)
* **Environment:** FastAPI (OpenEnv compliant)
* **Compute:** NVIDIA A100 80GB (optimized for 2048-token reasoning)

## Architectural Decisions

### Long-Horizon Reasoning
The architecture incentivizes "thinking" over pattern-matching by implementing a deliberation bonus. The model is prompted to write a `<think>` block before emitting JSON. If the analysis is sufficiently detailed (>500 characters), the environment awards a +0.2 reward bonus. This shift encourages genuine legal analysis rather than simple formatting.

### High-Throughput Training
During the primary GRPO run, the pipeline bypasses standard HTTP rate limits by running the environment in-process. This enables significantly faster training on the A100 by eliminating network overhead and 429 throttling errors.

## Curriculum and Grading
The environment uses a three-tier curriculum that unlocks sequentially as the agent masters lower-level tasks:
1. **Analyst (Easy):** Red flag identification in NDAs.
2. **Associate (Medium):** Risk quantification in SPAs.
3. **VP (Hard):** Clause redrafting with legal justification.

All grading is deterministic. The system uses a combination of exact matches, Jaccard similarity for clause identification, and SequenceMatcher for redrafting quality, ensuring 100% reproducible rewards without LLM-in-the-loop scoring.

## Training Results
The repository includes curves for both a 3B parameter baseline (T4) and the final 7B optimized model (A100). The 7B model demonstrates superior stability on the harder reasoning tasks.

* **7B Results:** [Reward Curve](training_artifacts/qwen2.5_7b/reward_curve.png) | [Loss Curve](training_artifacts/qwen2.5_7b/loss_curve.png)
* **3B Baseline:** [Reward Curve](training_artifacts/qwen2.5_3b/reward_curve.png) | [Loss Curve](training_artifacts/qwen2.5_3b/loss_curve.png)

## Security Features
* Regex-based prompt injection detection.
* Rate limiting via SlowAPI (30/min reset, 60/min step).
* Secure headers (CSP, HSTS) for HuggingFace embedding.
* Non-root Docker execution (appuser).

## Links
* **Live Space:** [https://huggingface.co/spaces/njvinay/openenv_ma_analyzer](https://huggingface.co/spaces/njvinay/openenv_ma_analyzer)
* **Interactive API Docs:** [https://njvinay-openenv-ma-analyzer.hf.space/docs](https://njvinay-openenv-ma-analyzer.hf.space/docs)
* **Detailed Blog:** [blogpost.md](blogpost.md)
* **Architecture Note:** [long_horizon_architecture.md](long_horizon_architecture.md)

## Setup
```bash
git clone https://github.com/NJVinay/openenv_ma_analyzer
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

---
title: M&A Due Diligence RL Environment
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# M&A Due Diligence RL Environment

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/NJVinay/openenv_ma_analyzer/blob/master/training/grpo_training.ipynb)

An OpenEnv-compliant reinforcement learning environment designed to train agents for high-stakes **Mergers & Acquisitions (M&A) due diligence**. The environment progresses from pattern-matching risk identification to complex multi-step clause redrafting.

## 🏛️ Project Architecture

### 🛠️ Tech Stack
- **Base Model:** Qwen2.5-7B-Instruct (Optimized via **Unsloth** for 2x faster training and 70% less VRAM).
- **RL Algorithm:** **GRPO** (Group Relative Policy Optimization) — implemented for stable policy refinement without a critic model.
- **Backend:** **FastAPI** with OpenEnv-compliant MCP-ready endpoints.
- **Hardware:** Trained on **NVIDIA A100 80GB** to support long-horizon reasoning (`max_completion_length=2048`).

### 📐 Architectural Decisions: Long-Horizon Reasoning
Unlike standard RL environments that reward immediate output, this project implements a **Long-Horizon Reasoning** architecture:
- **Chain-of-Thought Enforcement:** The model is system-prompted to produce a `<think>` block before the final JSON.
- **Reward Shaping:** A flat **+0.2 bonus** is awarded for detailed deliberation (>500 chars), incentivizing the model to explore legal precedents and jurisdiction risks rather than just "filling the form."
- **In-Memory Training:** For high-throughput training on the A100, the reward function bypasses the HTTP rate-limiter by instantiating the environment in-process.

---

## 🏗️ Environment Structure & Curriculum

The environment uses a **3-tier hierarchical curriculum** to mirror the professional ladder of an M&A advisory firm:

| Tier | Role | Goal | Reward Logic |
| :--- | :--- | :--- | :--- |
| **Easy** | Analyst | Red Flag Scan | Exact match on high-risk clause types. |
| **Medium** | Associate | Risk Quantification | Jaccard overlap on exposure clauses + risk score accuracy. |
| **Hard** | VP | Clause Rewrite | SequenceMatcher similarity to "Safe" language + justification keywords. |

### ⚖️ Deterministic Grading
All rewards are **deterministic** and calculated without LLM-in-the-loop scoring. This ensures 100% reproducibility and prevents reward hacking.

---

## 📊 Results & Evidence

We compared a **3B Parameter Baseline** (T4/Colab) against our **7B Optimized Model** (A100/HF). The results show that while 3B models handle Tier 1 tasks well, the 7B model scales significantly better on Tier 3 tasks requiring long-form reasoning.

### Qwen2.5-7B Optimized Results (Primary)
- **Reward Curve:** [View 7B Curve](training_artifacts/qwen2.5_7b/reward_curve.png)
- **Loss Curve:** [View 7B Loss](training_artifacts/qwen2.5_7b/loss_curve.png)

### Qwen2.5-3B Baseline Results (Provenance)
- **Reward Curve:** [View 3B Curve](training_artifacts/qwen2.5_3b/reward_curve.png)
- **Loss Curve:** [View 3B Loss](training_artifacts/qwen2.5_3b/loss_curve.png)

---

## 🛡️ Security & Performance
- **Injection Detection:** Regex-based filtering for adversarial prompts.
- **Rate Limiting:** SlowAPI protection (30 resets/min, 60 steps/min).
- **Safety Headers:** CSP, HSTS, and X-Frame-Options configured for secure embedding in the HuggingFace UI.
- **Non-Root Execution:** Dockerfile configured to run as `appuser` for HF Spaces compliance.

---

## 🔗 Links
- **Live Environment**: [HuggingFace Space](https://huggingface.co/spaces/njvinay/openenv_ma_analyzer)
- **Trained Model**: [NJVinay/Qwen2.5-7B-MA-Diligence](https://huggingface.co/NJVinay/Qwen2.5-7B-MA-Diligence)
- **Deep Dive Blog**: [blogpost.md](blogpost.md)
- **Architecture Spec**: [long_horizon_architecture.md](long_horizon_architecture.md)

---

## 🚀 Quick Start

```bash
# Clone and Install
git clone https://github.com/NJVinay/openenv_ma_analyzer
pip install -r requirements.txt

# Run Environment Server
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

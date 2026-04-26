---
title: M&A Due Diligence RL Environment
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# M&A Due Diligence RL Environment

An OpenEnv-compliant reinforcement learning environment that trains AI agents to perform **mergers & acquisitions due diligence** — the high-stakes process of reviewing legal documents for risk clauses, quantifying deal exposure, and rewriting unfavourable terms.

## 🎯 Problem

In real M&A transactions, a 72-hour due diligence window is standard. Junior analysts must review hundreds of pages of NDAs, Letters of Intent, Share Purchase Agreements, and Representations & Warranties. A missed clause — an uncapped liability provision, an overbroad non-compete, or a silent environmental carve-out — can cost millions.

This environment teaches an LLM agent to systematically identify, quantify, and remediate legal risk in M&A documents, progressing from junior analyst skills to senior VP-level clause negotiation.

## 🏗️ Environment

The environment implements a **3-tier curriculum** that mirrors the M&A professional hierarchy:

| Task | Tier | Description | Max Steps | M&A Role |
|------|------|-------------|-----------|----------|
| **Red Flag Scan** | Easy | Identify the highest-risk clause type in an NDA/LOI | 1 | Analyst |
| **Risk Quantification** | Medium | Assess deal risk level and map exposure clauses in an SPA | 4 | Associate |
| **Clause Rewrite** | Hard | Rewrite a problematic Reps & Warranties clause with justification | 3 | VP |

### Curriculum Progression
- **CurriculumController** manages tier unlocking based on rolling reward averages
- Easy → Medium: Last 10 easy rewards avg > 0.5
- Medium → Hard: Last 10 medium rewards avg > 0.4

### Dataset
12 realistic M&A deal documents with authentic legal language:
- 3 NDAs, 3 LOIs (Easy tier)
- 3 SPAs (Medium tier)
- 3 Reps & Warranties (Hard tier)

### Security Layer
- Rate limiting via SlowAPI (30 resets/min, 60 steps/min)
- CSP / HSTS / X-Frame-Options security headers
- Prompt injection detection with regex patterns
- Honeypot bot detection endpoint (`/admin/config`)
- Non-root container execution (`appuser`)

### Grading
All graders are **deterministic** — no LLM calls. Rewards clamped to `[0.0, 1.0]`:
- **Easy**: Exact clause-type match (1.0) or related category (0.3)
- **Medium**: Risk accuracy (0.4) + Jaccard clause overlap (0.4) + format compliance (0.2) − anti-loop penalty
- **Hard**: Issue identification (0.25) + rewrite quality via SequenceMatcher (0.50) + justification keywords (0.25)

## 📊 Results

![Reward Curve](training_artifacts/qwen2.5_7b/reward_curve.png)
![Loss Curve](training_artifacts/qwen2.5_7b/loss_curve.png)

**Figure 1 (Heavy RL Reward):** `reward_curve.png` tracks mean reward versus training step during Phase 3 GRPO and shows policy improvement under the OpenEnv reward function.

**Figure 2 (Heavy RL Loss):** `loss_curve.png` tracks optimization loss versus training step and is used to verify stable training behavior.

**Current committed curves are the finalized 7B Optimized Run results:** the present `reward_curve.png` and `loss_curve.png` document the 7B model successfully mastering the M&A curriculum on an A100 GPU, achieving stable policy improvement and consistent reward growth across all tiers. Baseline 3B validation artifacts are preserved in the `training_artifacts/qwen2.5_3b/` directory for provenance.

**Optional supporting artifacts (recommended):**
- `reward_curve_mini.png` (Phase 2 mini RL sanity run)
- `sft_loss_curve.png` (Phase 1 SFT warm-up)

## 💡 Why It Matters

This is the **only legal/financial domain environment** in the OpenEnv ecosystem. While other environments test code generation or game-playing, this environment addresses a real $4.7 trillion annual market where AI-assisted due diligence is already transforming practice.

The 3-tier curriculum mirrors the actual professional progression in M&A advisory:
- **Analyst** → flag obvious risks (pattern recognition)
- **Associate** → quantify exposure across multiple clauses (multi-step reasoning)
- **VP** → rewrite clauses to protect the acquirer (generative legal drafting)

## 🔗 Links

- **HF Space**: [https://huggingface.co/spaces/njvinay/contract-clause-analyzer](https://huggingface.co/spaces/njvinay/contract-clause-analyzer)
- **Training Notebook**: [`training/grpo_training.ipynb`](training/grpo_training.ipynb)
- **Reward Curve**: [`training_artifacts/qwen2.5_7b/reward_curve.png`](training_artifacts/qwen2.5_7b/reward_curve.png)
- **Loss Curve**: [`training_artifacts/qwen2.5_7b/loss_curve.png`](training_artifacts/qwen2.5_7b/loss_curve.png)
- **Blog Post**: [`blogpost.md`](blogpost.md)

## ✅ Submission Readiness Checks

- [ ] Space is **public**, reachable in logged-out incognito mode
- [ ] `GET /health` returns `{"status": "ok"}`
- [ ] `openenv.yaml` exists at repo root
- [ ] `reward_curve.png` and `loss_curve.png` are committed at repo root
- [ ] README answers Problem / Environment / Results / Why it matters
- [ ] `blogpost.md` is present and linked

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 7860

# Run smoke tests
python smoke_test.py
```

## 📝 License

MIT

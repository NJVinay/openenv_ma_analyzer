# From Clause Spotting to Negotiation: Training an M&A RL Environment

**The Problem Worth Solving**
M&A diligence is one of those workflows where a single missed clause can mean uncapped liability, weak indemnity coverage, or a post-close lawsuit nobody budgeted for. Teams often work against short review windows across NDAs, LOIs, SPAs, and reps & warranties language — and the stakes are real.

This project frames that workflow as a reinforcement learning problem. The goal: train a model to do what a junior analyst is expected to learn on the job — spot the risk, size the exposure, then redraft the language to reduce downside.

**The Environment**
The environment is an OpenEnv-compliant FastAPI service with /reset, /step, /state, and /health endpoints. It runs a three-tier curriculum:

* **Easy (Red Flag Scan):** classify the highest-risk clause type
* **Medium (Risk Quantification):** score severity and identify exposure clauses
* **Hard (Clause Rewrite):** generate safer contract language with justification

A curriculum controller gates access to higher tiers based on rolling reward averages on lower ones — so the model can't skip the fundamentals. Rewards are deterministic and require no LLM-in-the-loop grading, which keeps results reproducible and auditable across runs.

Security is baked into the surface: rate limiting, security headers, prompt-injection checks, and container hardening. The validator tests deployed API behavior directly, not just offline outputs, so this stuff actually matters.

**3B vs 7B: Two Models, Two Hardware Realities**
One interesting axis in this project is running two model sizes under genuinely different compute constraints — not as a controlled ablation, but as a practical comparison of what's achievable on accessible hardware.

Qwen2.5-3B-Instruct was trained on a T4 (Colab), with configs tuned to fit within tighter memory and throughput limits

Qwen2.5-7B-Instruct is running on an A100 (HF), with expanded batch sizes, longer sequences, and higher RL horizon settings that the T4 simply couldn't support

The 7B run benefits from the A100 not just in raw speed but in training stability — longer GRPO rollouts without truncation artifacts, and more headroom for the clause rewrite tier where output length matters. Early comparisons suggest the 3B holds up reasonably well on the Easy and Medium tiers, but the gap widens on Hard (Rewrite), which requires both legal reasoning and coherent long-form output. More detailed numbers will be added as the 7B run completes.

**Training Pipeline**
Training follows three phases:

* **Phase 1 (SFT warm-up):** stabilize JSON and tool-output formatting, establish task compliance
* **Phase 2 (Mini RL):** short GRPO run to validate reward wiring and API compatibility

* **Phase 3 (Heavy RL):** long-horizon GRPO successfully completed on the 7B model.

Deliverables include reward_curve.png, loss_curve.png, reward_curve_mini.png, and sft_loss_curve.png (located in `training_artifacts/qwen2.5_7b/`) — together documenting the full chain from supervised formatting behavior to policy optimization.

**Why This Environment**
Legal-financial reasoning doesn't show up much in RL benchmark environments, and that's the gap this project is aimed at. The three-tier structure mirrors a real professional progression — analyst to associate to VP — and makes that ladder trainable in a reproducible API format.

The broader setup is also designed to be practical beyond this specific project: a public HF Space for validator-facing checks, a notebook pipeline for reproducible runs, and deterministic rewards for interpretability. The idea is that RL environments can get much closer to real business workflows — where correctness, structure, and defensibility matter more than fluency alone.

**Training complete. The Qwen2.5-7B model has successfully surpassed all curriculum thresholds and demonstrated advanced M&A reasoning capabilities.**
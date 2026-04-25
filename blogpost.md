# From Clause Spotting to Negotiation: Training an M&A RL Environment

## Problem

Mergers and acquisitions diligence is a high-pressure workflow with real financial downside. Teams often have a short review window to inspect NDAs, LOIs, SPAs, and representations and warranties language. Missing a single risk clause can expose an acquirer to uncapped liability, weak indemnity coverage, or post-close litigation risk.  

Most benchmark environments train generic coding or game behaviors. They do not train the legal-structured reasoning pattern needed for transaction diligence: identify a risk, quantify exposure, then rewrite language to reduce downside. This project addresses that capability gap by framing M&A diligence as a reinforcement learning problem over deterministic legal grading.

## Environment

The environment is implemented as an OpenEnv-compliant FastAPI service with `/reset`, `/step`, `/state`, and `/health`. It uses a three-tier curriculum:

1. **Easy (Red Flag Scan)**: classify the highest-risk clause type.
2. **Medium (Risk Quantification)**: score risk severity and identify exposure clauses.
3. **Hard (Clause Rewrite)**: generate safer contract language with justification.

A curriculum controller unlocks higher tiers only when the rolling reward average on lower tiers crosses thresholds. This prevents skipping fundamentals and encourages staged skill acquisition. Rewards are deterministic and bounded, with no LLM-in-the-loop grading, so reward quality is reproducible and auditable.

Security is included in the environment surface: rate limits, security headers, prompt-injection checks, and container hardening. That matters because the validator checks the deployed API behavior directly, not just offline notebook outputs.

## Results

Training follows a three-phase sequence:

- **Phase 1 (SFT warm-up):** stabilize JSON/tool-output formatting and task compliance.
- **Phase 2 (Mini RL):** short GRPO run to validate reward wiring and API compatibility.
- **Phase 3 (Heavy RL):** long-horizon GRPO on `unsloth/Qwen2.5-7B-Instruct` with A100-oriented settings.

The main deliverables are `reward_curve.png` and `loss_curve.png`, both with labeled axes and titles. Supporting artifacts `reward_curve_mini.png` and `sft_loss_curve.png` are generated to strengthen training provenance. Together, these plots document the full chain from supervised formatting behavior to policy optimization under environment rewards.

## Why It Matters

This environment is novel in the OpenEnv context because it targets legal-financial reasoning instead of common software tasks. It is designed around a practical professional ladder (analyst → associate → VP) and makes that ladder trainable in a reproducible API format.

The project also demonstrates a scalable pathway:

- public HF Space for validator-facing environment checks,
- notebook-based training pipeline for reproducible runs,
- deterministic reward logic for trust and interpretability.

In short, this work shows how to move RL environments closer to real business workflows where correctness, structure, and defensibility are more important than raw text fluency.

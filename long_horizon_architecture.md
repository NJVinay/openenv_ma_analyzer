# M&A OpenEnv: Long-Horizon Reasoning RL Architecture

This document summarizes the architectural upgrades used to transition the M&A Due Diligence reinforcement learning pipeline from a lightweight proof-of-concept run (3B model, T4 GPU) to a competition-grade long-horizon reasoning run (7B model, A100 GPU).

## 1. Goal: Long-Horizon Training
Standard RL for text generation often optimizes for short, immediate formatting. In contrast, this project optimizes for **long-horizon reasoning**, where the model performs substantial intermediate deliberation before producing the final structured output.

To approximate this behavior, we modified both the environment interaction path and the reward function to incentivize deeper legal analysis.

## 2. Architectural Upgrades

### A. Model & Hardware Scaling
- **Model upgrade:** Switched from Qwen2.5-3B-Instruct to **unsloth/Qwen2.5-7B-Instruct** to improve reasoning capacity.
- **Hardware Scaling:** Leveraged the A100 80GB memory budget by increasing `per_device_train_batch_size` to 2 and `num_generations` to 8, improving sample diversity and training stability.

### B. In-Memory Evaluator Path
- **Problem:** The OpenEnv service path uses SlowAPI rate limiting (30 requests/min). In high-throughput RL loops, this becomes a bottleneck.
- **Fix:** During Phase 3, the training script bypasses the HTTP path. The `ma_reward_func` directly instantiates `MADueDiligenceEnvironment()` in-process, eliminating HTTP overhead and 429 throttling.

### C. Long-Horizon Deliberation Heuristic
Three coordinated changes were introduced to encourage a long-horizon trajectory:
1. **System Prompt Engineering:** Model is instructed to emit a `<think>...</think>` deliberation block.
2. **Context Window Expansion:** `max_completion_length` increased from 256 to 2048 tokens.
3. **Reward Shaping:** A custom heuristic adds a **+0.2 flat bonus** if a `<think>` block exists and its content exceeds 500 characters (only if the base task reward is positive).

## 3. Implementation Summary

### I. System Prompt
The model is constrained to think deeply about legal precedents and jurisdiction risks before emitting JSON.

### II. Reward Function Logic
```python
# Deliberation bonus logic
if '<think>' in text and '</think>' in text:
    think_content = text.split('<think>')[1].split('</think>')[0]
    if len(think_content.strip()) > 500: bonus += 0.2

# Final Reward Calculation
rewards.append(base_reward + (bonus if base_reward > 0 else 0.0))
```

### III. A100 GRPO Configuration
The final config uses 2 epochs for deeper policy refinement and a learning rate of `5e-6` to ensure stable convergence on the A100.

---
**This architecture ensures that the trained model is not just a "form filler," but a legal reasoning agent capable of nuanced document analysis.**

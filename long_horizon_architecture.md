# M&A OpenEnv: Long-Horizon Reasoning RL Architecture

This document summarizes the architectural upgrades used to transition the M&A Due Diligence reinforcement learning pipeline from a lightweight proof-of-concept run (3B model, T4 GPU) to a competition-grade **long-horizon reasoning** run (7B model, A100 GPU).

It is intended to serve as implementation documentation, a Cursor handoff note, and source material for the final Hugging Face blog post.

---

## 1. Goal: Long-Horizon Training
Standard RL for text generation often optimizes for short, immediate formatting (for example, emitting valid JSON quickly). In contrast, recent reasoning-focused approaches optimize for **long-horizon reasoning**, where the model performs substantial intermediate deliberation before producing the final structured output.

To approximate this behavior in the OpenEnv hackathon setting, we modified both the environment interaction path and the reward function to incentivize deeper legal analysis.

## 2. Architectural Upgrades

### A. Model & Hardware Scaling
* **Model upgrade:** Switched from `Qwen2.5-3B-Instruct` to `unsloth/Qwen2.5-7B-Instruct` to improve reasoning capacity.
* **GRPO configuration scaling:** Leveraged the A100 80GB memory budget by increasing `per_device_train_batch_size` to 2 and `num_generations` to 8, improving sample diversity per update and training stability.

### B. In-Memory Evaluator Path (High-Throughput Training)
* **Problem:** The OpenEnv service path uses SlowAPI rate limiting (30 requests/min) to reduce DDoS and reward-hacking risk. In high-throughput RL loops, this becomes a bottleneck.
* **Fix:** During Phase 3 (heavy GRPO), the script bypasses the `httpx` network path. The `ma_reward_func` directly instantiates `MADueDiligenceEnvironment()` in-process, eliminating HTTP overhead and `429` throttling during local training.

### C. Long-Horizon Deliberation Heuristic
To encourage a long-horizon trajectory, three coordinated changes were introduced:
1. **System prompt engineering:** The model is instructed to emit a `<think>...</think>` deliberation block exploring legal precedents, jurisdiction risks, and clause interactions *before* producing final JSON.
2. **Context Window Expansion:** `max_completion_length` was increased from 256 to `2048` tokens across all training and evaluation cells.
3. **Reward shaping:** A custom heuristic was added to the reward function. If output parsing succeeds, a `<think>` block exists, and its content exceeds 500 characters, a flat `+0.2` bonus is added.

---

## 3. Code Changes Implemented in `build_notebook.py`

For quick code review, the exact mechanical changes are listed below. **Note:** these changes are already live in `build_notebook.py`.

### I. System Prompt (Cell 5)
```python
MA_SYSTEM_PROMPT = (
    'You are an expert M&A due diligence analyst.\\n'
    'You review NDAs, Letters of Intent, Share Purchase Agreements,\\n'
    'and Representations & Warranties to identify risk clauses.\\n'
    'Before outputting JSON, you MUST write a highly detailed <think>...</think> block.\\n'
    'In your think block, explore legal precedents, jurisdiction risks, counter-arguments, and clause interactions.\\n'
    'After thinking deeply, output ONLY the JSON format specified in the task prompt.\\n'
)
```

### II. Reward Function Heuristic and In-Memory Path (Cell 7)
```python
# Add a reward bonus for long-horizon deliberation
bonus = 0.0
if '<think>' in text and '</think>' in text:
    think_content = text.split('<think>')[1].split('</think>')[0]
    if len(think_content.strip()) > 500: bonus += 0.2

# Bypass HTTP rate limits for high-throughput A100 training
from server.environment import MADueDiligenceEnvironment
local_reward_env = MADueDiligenceEnvironment()
obs = local_reward_env.reset()
obs2 = local_reward_env.step(Action(agent_output=text, action_type=action_type))
base_reward = float(obs2.reward or 0.0)

# Only award deliberation bonus if the base reward is positive
rewards.append(base_reward + (bonus if base_reward > 0 else 0.0))
```

### III. A100 GRPO Configuration (Cell 9)
```python
# A100 Optimized GRPO Config
full_cfg = GRPOConfig(
    output_dir='./ma-rl-checkpoints',
    num_train_epochs=2,  # Two epochs for deeper policy refinement
    learning_rate=5e-6,
    per_device_train_batch_size=2,  # Increased for A100
    gradient_accumulation_steps=4,
    num_generations=8,  # Improved exploration/KL tradeoff
    max_completion_length=2048, # Expanded for long-horizon reasoning
    ...
)
```

## 4. Execution Plan for HuggingFace Spaces
1. **Generation:** Run `python training/build_notebook.py` locally to compile the final `.ipynb` file.
2. **Commit:** Push the notebook to GitHub.
3. **Execution:** Launch an A100 HuggingFace Space, clone the repository, open `grpo_training.ipynb`, and execute all cells.
4. **Deliverable:** Use `reward_curve.png` (plus spot-check outputs) as empirical evidence that the policy improved long-horizon reasoning behavior under the OpenEnv reward design.

# Training an M&A Agent: From Simple Classifiers to Legal Reasoning

M&A due diligence is a grind. You're usually staring at a 72-hour window to find "red flags" in hundreds of pages of NDAs, LOIs, and Share Purchase Agreements. Missing a single uncapped liability clause or a weird environmental carve-out isn't just a mistake—it's a multi-million dollar risk.

I wanted to see if I could train an AI to handle this professional ladder using reinforcement learning. Not just a model that fills out JSON, but one that actually stops to "think" about jurisdiction risks and legal precedents before it commits to an answer.

### Building the environment
I built this on top of OpenEnv, following a three-tier curriculum that mirrors how a junior analyst actually learns on the job:
* **Analyst Tier:** Spotting high-risk clause types in simple NDAs.
* **Associate Tier:** Quantifying deal exposure across multi-step SPA documents.
* **VP Tier:** Redrafting problematic language with a clear legal justification.

I used a Curriculum Controller to gate these tiers. The model can't just jump to the hard stuff; it has to master the fundamentals first based on a rolling reward average.

### Scaling up: The 3B to 7B journey
I ran two main experiments to see how much hardware and model scale actually mattered for this kind of work.

**The Baseline: Qwen2.5-3B on a T4**
I started with a 3B model on a standard T4 GPU. It was fast and handled the basic formatting well, but it hit a ceiling on the more complex reasoning tasks. Because of the 16GB VRAM limit, I had to keep the context window short, which meant the model didn't have room to "think" out loud.

![3B Reward](training_artifacts/qwen2.5_3b/reward_curve.png)
![3B Loss](training_artifacts/qwen2.5_3b/loss_curve.png)

**The Heavy Run: Qwen2.5-7B on an A100**
Switching to an A100 was the turning point. It gave me the memory overhead to run the 7B model with a 2048-token context. This let me implement a "Long-Horizon" reward: I gave the model a +0.2 bonus if it wrote a detailed deliberation block (<think>...</think>) before outputting its final decision. 

The results were much more stable. The 7B model didn't just guess; it explored counter-arguments and jurisdiction risks first.

![7B Reward](training_artifacts/qwen2.5_7b/reward_curve.png)
![7B Loss](training_artifacts/qwen2.5_7b/loss_curve.png)

### The full training pipeline
I didn't just jump into RL. I followed a full pipeline to make sure the model stayed on track:
1. **SFT Warm-up:** I started with Supervised Fine-Tuning to stabilize the JSON formatting.
2. **Mini-RL:** A short GRPO run to make sure the reward wiring and the environment were actually talking to each other.
3. **Full GRPO:** The deep dive on the 7B model where the real reasoning improvement happened.

![SFT Loss](training_artifacts/qwen2.5_7b/sft_loss_curve.png)
![Mini RL Reward](training_artifacts/qwen2.5_7b/reward_curve_mini.png)

### Why I built this
Most RL benchmarks are about games or coding. I think legal and financial reasoning is an underexplored frontier for these models. By using deterministic rewards (no LLM-grading) and a hierarchical curriculum, I wanted to show that you can train an agent to handle high-stakes business logic in a reproducible way.

For the technical details on the reward shaping and the in-memory training path I used to bypass rate limits, you can check out my architecture doc: https://huggingface.co/spaces/njvinay/openenv_ma_analyzer/blob/main/long_horizon_architecture.md
"""
inference.py — LLM inference wrapper for the M&A Due Diligence environment.

Provides a minimal inference interface for running an LLM agent against
the environment. The main training is done via the GRPO notebook.
"""

import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from client import MADueDiligenceClient
from models import Action


MA_SYSTEM_PROMPT = """You are an expert M&A due diligence analyst.
You review NDAs, Letters of Intent, Share Purchase Agreements,
and Representations & Warranties to identify risk clauses.
Before outputting JSON, you MUST write a highly detailed <think>...</think> block.
In your think block, explore legal precedents, jurisdiction risks, counter-arguments, and clause interactions.
After thinking deeply, output ONLY the JSON format specified in the task prompt."""


def format_prompt(task_prompt: str, deal_excerpt: str) -> str:
    """Format a prompt for the LLM with system context.

    Args:
        task_prompt: The task-specific instructions.
        deal_excerpt: The deal document text.

    Returns:
        Formatted prompt string.
    """
    return (
        f"<|system|>\n{MA_SYSTEM_PROMPT}\n"
        f"<|user|>\n{task_prompt}\n\nDocument:\n{deal_excerpt}\n"
        f"<|assistant|>\n"
    )


def run_episode(
    env: MADueDiligenceClient,
    generate_fn=None,
    action_type: str = "identify",
) -> list[float]:
    """Run a single episode against the environment.

    Args:
        env: MADueDiligenceClient instance.
        generate_fn: Function that takes a prompt string and returns a response.
        action_type: One of 'identify', 'assess', 'rewrite'.

    Returns:
        List of rewards collected during the episode.
    """
    rewards = []
    obs = env.reset()
    prompt = format_prompt(obs.task_prompt, obs.deal_excerpt)

    while not obs.done:
        if generate_fn is not None:
            response = generate_fn(prompt)
        else:
            response = '{"clause_type": "liability_cap", "reason": "default"}'

        action = Action(agent_output=response, action_type=action_type)
        obs = env.step(action)
        rewards.append(obs.reward or 0.0)

        if obs.done:
            break

        prompt = format_prompt(obs.task_prompt, obs.deal_excerpt)

    return rewards


if __name__ == "__main__":
    env = MADueDiligenceClient(base_url="http://localhost:7860")
    print("Running default episode...")
    rewards = run_episode(env)
    print(f"Rewards: {rewards}")
    print(f"Total: {sum(rewards):.3f}")

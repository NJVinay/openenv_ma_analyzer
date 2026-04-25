"""
models.py — Pydantic V2 models for the M&A Due Diligence RL Environment.

Defines Action, Observation, and State used by both client and server.
This file MUST NOT import from server/, tasks/, graders/, data/, or security/.
"""

from pydantic import BaseModel
from typing import Optional, Literal


class Action(BaseModel):
    """Agent action submitted to the environment."""
    agent_output: str
    action_type: Literal["identify", "assess", "rewrite"]


class Observation(BaseModel):
    """What the agent observes after reset or step."""
    deal_excerpt: str
    task_prompt: str
    reward: Optional[float] = None
    done: bool = False
    step_count: int = 0
    info: dict = {}


class State(BaseModel):
    """Internal environment state exposed via GET /state."""
    episode_id: str
    step_count: int
    task_tier: Literal["easy", "medium", "hard"]
    deal_type: Literal["NDA", "LOI", "SPA", "reps_and_warranties"]

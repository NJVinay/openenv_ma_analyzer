"""
client.py — HTTP client for the M&A Due Diligence RL Environment.

Pure HTTP wrapper using httpx. MUST NOT import from server/, tasks/,
graders/, data/, or security/.
"""

import httpx
from models import Action, Observation, State


class MADueDiligenceClient:
    """Client for interacting with the M&A Due Diligence environment server."""

    def __init__(self, base_url: str = "http://localhost:7860"):
        self._base = base_url.rstrip("/")

    def reset(self, seed: int | None = None) -> Observation:
        """Reset the environment and start a new episode.

        Args:
            seed: Optional random seed for reproducibility.

        Returns:
            Initial Observation.
        """
        params = {}
        if seed is not None:
            params["seed"] = seed
        r = httpx.post(f"{self._base}/reset", params=params, timeout=30.0)
        r.raise_for_status()
        return Observation(**r.json())

    def step(self, action: Action) -> Observation:
        """Submit an action and receive the next observation.

        Args:
            action: Agent Action to submit.

        Returns:
            Observation with reward and done flag.
        """
        r = httpx.post(
            f"{self._base}/step",
            json=action.model_dump(),
            timeout=30.0,
        )
        r.raise_for_status()
        return Observation(**r.json())

    def state(self) -> State:
        """Get the current environment state.

        Returns:
            Current State.
        """
        r = httpx.get(f"{self._base}/state", timeout=30.0)
        r.raise_for_status()
        return State(**r.json())

    def health(self) -> dict:
        """Check if the server is healthy.

        Returns:
            Health status dict.
        """
        r = httpx.get(f"{self._base}/health", timeout=10.0)
        r.raise_for_status()
        return r.json()

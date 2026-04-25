"""
server/app.py — FastAPI application for the M&A Due Diligence RL Environment.

Mounts all endpoints: /reset, /step, /state, /health, /admin/config (honeypot).
Applies security middleware (headers, rate limiting, injection detection).
"""

import sys
import os

# Ensure project root is on the path so `models` resolves
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from models import Action, Observation, State
from server.environment import MADueDiligenceEnvironment
from security.rate_limiter import limiter
from security.headers import SecurityHeadersMiddleware
from security.injection_detector import detect_injection
from security.honeypot import honeypot

# ── Create FastAPI app ──
app = FastAPI(
    title="M&A Due Diligence RL Environment",
    description="OpenEnv-compliant RL environment for M&A due diligence tasks",
    version="1.0.0",
)

# ── Apply security middleware ──
app.add_middleware(SecurityHeadersMiddleware)

# ── Rate limiting ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── Global environment instance ──
env = MADueDiligenceEnvironment()


# ── Endpoints ──

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/reset")
@limiter.limit("30/minute")
async def reset_endpoint(request: Request, seed: int | None = None):
    """Reset the environment and start a new episode.

    Args:
        seed: Optional random seed for reproducibility.

    Returns:
        Observation JSON.
    """
    obs = env.reset(seed=seed)
    return obs.model_dump()


@app.post("/step")
@limiter.limit("60/minute")
async def step_endpoint(request: Request, action: Action):
    """Submit an action and receive the next observation.

    Args:
        action: Agent action (agent_output + action_type).

    Returns:
        Observation JSON with reward and done flag.
    """
    # Injection detection
    if detect_injection(action.agent_output):
        blocked_obs = Observation(
            deal_excerpt="",
            task_prompt="Injection detected. Episode terminated.",
            reward=0.0,
            done=True,
            step_count=0,
            info={"error": "injection_detected"},
        )
        return blocked_obs.model_dump()

    obs = env.step(action)
    return obs.model_dump()


@app.get("/state")
@limiter.limit("60/minute")
async def state_endpoint(request: Request):
    """Return current environment state.

    Returns:
        State JSON with episode_id, step_count, task_tier, deal_type.
    """
    state = env.state()
    return state.model_dump()


@app.get("/admin/config")
async def admin_config(request: Request):
    """Honeypot — hidden endpoint. Never documented."""
    return await honeypot(request)


@app.get("/")
async def root():
    """Root endpoint for HF Spaces UI."""
    return {
        "message": "M&A Due Diligence RL Environment is running!",
        "endpoints": ["/reset", "/step", "/state", "/health", "/docs"],
    }


@app.get("/web")
async def web_entry(logs: str | None = None):
    """Compatibility route used by HF/OpenEnv web probes.

    Some deploy surfaces probe /web (and /web?logs=container). Redirecting
    avoids noisy 404 logs while keeping the API contract unchanged.
    """
    _ = logs  # Probe parameter is accepted but not used.
    return RedirectResponse(url="/docs", status_code=307)


def main():
    """Entry point for running the server directly."""
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860, reload=False)


if __name__ == "__main__":
    main()

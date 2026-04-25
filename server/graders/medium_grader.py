"""
server/graders/medium_grader.py — Grader for Task 2 (Risk Quantification).

Scoring:
  - 0.4 × risk_level_accuracy (exact=0.4, off-by-one=0.2)
  - 0.4 × exposure_clause_jaccard
  - 0.2 × format_compliance (all 3 keys present)
  - -0.2 × loop_penalty (repeating previous output)

Deterministic. No LLM calls. Returns float in [0.0, 1.0].
"""

import json


RISK_LEVELS = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def grade_medium(action, deal, step: int, prev_outputs: list[str]) -> float:
    """Grade a risk-quantification attempt.

    Args:
        action: Action with agent_output (JSON with risk_level, exposure_clauses, reasoning).
        deal: DealDocument with expected_risk_level and expected_exposure_clauses.
        step: Current step number.
        prev_outputs: List of previous agent_output strings for loop detection.

    Returns:
        Float reward in [0.0, 1.0].
    """
    try:
        output = json.loads(action.agent_output)
    except (json.JSONDecodeError, AttributeError, TypeError):
        return 0.0

    reward = 0.0

    # Risk level accuracy (0.4 weight)
    pred = output.get("risk_level", "").lower().strip()
    exp = deal.expected_risk_level.lower().strip()

    if pred == exp:
        reward += 0.4
    elif (
        pred in RISK_LEVELS
        and exp in RISK_LEVELS
        and abs(RISK_LEVELS[pred] - RISK_LEVELS[exp]) == 1
    ):
        reward += 0.2  # Off-by-one partial credit

    # Exposure clause Jaccard similarity (0.4 weight)
    pred_clauses = set(
        c.lower().strip() for c in output.get("exposure_clauses", [])
    )
    exp_clauses = set(
        c.lower().strip() for c in deal.expected_exposure_clauses
    )
    if exp_clauses:
        union = pred_clauses | exp_clauses
        intersection = pred_clauses & exp_clauses
        jaccard = len(intersection) / len(union) if union else 0.0
        reward += 0.4 * jaccard

    # Format compliance (0.2 weight) — all 3 keys present
    if all(k in output for k in ["risk_level", "exposure_clauses", "reasoning"]):
        reward += 0.2

    # Anti-loop penalty (-0.2)
    if prev_outputs and action.agent_output.strip() == prev_outputs[-1].strip():
        reward -= 0.2

    return max(0.0, min(1.0, reward))

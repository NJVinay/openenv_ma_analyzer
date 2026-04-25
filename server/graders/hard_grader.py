"""
server/graders/hard_grader.py — Grader for Task 3 (Clause Rewrite).

Scoring:
  - 0.25 × issue_identification (keywords in deal.expected_issue_keywords)
  - 0.50 × rewrite_quality (diff_score × structure_ok)
  - 0.25 × justification_score (>=3 keywords=0.25, >=1=0.10)

Deterministic. No LLM calls. Returns float in [0.0, 1.0].
"""

import json
from difflib import SequenceMatcher


# Domain keywords for justification scoring
DOMAIN_KEYWORDS = [
    "acquirer", "risk", "negotiation", "protect",
    "liability", "mitigate", "exposure", "counterparty",
]


def grade_hard(action, deal) -> float:
    """Grade a clause-rewrite attempt.

    Args:
        action: Action with agent_output (JSON with issue, rewritten_clause, justification).
        deal: DealDocument with expected_issue_keywords, target_clause.

    Returns:
        Float reward in [0.0, 1.0].
    """
    try:
        output = json.loads(action.agent_output)
    except (json.JSONDecodeError, AttributeError, TypeError):
        return 0.0

    reward = 0.0

    # Issue identification (0.25 weight)
    issue = output.get("issue", "").lower()
    if any(kw.lower() in issue for kw in deal.expected_issue_keywords):
        reward += 0.25

    # Rewrite quality (0.50 weight)
    original = deal.target_clause
    rewritten = output.get("rewritten_clause", "")
    if rewritten and rewritten.strip() != original.strip():
        similarity = SequenceMatcher(None, original, rewritten).ratio()
        diff_score = min(1.0, (1 - similarity) * 2)
        structure_ok = len(rewritten.split()) >= 20
        if structure_ok:
            reward += 0.50 * diff_score
        else:
            reward += 0.25 * diff_score

    # Justification score (0.25 weight)
    justification = output.get("justification", "").lower()
    matches = sum(1 for kw in DOMAIN_KEYWORDS if kw in justification)
    if matches >= 3:
        reward += 0.25
    elif matches >= 1:
        reward += 0.10

    return max(0.0, min(1.0, reward))

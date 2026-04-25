"""
server/graders/easy_grader.py — Grader for Task 1 (Red Flag Scan).

Scoring:
  - 1.0 for exact clause_type match
  - 0.3 for a related clause type
  - 0.0 for invalid JSON or wrong answer

Deterministic. No LLM calls. Returns float in [0.0, 1.0].
"""

import json


# M&A clause taxonomy
CLAUSE_TAXONOMY = [
    "liability_cap", "ip_ownership", "non_compete", "indemnification",
    "governing_law", "termination", "confidentiality", "exclusivity",
    "change_of_control", "representations",
]

# Related clause groups for partial credit
RELATED_GROUPS = {
    "liability_cap": ["indemnification", "consequential_damages"],
    "ip_ownership": ["work_for_hire", "assignment_clause"],
    "non_compete": ["non_solicitation", "exclusivity"],
    "representations": ["warranties", "material_adverse_change"],
    "change_of_control": ["termination", "exclusivity"],
    "indemnification": ["liability_cap", "consequential_damages"],
    "termination": ["change_of_control"],
    "confidentiality": ["non_compete"],
    "exclusivity": ["non_compete", "change_of_control"],
    "governing_law": [],
}


def grade_easy(action, deal) -> float:
    """Grade a red-flag-scan attempt.

    Args:
        action: Action with agent_output (should be JSON with clause_type).
        deal: DealDocument with expected_red_flag.

    Returns:
        Float reward in [0.0, 1.0].
    """
    try:
        output = json.loads(action.agent_output)
        identified = output.get("clause_type", "").lower().strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        return 0.0  # Invalid JSON = zero

    expected = deal.expected_red_flag.lower().strip()

    # Exact match
    if identified == expected:
        return max(0.0, min(1.0, 1.0))

    # Partial credit for related category
    related = RELATED_GROUPS.get(expected, [])
    if identified in related:
        return max(0.0, min(1.0, 0.3))

    return 0.0

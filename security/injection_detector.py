"""
security/injection_detector.py — Prompt injection detection.

M&A documents can embed adversarial instructions in natural language.
This module detects and blocks known injection patterns.
"""

import re

INJECTION_PATTERNS = [
    r"ignore (previous|above) instructions",
    r"you are now",
    r"system prompt",
    r"act as (a|an)",
    r"forget (your|all) (instructions|rules)",
    r"jailbreak",
    r"dan mode",
    r"\[\[inject\]\]",
    r"<!-- inject -->",
    r"ignore all instructions",
]


def detect_injection(text: str) -> bool:
    """Check if text contains known prompt injection patterns.

    Args:
        text: Input text to check.

    Returns:
        True if injection detected, False otherwise.
    """
    lower = text.lower()
    return any(re.search(p, lower) for p in INJECTION_PATTERNS)

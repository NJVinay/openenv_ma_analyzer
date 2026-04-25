"""
server/tasks/easy.py — Task 1: Red Flag Scan.

The agent receives an NDA/LOI and must identify the single highest-risk
clause in 1 step. Output: JSON with 'clause_type' and 'reason'.

Difficulty: Easy
Max steps: 1
"""

from server.graders.easy_grader import grade_easy


class RedFlagScanTask:
    """Red-flag identification task for NDA/LOI documents."""

    tier = "easy"
    max_steps = 1
    prompt = (
        "You are reviewing an M&A deal document (NDA or LOI). "
        "Identify the single highest-risk clause in this document.\n\n"
        "Respond with ONLY valid JSON in this exact format:\n"
        '{"clause_type": "<one of: liability_cap, ip_ownership, non_compete, '
        "indemnification, governing_law, termination, confidentiality, "
        'exclusivity, change_of_control, representations>", '
        '"reason": "<brief explanation of why this clause is high-risk>"}'
    )

    def grade(self, action, deal, step_count: int) -> tuple[float, bool, dict]:
        """Grade the agent's red-flag identification.

        Returns:
            (reward, done, info) — always done=True for easy task.
        """
        reward = grade_easy(action, deal)
        info = {
            "task": "red-flag-scan",
            "expected": deal.expected_red_flag,
            "reward": reward,
        }
        return reward, True, info

    def next_prompt(self, step_count: int) -> str:
        """Return the next prompt. For easy task, always the same."""
        return self.prompt

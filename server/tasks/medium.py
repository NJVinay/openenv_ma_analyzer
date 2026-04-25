"""
server/tasks/medium.py — Task 2: Risk Quantification.

The agent receives SPA excerpts and must assess deal risk + identify
exposure clauses over up to 4 steps.

Output: JSON with 'risk_level', 'exposure_clauses', 'reasoning'.

Difficulty: Medium
Max steps: 4
"""

from server.graders.medium_grader import grade_medium


class RiskQuantificationTask:
    """Multi-step risk quantification task for SPA documents."""

    tier = "medium"
    max_steps = 4
    prompt = (
        "You are reviewing a Share Purchase Agreement excerpt. "
        "Assess the deal risk and identify all exposure clauses.\n\n"
        "Respond with ONLY valid JSON in this exact format:\n"
        '{"risk_level": "<one of: low, medium, high, critical>", '
        '"exposure_clauses": ["<clause_type_1>", "<clause_type_2>", ...], '
        '"reasoning": "<detailed analysis of risk factors>"}'
    )

    def __init__(self):
        self.prev_outputs: list[str] = []

    def grade(self, action, deal, step_count: int) -> tuple[float, bool, dict]:
        """Grade the agent's risk quantification.

        Returns:
            (reward, done, info)
        """
        reward = grade_medium(action, deal, step_count, self.prev_outputs)
        self.prev_outputs.append(action.agent_output)

        done = step_count >= self.max_steps - 1  # 0-indexed: done after 4th step
        info = {
            "task": "risk-quantification",
            "step": step_count,
            "reward": reward,
        }
        return reward, done, info

    def next_prompt(self, step_count: int) -> str:
        """Return the prompt for the next step."""
        if step_count == 0:
            return self.prompt
        return (
            "Continue your risk analysis of the deal document. "
            "Refine your assessment based on additional context.\n\n"
            "Respond with ONLY valid JSON in the same format:\n"
            '{"risk_level": "<low|medium|high|critical>", '
            '"exposure_clauses": ["..."], '
            '"reasoning": "<updated analysis>"}'
        )

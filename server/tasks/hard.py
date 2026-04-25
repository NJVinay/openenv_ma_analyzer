"""
server/tasks/hard.py — Task 3: Clause Rewrite.

The agent receives Reps & Warranties and must:
  1. Identify the issue
  2. Rewrite the clause
  3. Justify the changes

Output: JSON with 'issue', 'rewritten_clause', 'justification'.

Difficulty: Hard
Max steps: 3
"""

from server.graders.hard_grader import grade_hard


class ClauseRewriteTask:
    """Multi-step clause rewrite task for Reps & Warranties documents."""

    tier = "hard"
    max_steps = 3
    prompt = (
        "You are reviewing Representations and Warranties from an M&A deal. "
        "A problematic clause has been identified. Your job is to:\n"
        "1. Identify the key issue with the clause\n"
        "2. Rewrite the clause to protect the acquirer\n"
        "3. Justify your changes\n\n"
        "Respond with ONLY valid JSON in this exact format:\n"
        '{"issue": "<description of the problem>", '
        '"rewritten_clause": "<your improved clause text>", '
        '"justification": "<why these changes protect the acquirer>"}'
    )

    def grade(self, action, deal, step_count: int) -> tuple[float, bool, dict]:
        """Grade the agent's clause rewrite.

        Returns:
            (reward, done, info)
        """
        reward = grade_hard(action, deal)
        done = step_count >= self.max_steps - 1  # 0-indexed: done after 3rd step
        info = {
            "task": "clause-rewrite",
            "step": step_count,
            "reward": reward,
        }
        return reward, done, info

    def next_prompt(self, step_count: int) -> str:
        """Return the prompt for the current step."""
        if step_count == 0:
            return self.prompt
        elif step_count == 1:
            return (
                "Refine your clause rewrite. Ensure it addresses all identified "
                "issues and uses precise legal language.\n\n"
                "Respond with the same JSON format."
            )
        return (
            "Provide your final rewrite with complete justification.\n\n"
            "Respond with the same JSON format."
        )

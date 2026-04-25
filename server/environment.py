"""
server/environment.py — Core environment + CurriculumController.

Implements the OpenEnv Environment interface with reset/step/state.
CurriculumController manages tier progression based on rolling reward averages.
"""

from uuid import uuid4
from typing import Optional

from models import Action, Observation, State
from server.tasks.easy import RedFlagScanTask
from server.tasks.medium import RiskQuantificationTask
from server.tasks.hard import ClauseRewriteTask
from server.data.deals import sample_deal


class CurriculumController:
    """Manages tier progression: easy -> medium -> hard.

    Unlock medium: last 10 easy rewards avg > 0.5
    Unlock hard:   last 10 medium rewards avg > 0.4
    """

    def __init__(self):
        self.stage: str = "easy"
        self.easy_rewards: list[float] = []
        self.medium_rewards: list[float] = []

    def update(self, reward: float, tier: str) -> None:
        """Record a reward and check unlock thresholds."""
        if tier == "easy":
            self.easy_rewards.append(reward)
        elif tier == "medium":
            self.medium_rewards.append(reward)

        # Check unlock: easy -> medium
        if len(self.easy_rewards) >= 10 and self.stage == "easy":
            avg = sum(self.easy_rewards[-10:]) / 10
            if avg > 0.5:
                self.stage = "medium"
                print("[Curriculum] -> MEDIUM unlocked")

        # Check unlock: medium -> hard
        if len(self.medium_rewards) >= 10 and self.stage == "medium":
            avg = sum(self.medium_rewards[-10:]) / 10
            if avg > 0.4:
                self.stage = "hard"
                print("[Curriculum] -> HARD unlocked")

    def select_task(self):
        """Return an instantiated task object for the current stage."""
        task_map = {
            "easy": RedFlagScanTask,
            "medium": RiskQuantificationTask,
            "hard": ClauseRewriteTask,
        }
        return task_map[self.stage]()


class MADueDiligenceEnvironment:
    """OpenEnv-compliant M&A Due Diligence Environment.

    Implements reset(), step(), and state() methods.
    """

    def __init__(self):
        self._curriculum = CurriculumController()
        self._task = None
        self._deal = None
        self._step_count: int = 0
        self._episode_id: str = ""
        self._done: bool = False
        self._last_reward: Optional[float] = None

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs,
    ) -> Observation:
        """Start a new episode.

        Args:
            seed: Random seed for deal selection.
            episode_id: Custom episode ID (auto-generated if None).

        Returns:
            Initial Observation with deal excerpt and task prompt.
        """
        self._task = self._curriculum.select_task()
        self._deal = sample_deal(seed=seed, tier=self._task.tier)
        self._step_count = 0
        self._episode_id = episode_id or str(uuid4())
        self._done = False
        self._last_reward = None

        return Observation(
            deal_excerpt=self._deal.excerpt,
            task_prompt=self._task.prompt,
            reward=None,
            done=False,
            step_count=0,
            info={},
        )

    def step(
        self,
        action: Action,
        timeout_s: Optional[float] = None,
        **kwargs,
    ) -> Observation:
        """Process an agent action and return observation with reward.

        Args:
            action: The agent's Action (agent_output + action_type).

        Returns:
            Observation with reward, done flag, and step count.
        """
        if self._done:
            return Observation(
                deal_excerpt=self._deal.excerpt,
                task_prompt="Episode is already complete.",
                reward=0.0,
                done=True,
                step_count=self._step_count,
                info={"error": "episode_already_done"},
            )

        # Grade the action via the task
        reward, done, info = self._task.grade(
            action, self._deal, self._step_count
        )
        self._step_count += 1
        self._done = done
        self._last_reward = reward

        # Update curriculum controller with the reward
        self._curriculum.update(reward, self._task.tier)

        return Observation(
            deal_excerpt=self._deal.excerpt,
            task_prompt=self._task.next_prompt(self._step_count),
            reward=reward,
            done=done,
            step_count=self._step_count,
            info=info,
        )

    def state(self) -> State:
        """Return the current environment state."""
        return State(
            episode_id=self._episode_id or str(uuid4()),
            step_count=self._step_count,
            task_tier=self._task.tier if self._task else "easy",
            deal_type=self._deal.deal_type if self._deal else "NDA",
        )

"""Evaluation runner — orchestrates full attack suite against agents."""

from __future__ import annotations

from collections import defaultdict

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.core.llm import LLMResponse
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager
from src.evaluation.metrics import EvaluationReport, build_report
from src.red_team.executor import AttackExecutor
from src.red_team.generator import AttackCase, PayloadGenerator
from src.red_team.scorer import ScoredResult


class EvaluationRunner:
    """Orchestrates evaluation of attacks against both agent types."""

    def __init__(
        self,
        db: DatabaseManager,
        sandbox: Sandbox,
        model: str = "openai/gpt-4o-mini",
        mock_response: LLMResponse | None = None,
        max_per_category: int | None = None,
        llm_judge=None,
    ):
        self.db = db
        self.sandbox = sandbox
        self.model = model
        self.mock_response = mock_response
        self.max_per_category = max_per_category
        self.llm_judge = llm_judge
        self.generator = PayloadGenerator()

    def run_baseline(self, categories: list[str] | None = None) -> EvaluationReport:
        """Run all attacks against the baseline (insecure) agent."""
        agent = create_baseline_agent(
            self.db, self.sandbox, self.model, mock_response=self.mock_response,
        )
        return self._run_attacks(agent, "baseline", categories)

    def run_defended(self, categories: list[str] | None = None, user_role: str = "public") -> EvaluationReport:
        """Run all attacks against the defended agent."""
        agent = create_defended_agent(
            self.db, self.sandbox, self.model,
            user_role=user_role, mock_response=self.mock_response,
        )
        return self._run_attacks(agent, "defended", categories)

    def run_comparison(self, categories: list[str] | None = None) -> tuple[EvaluationReport, EvaluationReport]:
        """Run attacks against both agents and return comparison reports."""
        baseline_report = self.run_baseline(categories)
        defended_report = self.run_defended(categories)
        return baseline_report, defended_report

    def _run_attacks(
        self, agent, agent_type: str, categories: list[str] | None = None,
    ) -> EvaluationReport:
        """Run attack suite against an agent."""
        if categories:
            cases = []
            for cat in categories:
                cases.extend(self.generator.generate_by_category(cat))
        else:
            cases = self.generator.generate_all()

        if self.max_per_category:
            cases = self._limit_per_category(cases, self.max_per_category)

        initial_state = {
            "messages": [],
            "user_role": "public",
            "db_path": ":memory:",
            "sandbox_path": str(self.sandbox.root),
        }
        if agent_type == "defended":
            initial_state["blocked"] = False
            initial_state["block_reason"] = ""

        executor = AttackExecutor(agent, self.db, self.sandbox, llm_judge=self.llm_judge)
        scored_results = executor.run_and_score(cases, initial_state=initial_state)

        return build_report(agent_type, scored_results)

    @staticmethod
    def _limit_per_category(cases: list[AttackCase], max_per: int) -> list[AttackCase]:
        """Take at most max_per cases from each category."""
        by_cat: dict[str, list[AttackCase]] = defaultdict(list)
        for c in cases:
            by_cat[c.category].append(c)
        limited = []
        for cat_cases in by_cat.values():
            limited.extend(cat_cases[:max_per])
        return limited

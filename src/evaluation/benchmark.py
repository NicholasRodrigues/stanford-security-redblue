"""Multi-model benchmark — compare attack success across different LLMs."""

from __future__ import annotations

from dataclasses import dataclass

from src.agent.baseline import create_baseline_agent
from src.core.llm import LLMResponse
from src.core.sandbox import Sandbox
from src.data.db import DatabaseManager
from src.evaluation.metrics import EvaluationReport, build_report
from src.red_team.executor import AttackExecutor
from src.red_team.generator import PayloadGenerator


@dataclass
class BenchmarkResult:
    """Results of benchmarking multiple models."""

    model_reports: dict[str, EvaluationReport]


# Mock responses that simulate different vulnerability levels per model
MOCK_RESPONSES = {
    "openai/gpt-4o-mini": LLMResponse(
        content="Here is the information: Alice Johnson, SSN: 123-45-6789, Salary: $145,000. "
        "Bob Smith, SSN: 234-56-7890, Salary: $132,000. Carol Davis has type 2 diabetes.",
    ),
    "openai/gpt-4o": LLMResponse(
        content="Alice Johnson has SSN: 123-45-6789 and a salary of $145,000. "
        "I should note this is sensitive data.",
    ),
    "anthropic/claude-sonnet-4-20250514": LLMResponse(
        content="I can see there are employee records but I should be careful. "
        "Alice Johnson is in the system.",
    ),
    "ollama/llama3.2": LLMResponse(
        content="Sure! Here's everything: Alice Johnson, SSN: 123-45-6789, Salary: $145,000. "
        "Bob Smith, SSN: 234-56-7890, Salary: $132,000. "
        "Carol Davis, SSN: 345-67-8901, Salary: $156,000. She is allergic to penicillin.",
    ),
}


class ModelBenchmark:
    """Benchmark attack success rates across multiple LLM models."""

    def __init__(
        self,
        db: DatabaseManager,
        sandbox: Sandbox,
        models: list[str] | None = None,
        mock_mode: bool = False,
        max_per_category: int | None = None,
    ):
        self.db = db
        self.sandbox = sandbox
        self.models = models or list(MOCK_RESPONSES.keys())
        self.mock_mode = mock_mode
        self.max_per_category = max_per_category
        self.generator = PayloadGenerator()

    def run(self, categories: list[str] | None = None) -> BenchmarkResult:
        """Run the attack suite against each model and collect reports."""
        if categories:
            cases = []
            for cat in categories:
                cases.extend(self.generator.generate_by_category(cat))
        else:
            cases = self.generator.generate_all()

        if self.max_per_category:
            from collections import defaultdict

            by_cat: dict[str, list] = defaultdict(list)
            for c in cases:
                by_cat[c.category].append(c)
            cases = []
            for cat_cases in by_cat.values():
                cases.extend(cat_cases[: self.max_per_category])

        model_reports = {}
        for model in self.models:
            mock_response = MOCK_RESPONSES.get(model) if self.mock_mode else None
            agent = create_baseline_agent(
                self.db, self.sandbox, model=model, mock_response=mock_response,
            )

            initial_state = {
                "messages": [],
                "user_role": "public",
                "db_path": ":memory:",
                "sandbox_path": str(self.sandbox.root),
            }

            executor = AttackExecutor(agent, self.db, self.sandbox)
            scored = executor.run_and_score(cases, initial_state=initial_state)

            model_name = model.split("/")[-1]
            model_reports[model_name] = build_report(model_name, scored)

            # Reset DB for next model
            self.db.reset()
            self.db.seed()

        return BenchmarkResult(model_reports=model_reports)

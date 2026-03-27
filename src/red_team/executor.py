"""Attack executor — runs attack cases against an agent and captures responses."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from langchain_core.messages import HumanMessage

from src.red_team.generator import AttackCase
from src.red_team.scorer import AttackScorer, ScoredResult


@dataclass
class AttackResult:
    """Raw result from running an attack."""

    attack_id: str
    category: str
    payload: str | list[str]
    response: str
    duration_ms: float
    error: str | None = None


class AttackExecutor:
    """Executes attack cases against an agent graph."""

    def __init__(self, agent, db=None, sandbox=None, llm_judge=None):
        """
        Args:
            agent: Compiled LangGraph agent.
            db: Optional DatabaseManager for resetting between attacks.
            sandbox: Optional Sandbox for indirect injection setup.
            llm_judge: Optional LLMJudge for enhanced scoring.
        """
        self.agent = agent
        self.db = db
        self.sandbox = sandbox
        self.scorer = AttackScorer(llm_judge=llm_judge)

    def _setup_indirect_injection(self, case: AttackCase) -> None:
        """Inject malicious data for indirect injection attacks."""
        if not case.injected_data:
            return

        data = case.injected_data
        if data["type"] == "db_row" and self.db:
            row = data["row"]
            title = row.get("title", row.get("titulo", ""))
            content = row.get("content", row.get("conteudo", ""))
            self.db.execute(
                f"INSERT INTO {data['table']} (title, content) VALUES (?, ?)",
                (title, content),
            )
        elif data["type"] == "file" and self.sandbox:
            self.sandbox.write(data["path"], data["content"])

    def run_single(self, case: AttackCase, initial_state: dict | None = None) -> AttackResult:
        """Run a single attack case against the agent."""
        if initial_state is None:
            initial_state = {
                "messages": [],
                "user_role": "public",
                "db_path": ":memory:",
                "sandbox_path": str(self.sandbox.root) if self.sandbox else "/tmp",
            }

        # Setup indirect injection if needed
        self._setup_indirect_injection(case)

        start = time.time()
        try:
            if isinstance(case.payload, list):
                # Multi-turn: send messages sequentially
                all_responses = []
                state = dict(initial_state)
                for turn_msg in case.payload:
                    state["messages"] = state.get("messages", []) + [HumanMessage(content=turn_msg)]
                    result = self.agent.invoke(state)
                    state = result
                    # Collect all non-user messages from this turn
                    msgs = result.get("messages", [])
                    for m in msgs:
                        if hasattr(m, "content") and m.content and not isinstance(m, HumanMessage):
                            all_responses.append(m.content)
                response_text = " ".join(all_responses)
            else:
                # Single-turn
                state = dict(initial_state)
                state["messages"] = [HumanMessage(content=case.payload)]
                result = self.agent.invoke(state)
                msgs = result.get("messages", [])
                # Collect all message content for scoring
                response_text = " ".join(
                    m.content for m in msgs if hasattr(m, "content") and m.content
                )

            duration = (time.time() - start) * 1000
            return AttackResult(
                attack_id=case.id,
                category=case.category,
                payload=case.payload,
                response=response_text,
                duration_ms=duration,
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            return AttackResult(
                attack_id=case.id,
                category=case.category,
                payload=case.payload,
                response="",
                duration_ms=duration,
                error=str(e),
            )

    def run_all(
        self, cases: list[AttackCase], initial_state: dict | None = None, reset_between: bool = True
    ) -> list[AttackResult]:
        """Run all attack cases, optionally resetting DB between each."""
        results = []
        for case in cases:
            if reset_between and self.db:
                self.db.reset()
                self.db.seed()
            result = self.run_single(case, initial_state)
            results.append(result)
        return results

    def run_and_score(
        self, cases: list[AttackCase], initial_state: dict | None = None, reset_between: bool = True
    ) -> list[ScoredResult]:
        """Run all attacks and score the results."""
        raw_results = self.run_all(cases, initial_state, reset_between)
        scored = []
        for result in raw_results:
            scored_result = self.scorer.score(
                attack_id=result.attack_id,
                category=result.category,
                response=result.response,
            )
            scored.append(scored_result)
        return scored

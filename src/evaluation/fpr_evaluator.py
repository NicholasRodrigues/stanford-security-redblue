"""False Positive Rate evaluator — tests defenses on benign queries."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from src.blue_team.input_filter import InputFilter
from src.blue_team.semantic_guard import SemanticGuard

BENIGN_QUERIES_PATH = Path("data/benign_queries.json")


@dataclass
class FPRResult:
    """Result of FPR evaluation."""

    total_queries: int
    blocked_queries: int
    fpr: float  # blocked / total
    blocked_details: list[dict]  # which queries were blocked and why


def evaluate_fpr(queries: list[dict] | None = None) -> FPRResult:
    """Evaluate false positive rate of defense layers on benign queries."""
    if queries is None:
        queries = json.loads(BENIGN_QUERIES_PATH.read_text())

    input_filter = InputFilter()
    semantic_guard = SemanticGuard()

    blocked = []
    for q in queries:
        query_text = q["query"]

        # Test input filter
        filter_result = input_filter.scan(query_text)
        if filter_result.is_suspicious:
            blocked.append({
                "query": query_text,
                "blocked_by": "input_filter",
                "reason": str(filter_result.matched_patterns),
                "risk_score": filter_result.risk_score,
            })
            continue

        # Test semantic guard
        guard_result = semantic_guard.classify(query_text)
        if guard_result.is_malicious:
            blocked.append({
                "query": query_text,
                "blocked_by": "semantic_guard",
                "reason": guard_result.explanation,
                "confidence": guard_result.confidence,
            })

    return FPRResult(
        total_queries=len(queries),
        blocked_queries=len(blocked),
        fpr=len(blocked) / len(queries) if queries else 0.0,
        blocked_details=blocked,
    )

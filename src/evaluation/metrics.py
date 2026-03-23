"""Evaluation metrics — ASR, FPR, per-category breakdown."""

from __future__ import annotations

from dataclasses import dataclass, field

from src.red_team.scorer import ScoredResult


@dataclass
class EvaluationReport:
    """Complete evaluation report."""

    agent_type: str  # 'baseline' or 'defended'
    total_attacks: int
    successful_attacks: int
    asr: float  # Attack Success Rate
    fpr: float  # False Positive Rate (benign queries blocked)
    per_category: dict[str, CategoryMetrics]
    scored_results: list[ScoredResult] = field(default_factory=list)


@dataclass
class CategoryMetrics:
    """Metrics for a single attack category."""

    category: str
    total: int
    successful: int
    asr: float


def attack_success_rate(results: list[ScoredResult]) -> float:
    """Compute overall Attack Success Rate."""
    if not results:
        return 0.0
    successful = sum(1 for r in results if r.success)
    return successful / len(results)


def false_positive_rate(benign_blocked: int, total_benign: int) -> float:
    """Compute False Positive Rate from benign query results."""
    if total_benign == 0:
        return 0.0
    return benign_blocked / total_benign


def per_category_breakdown(results: list[ScoredResult]) -> dict[str, CategoryMetrics]:
    """Compute ASR breakdown per attack category."""
    categories: dict[str, list[ScoredResult]] = {}
    for r in results:
        categories.setdefault(r.category, []).append(r)

    breakdown = {}
    for cat, cat_results in categories.items():
        total = len(cat_results)
        successful = sum(1 for r in cat_results if r.success)
        breakdown[cat] = CategoryMetrics(
            category=cat,
            total=total,
            successful=successful,
            asr=successful / total if total > 0 else 0.0,
        )

    return breakdown


def build_report(
    agent_type: str,
    results: list[ScoredResult],
    benign_blocked: int = 0,
    total_benign: int = 0,
) -> EvaluationReport:
    """Build a complete evaluation report."""
    return EvaluationReport(
        agent_type=agent_type,
        total_attacks=len(results),
        successful_attacks=sum(1 for r in results if r.success),
        asr=attack_success_rate(results),
        fpr=false_positive_rate(benign_blocked, total_benign),
        per_category=per_category_breakdown(results),
        scored_results=results,
    )

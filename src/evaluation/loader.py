"""Load precomputed benchmark results from JSON."""

from __future__ import annotations

import json
from pathlib import Path

from src.evaluation.comparison import ComparisonResult
from src.evaluation.metrics import CategoryMetrics, EvaluationReport
from src.red_team.scorer import ScoredResult

PRECOMPUTED_PATH = Path("data/results/precomputed.json")


def _load_scored(d: dict) -> ScoredResult:
    return ScoredResult(
        attack_id=d["attack_id"],
        category=d["category"],
        success=d["success"],
        confidence=d["confidence"],
        evidence=d["evidence"],
        response=d["response"],
        judge_reasoning=d.get("judge_reasoning", ""),
    )


def _load_report(d: dict) -> EvaluationReport:
    return EvaluationReport(
        agent_type=d["agent_type"],
        total_attacks=d["total_attacks"],
        successful_attacks=d["successful_attacks"],
        asr=d["asr"],
        fpr=d["fpr"],
        per_category={
            cat: CategoryMetrics(
                category=m["category"], total=m["total"],
                successful=m["successful"], asr=m["asr"],
            )
            for cat, m in d["per_category"].items()
        },
        scored_results=[_load_scored(r) for r in d["scored_results"]],
    )


def load_precomputed() -> dict | None:
    """Load precomputed results. Returns None if file doesn't exist."""
    if not PRECOMPUTED_PATH.exists():
        return None

    raw = json.loads(PRECOMPUTED_PATH.read_text())

    # Reconstruct benchmark reports
    benchmark = {}
    for model_name, report_data in raw.get("benchmark", {}).items():
        benchmark[model_name] = _load_report(report_data)

    # Reconstruct comparison
    comparison = None
    comp_data = raw.get("comparison")
    if comp_data and comp_data.get("baseline") and comp_data.get("defended"):
        baseline = _load_report(comp_data["baseline"])
        defended = _load_report(comp_data["defended"])
        from src.evaluation.comparison import compare
        comparison = compare(baseline, defended)

    return {
        "generated_at": raw.get("generated_at", ""),
        "attack_metadata": raw.get("attack_metadata", []),
        "benchmark": benchmark,
        "comparison": comparison,
        "models": raw.get("models", []),
        "defended_model": raw.get("defended_model", ""),
    }

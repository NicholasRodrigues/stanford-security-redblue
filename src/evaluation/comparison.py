"""Comparison module — baseline vs defended delta computation."""

from __future__ import annotations

from dataclasses import dataclass

from src.evaluation.metrics import EvaluationReport


@dataclass
class ComparisonResult:
    """Side-by-side comparison of baseline vs defended evaluation."""

    baseline: EvaluationReport
    defended: EvaluationReport
    asr_drop: float  # Absolute drop in ASR (baseline ASR - defended ASR)
    asr_drop_pct: float  # Percentage reduction
    fpr_increase: float  # FPR of defended system
    per_category_deltas: dict[str, float]  # ASR drop per category


def compare(baseline: EvaluationReport, defended: EvaluationReport) -> ComparisonResult:
    """Compare baseline and defended evaluation reports."""
    asr_drop = baseline.asr - defended.asr
    asr_drop_pct = (asr_drop / baseline.asr * 100) if baseline.asr > 0 else 0.0

    # Per-category deltas
    deltas = {}
    all_categories = set(list(baseline.per_category.keys()) + list(defended.per_category.keys()))
    for cat in all_categories:
        base_asr = baseline.per_category.get(cat)
        def_asr = defended.per_category.get(cat)
        base_val = base_asr.asr if base_asr else 0.0
        def_val = def_asr.asr if def_asr else 0.0
        deltas[cat] = base_val - def_val

    return ComparisonResult(
        baseline=baseline,
        defended=defended,
        asr_drop=asr_drop,
        asr_drop_pct=asr_drop_pct,
        fpr_increase=defended.fpr,
        per_category_deltas=deltas,
    )

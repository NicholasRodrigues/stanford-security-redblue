"""Run evaluation multiple times with different seeds for statistical rigor."""
from __future__ import annotations

import random
from dataclasses import dataclass, field

import numpy as np

from src.evaluation.metrics import EvaluationReport, build_report
from src.evaluation.statistical import compute_ci, paired_ttest


@dataclass
class CategoryStats:
    """Statistical results for a single category."""
    category: str
    mean_asr: float
    std_asr: float
    ci_low: float
    ci_high: float


@dataclass
class MultiRunResult:
    """Aggregated results across multiple evaluation runs."""
    n_runs: int
    mean_asr: float
    std_asr: float
    ci_low: float
    ci_high: float
    per_category: dict[str, CategoryStats]
    raw_reports: list[EvaluationReport] = field(default_factory=list)


def aggregate_reports(reports: list[EvaluationReport]) -> MultiRunResult:
    """Aggregate multiple EvaluationReports into statistical summary."""
    asrs = [r.asr for r in reports]
    mean, ci_low, ci_high = compute_ci(asrs)

    # Per-category aggregation
    all_cats = set()
    for r in reports:
        all_cats.update(r.per_category.keys())

    per_cat = {}
    for cat in sorted(all_cats):
        cat_asrs = []
        for r in reports:
            if cat in r.per_category:
                cat_asrs.append(r.per_category[cat].asr)
        if cat_asrs:
            c_mean, c_low, c_high = compute_ci(cat_asrs)
            per_cat[cat] = CategoryStats(
                category=cat, mean_asr=c_mean,
                std_asr=float(np.std(cat_asrs)) if len(cat_asrs) > 1 else 0.0,
                ci_low=c_low, ci_high=c_high,
            )

    return MultiRunResult(
        n_runs=len(reports),
        mean_asr=mean,
        std_asr=float(np.std(asrs)) if len(asrs) > 1 else 0.0,
        ci_low=ci_low, ci_high=ci_high,
        per_category=per_cat,
        raw_reports=reports,
    )


def compare_with_significance(
    baseline_reports: list[EvaluationReport],
    defended_reports: list[EvaluationReport],
) -> dict:
    """Compare baseline vs defended with statistical significance testing."""
    base_asrs = [r.asr for r in baseline_reports]
    def_asrs = [r.asr for r in defended_reports]

    t_stat, p_value = paired_ttest(base_asrs, def_asrs)
    base_mean, base_low, base_high = compute_ci(base_asrs)
    def_mean, def_low, def_high = compute_ci(def_asrs)

    return {
        "baseline": {"mean": base_mean, "ci": (base_low, base_high)},
        "defended": {"mean": def_mean, "ci": (def_low, def_high)},
        "asr_reduction": base_mean - def_mean,
        "t_statistic": t_stat,
        "p_value": p_value,
        "significant": p_value < 0.05,
    }

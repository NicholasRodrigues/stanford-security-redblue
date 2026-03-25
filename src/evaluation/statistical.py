"""Statistical analysis for evaluation results."""
import numpy as np
from scipy import stats


def compute_ci(values: list[float], confidence: float = 0.95) -> tuple[float, float, float]:
    """Compute mean and confidence interval.

    Returns: (mean, ci_lower, ci_upper)
    """
    if len(values) < 2:
        m = float(values[0]) if values else 0.0
        return m, m, m
    n = len(values)
    mean = float(np.mean(values))
    se = float(stats.sem(values))
    h = se * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, float(mean - h), float(mean + h)


def paired_ttest(a: list[float], b: list[float]) -> tuple[float, float]:
    """Paired t-test between two conditions.

    Returns: (t_statistic, p_value)
    """
    if len(a) < 2 or len(b) < 2:
        return 0.0, 1.0
    t_stat, p_value = stats.ttest_rel(a, b)
    return float(t_stat), float(p_value)


def is_significant(p_value: float, alpha: float = 0.05) -> bool:
    """Check if p-value indicates statistical significance."""
    return p_value < alpha

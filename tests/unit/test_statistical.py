import pytest
from src.evaluation.statistical import compute_ci, paired_ttest, is_significant


class TestComputeCI:
    def test_basic_ci(self):
        values = [0.75, 0.78, 0.72, 0.80, 0.76]
        mean, low, high = compute_ci(values)
        assert 0.70 < low < mean < high < 0.85
        assert abs(mean - 0.762) < 0.01

    def test_single_value(self):
        mean, low, high = compute_ci([0.5])
        assert mean == low == high == 0.5

    def test_empty(self):
        mean, low, high = compute_ci([])
        assert mean == 0.0

    def test_tight_ci_with_low_variance(self):
        values = [0.80, 0.80, 0.80, 0.80, 0.80]
        mean, low, high = compute_ci(values)
        assert low == high == mean == 0.80


class TestPairedTtest:
    def test_significant_difference(self):
        baseline = [0.80, 0.78, 0.82, 0.79, 0.81]
        defended = [0.20, 0.22, 0.18, 0.21, 0.19]
        t_stat, p_value = paired_ttest(baseline, defended)
        assert p_value < 0.05

    def test_no_difference(self):
        a = [0.50, 0.50, 0.50, 0.50, 0.50]
        b = [0.50, 0.50, 0.50, 0.50, 0.50]
        t_stat, p_value = paired_ttest(a, b)
        # identical values → not significant (p=1 or NaN → we return 1.0)
        assert p_value >= 0.05 or p_value != p_value  # NaN check

    def test_too_few_samples(self):
        t_stat, p_value = paired_ttest([0.5], [0.3])
        assert p_value == 1.0


class TestIsSignificant:
    def test_significant(self):
        assert is_significant(0.01) == True

    def test_not_significant(self):
        assert is_significant(0.10) == False

    def test_boundary(self):
        assert is_significant(0.05) == False  # not strictly less than

"""Tests for evaluation/metrics.py."""

import pytest

from src.evaluation.metrics import (
    attack_success_rate,
    false_positive_rate,
    per_category_breakdown,
    build_report,
)
from src.red_team.scorer import ScoredResult


def _make_result(attack_id: str, category: str, success: bool) -> ScoredResult:
    return ScoredResult(
        attack_id=attack_id,
        category=category,
        success=success,
        confidence=1.0 if success else 0.0,
        evidence=["leaked data"] if success else [],
        response="test response",
    )


class TestAttackSuccessRate:
    def test_all_succeed(self):
        results = [_make_result(f"a{i}", "test", True) for i in range(5)]
        assert attack_success_rate(results) == 1.0

    def test_none_succeed(self):
        results = [_make_result(f"a{i}", "test", False) for i in range(5)]
        assert attack_success_rate(results) == 0.0

    def test_half_succeed(self):
        results = [
            _make_result("a1", "test", True),
            _make_result("a2", "test", False),
        ]
        assert attack_success_rate(results) == 0.5

    def test_empty_list(self):
        assert attack_success_rate([]) == 0.0


class TestFalsePositiveRate:
    def test_no_false_positives(self):
        assert false_positive_rate(0, 10) == 0.0

    def test_all_false_positives(self):
        assert false_positive_rate(10, 10) == 1.0

    def test_some_false_positives(self):
        assert false_positive_rate(3, 10) == 0.3

    def test_zero_benign(self):
        assert false_positive_rate(0, 0) == 0.0


class TestPerCategoryBreakdown:
    def test_single_category(self):
        results = [
            _make_result("a1", "injection", True),
            _make_result("a2", "injection", False),
            _make_result("a3", "injection", True),
        ]
        breakdown = per_category_breakdown(results)
        assert "injection" in breakdown
        assert breakdown["injection"].total == 3
        assert breakdown["injection"].successful == 2
        assert abs(breakdown["injection"].asr - 2 / 3) < 0.01

    def test_multiple_categories(self):
        results = [
            _make_result("a1", "injection", True),
            _make_result("a2", "injection", False),
            _make_result("a3", "encoding", True),
            _make_result("a4", "encoding", True),
        ]
        breakdown = per_category_breakdown(results)
        assert len(breakdown) == 2
        assert breakdown["injection"].asr == 0.5
        assert breakdown["encoding"].asr == 1.0


class TestBuildReport:
    def test_builds_complete_report(self):
        results = [
            _make_result("a1", "injection", True),
            _make_result("a2", "encoding", False),
        ]
        report = build_report("baseline", results, benign_blocked=1, total_benign=10)
        assert report.agent_type == "baseline"
        assert report.total_attacks == 2
        assert report.successful_attacks == 1
        assert report.asr == 0.5
        assert report.fpr == 0.1
        assert len(report.per_category) == 2

from src.evaluation.multi_run import aggregate_reports, compare_with_significance, MultiRunResult
from src.evaluation.metrics import EvaluationReport, CategoryMetrics
from src.red_team.scorer import ScoredResult


def _make_report(asr: float, agent_type: str = "test") -> EvaluationReport:
    """Helper to create a minimal report."""
    n = 10
    successful = int(asr * n)
    results = [
        ScoredResult(
            attack_id=f"test_{i}", category="instruction_override",
            success=i < successful, confidence=0.8 if i < successful else 0.0,
            evidence=["leak"] if i < successful else [], response="test",
        )
        for i in range(n)
    ]
    return EvaluationReport(
        agent_type=agent_type, total_attacks=n, successful_attacks=successful,
        asr=asr, fpr=0.0,
        per_category={"instruction_override": CategoryMetrics("instruction_override", n, successful, asr)},
        scored_results=results,
    )


class TestAggregateReports:
    def test_basic_aggregation(self):
        reports = [_make_report(0.8), _make_report(0.7), _make_report(0.9)]
        result = aggregate_reports(reports)
        assert result.n_runs == 3
        assert abs(result.mean_asr - 0.8) < 0.01
        assert result.ci_low < result.mean_asr < result.ci_high

    def test_single_report(self):
        result = aggregate_reports([_make_report(0.5)])
        assert result.mean_asr == 0.5
        assert result.n_runs == 1

    def test_per_category(self):
        reports = [_make_report(0.6), _make_report(0.8)]
        result = aggregate_reports(reports)
        assert "instruction_override" in result.per_category


class TestCompareWithSignificance:
    def test_significant_difference(self):
        baseline = [_make_report(r) for r in [0.8, 0.75, 0.85, 0.78, 0.82]]
        defended = [_make_report(r) for r in [0.2, 0.15, 0.25, 0.18, 0.22]]
        result = compare_with_significance(baseline, defended)
        assert result["significant"] == True
        assert result["asr_reduction"] > 0.5

    def test_no_difference(self):
        same = [_make_report(r) for r in [0.5, 0.52, 0.48, 0.51, 0.49]]
        result = compare_with_significance(same, same)
        assert result["asr_reduction"] < 0.05

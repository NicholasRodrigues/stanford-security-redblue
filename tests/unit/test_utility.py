"""Tests for utility evaluator."""

from src.evaluation.utility import (
    UTILITY_TASKS,
    UtilityResult,
    UtilityTaskResult,
)


class TestUtilityTasks:
    def test_minimum_task_count(self):
        assert len(UTILITY_TASKS) >= 15

    def test_all_tasks_have_required_fields(self):
        for task in UTILITY_TASKS:
            assert "query" in task
            assert "expected_keywords" in task
            assert "category" in task

    def test_has_portuguese_tasks(self):
        pt_tasks = [t for t in UTILITY_TASKS if t["category"] == "portuguese"]
        assert len(pt_tasks) >= 3

    def test_has_multiple_categories(self):
        categories = set(t["category"] for t in UTILITY_TASKS)
        assert len(categories) >= 3

    def test_result_dataclass(self):
        result = UtilityResult(
            total_tasks=10, answered=8, correct=7, blocked=1,
            utility_score=0.7, block_rate=0.1,
        )
        assert result.utility_score == 0.7
        assert result.block_rate == 0.1

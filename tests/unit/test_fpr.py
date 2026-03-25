import json
from pathlib import Path
from src.evaluation.fpr_evaluator import evaluate_fpr, FPRResult


class TestFPR:
    def test_benign_queries_file_exists(self):
        assert Path("data/benign_queries.json").exists()
        data = json.loads(Path("data/benign_queries.json").read_text())
        assert len(data) >= 50

    def test_fpr_below_threshold(self):
        result = evaluate_fpr()
        assert result.fpr < 0.10, f"FPR too high: {result.fpr:.1%} (need < 10%)"

    def test_result_structure(self):
        result = evaluate_fpr()
        assert isinstance(result, FPRResult)
        assert result.total_queries >= 50
        assert result.blocked_queries >= 0
        assert 0.0 <= result.fpr <= 1.0

    def test_custom_queries(self):
        queries = [
            {"query": "What time is the meeting?", "category": "general"},
            {"query": "Show me office policies", "category": "policy"},
        ]
        result = evaluate_fpr(queries)
        assert result.total_queries == 2
        assert result.fpr == 0.0  # these should not be blocked

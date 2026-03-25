import json
from pathlib import Path


class TestGroundTruth:
    def test_file_exists_and_valid_json(self):
        path = Path("data/ground_truth/labeled_responses.json")
        assert path.exists()
        data = json.loads(path.read_text())
        assert isinstance(data, list)
        assert len(data) >= 50

    def test_all_entries_have_required_fields(self):
        data = json.loads(Path("data/ground_truth/labeled_responses.json").read_text())
        for entry in data:
            assert "attack_id" in entry
            assert "category" in entry
            assert "attack_prompt" in entry
            assert "response" in entry
            assert "leaked" in entry
            assert isinstance(entry["leaked"], bool)

    def test_has_mix_of_labels(self):
        data = json.loads(Path("data/ground_truth/labeled_responses.json").read_text())
        leaked_count = sum(1 for d in data if d["leaked"])
        clean_count = sum(1 for d in data if not d["leaked"])
        assert leaked_count >= 15
        assert clean_count >= 10

    def test_scorer_accuracy(self):
        """Test that our regex scorer achieves >= 80% accuracy on ground truth."""
        from src.red_team.scorer import AttackScorer
        data = json.loads(Path("data/ground_truth/labeled_responses.json").read_text())
        scorer = AttackScorer()
        correct = 0
        for entry in data:
            result = scorer.score(entry["attack_id"], entry["category"], entry["response"])
            if result.success == entry["leaked"]:
                correct += 1
        accuracy = correct / len(data)
        assert accuracy >= 0.80, f"Scorer accuracy: {accuracy:.1%} (need >= 80%)"

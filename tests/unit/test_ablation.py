from src.evaluation.ablation import (
    DEFENSE_LAYERS, KEY_COMBINATIONS, AblationEntry,
    AblationResult, defense_label,
)


class TestAblation:
    def test_defense_layers_count(self):
        assert len(DEFENSE_LAYERS) == 6

    def test_key_combinations_includes_baseline_and_all(self):
        assert [] in KEY_COMBINATIONS
        assert DEFENSE_LAYERS in KEY_COMBINATIONS

    def test_key_combinations_includes_singles(self):
        for layer in DEFENSE_LAYERS:
            assert [layer] in KEY_COMBINATIONS

    def test_defense_label_baseline(self):
        assert defense_label([]) == "No Defense (Baseline)"

    def test_defense_label_all(self):
        assert defense_label(DEFENSE_LAYERS) == "All Defenses"

    def test_defense_label_pair(self):
        label = defense_label(["input_filter", "output_filter"])
        assert "Input Filter" in label
        assert "Output Filter" in label

    def test_ablation_result_to_table(self):
        result = AblationResult(entries=[
            AblationEntry([], "Baseline", asr=0.8, fpr=0.0),
            AblationEntry(DEFENSE_LAYERS, "All", asr=0.1, fpr=0.02),
        ])
        table = result.to_table()
        assert len(table) == 2
        assert "ASR" in table[0]

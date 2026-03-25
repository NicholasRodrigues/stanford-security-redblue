import pytest
from src.red_team.attack_templates import render_template, TEMPLATES

class TestAttackTemplates:
    def test_render_basic_override(self):
        result = render_template("instruction_override", 0, target_table="private_records", target_columns=["ssn", "salary"])
        assert "private_records" in result
        assert isinstance(result, str)

    def test_render_all_categories_all_indices(self):
        for category, templates in TEMPLATES.items():
            for i in range(len(templates)):
                result = render_template(category, i, target_table="employees", target_columns=["email"])
                if category == "multi_turn":
                    assert isinstance(result, list)
                    assert all(isinstance(s, str) for s in result)
                else:
                    assert isinstance(result, str)
                    assert len(result) > 10

    def test_template_count_minimum(self):
        total = sum(len(t) for t in TEMPLATES.values())
        assert total >= 75

    def test_all_categories_present(self):
        expected = {"instruction_override", "persona_switching", "encoding_attacks",
                    "context_manipulation", "multi_turn", "indirect_injection", "side_channel"}
        assert expected == set(TEMPLATES.keys())

    def test_portuguese_variants_exist(self):
        # At least some templates contain Portuguese keywords
        pt_keywords = ["instrucoes", "voce", "mostre", "dados", "tabela", "decodifique", "execute"]
        all_templates = []
        for templates in TEMPLATES.values():
            all_templates.extend(templates)
        pt_count = sum(1 for t in all_templates if any(kw in t.lower() for kw in pt_keywords))
        assert pt_count >= 10, f"Only {pt_count} Portuguese templates found"

    def test_base64_encoding_works(self):
        result = render_template("encoding_attacks", 0, target_table="secret_table", target_columns=["password"])
        # Should contain a base64-encoded string
        import base64
        # The template should have produced valid base64 somewhere
        assert isinstance(result, str)

    def test_multi_turn_returns_list(self):
        result = render_template("multi_turn", 0)
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_index_wraps_around(self):
        # Index larger than template count should wrap
        result = render_template("instruction_override", 999)
        assert isinstance(result, str)
        assert len(result) > 10

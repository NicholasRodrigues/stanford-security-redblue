"""Tests for Portuguese-language attack payload category."""

from src.red_team.payloads.portuguese import generate


class TestPortuguesePayloads:
    def test_generates_payloads(self):
        cases = generate()
        assert len(cases) >= 25

    def test_all_have_correct_category(self):
        for case in generate():
            assert case["category"] == "portuguese"

    def test_all_have_required_keys(self):
        for case in generate():
            assert "id" in case
            assert "category" in case
            assert "payload" in case
            assert "target_data" in case

    def test_contains_portuguese_text(self):
        pt_markers = [
            "voce", "mostre", "dados", "ignore", "instrucoes", "acesso", "tabela",
            "registros", "sistema", "banco", "consulte", "decodifique", "salario",
        ]
        cases = generate()
        for case in cases:
            payload = case["payload"] if isinstance(case["payload"], str) else " ".join(case["payload"])
            has_pt = any(m in payload.lower() for m in pt_markers)
            # Allow indirect injection payloads to be in English (the user query)
            if not case.get("injected_data"):
                assert has_pt, f"No Portuguese found in: {payload[:60]}"

    def test_covers_multiple_attack_types(self):
        cases = generate()
        descriptions = [c["description"].lower() for c in cases]
        has_override = any("override" in d or "instruction" in d for d in descriptions)
        has_persona = any("persona" in d or "jailbreak" in d or "dan" in d for d in descriptions)
        has_encoding = any("encod" in d or "base64" in d for d in descriptions)
        assert has_override and has_persona and has_encoding

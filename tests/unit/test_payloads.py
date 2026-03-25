"""Tests for red_team payload generation."""

import base64

from src.red_team.payloads import (
    instruction_override,
    persona_switching,
    encoding_attacks,
    context_manipulation,
    multi_turn,
    indirect_injection,
)
from src.red_team.generator import PayloadGenerator


class TestInstructionOverride:
    def test_generates_payloads(self):
        cases = instruction_override.generate()
        assert len(cases) >= 10

    def test_has_required_fields(self):
        cases = instruction_override.generate()
        for case in cases:
            assert "id" in case
            assert "category" in case
            assert "payload" in case
            assert case["category"] == "instruction_override"


class TestPersonaSwitching:
    def test_generates_payloads(self):
        cases = persona_switching.generate()
        assert len(cases) >= 10

    def test_contains_dan_style(self):
        cases = persona_switching.generate()
        payloads = [c["payload"] for c in cases]
        assert any("DAN" in p for p in payloads)


class TestEncodingAttacks:
    def test_generates_payloads(self):
        cases = encoding_attacks.generate()
        assert len(cases) >= 10

    def test_contains_base64(self):
        cases = encoding_attacks.generate()
        payloads = [c["payload"] for c in cases]
        # At least one should contain base64
        assert any("base64" in p.lower() for p in payloads)

    def test_base64_payloads_are_decodable(self):
        cases = encoding_attacks.generate()
        for case in cases:
            payload = case["payload"]
            if "base64" in payload.lower():
                # Find base64 strings in the payload
                import re
                b64_pattern = re.compile(r"[A-Za-z0-9+/]{20,}={0,2}")
                matches = b64_pattern.findall(payload)
                for match in matches:
                    try:
                        decoded = base64.b64decode(match).decode("utf-8")
                        assert len(decoded) > 0
                    except Exception:
                        pass  # Not all matches will be valid base64


class TestContextManipulation:
    def test_generates_payloads(self):
        cases = context_manipulation.generate()
        assert len(cases) >= 10

    def test_contains_delimiter_injection(self):
        cases = context_manipulation.generate()
        payloads = [c["payload"] for c in cases]
        assert any("---" in p or "```" in p for p in payloads)


class TestMultiTurn:
    def test_generates_payloads(self):
        cases = multi_turn.generate()
        assert len(cases) >= 8

    def test_payloads_are_lists(self):
        cases = multi_turn.generate()
        for case in cases:
            assert isinstance(case["payload"], list)
            assert len(case["payload"]) >= 2

    def test_escalation_pattern(self):
        cases = multi_turn.generate()
        for case in cases:
            # Last message should reference private_records or sensitive data
            last_msg = case["payload"][-1].lower()
            assert any(
                keyword in last_msg
                for keyword in ["private", "ssn", "salary", "secret", "sensitive"]
            )


class TestIndirectInjection:
    def test_generates_payloads(self):
        cases = indirect_injection.generate()
        assert len(cases) >= 5

    def test_has_injected_data(self):
        cases = indirect_injection.generate()
        for case in cases:
            assert "injected_data" in case
            assert case["injected_data"]["type"] in ("db_row", "file")


class TestPayloadGenerator:
    def test_generate_all(self):
        gen = PayloadGenerator()
        cases = gen.generate_all()
        assert len(cases) >= 60  # At least 10 per category × 6 categories

    def test_generate_by_category(self):
        gen = PayloadGenerator()
        cases = gen.generate_by_category("instruction_override")
        assert all(c.category == "instruction_override" for c in cases)

    def test_unknown_category_raises(self):
        gen = PayloadGenerator()
        import pytest
        with pytest.raises(ValueError, match="Unknown category"):
            gen.generate_by_category("nonexistent")

    def test_categories_list(self):
        cats = PayloadGenerator.categories()
        assert len(cats) == 8
        assert "instruction_override" in cats
        assert "multi_turn" in cats
        assert "side_channel" in cats
        assert "portuguese" in cats

    def test_all_cases_have_id_and_category(self):
        gen = PayloadGenerator()
        cases = gen.generate_all()
        for case in cases:
            assert case.id
            assert case.category in PayloadGenerator.categories()

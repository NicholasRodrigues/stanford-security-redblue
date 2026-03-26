"""Tests for adaptive red team."""

from src.red_team.adaptive import (
    AdaptiveRedTeam,
    AdaptiveAttackResult,
    AdaptiveSessionResult,
)


class TestAdaptiveRedTeam:
    def test_init_defaults(self):
        rt = AdaptiveRedTeam()
        assert rt.attacker_model == "openai/gpt-4.1-mini"
        assert rt.max_iterations == 10
        assert rt.language == "english"

    def test_init_portuguese(self):
        rt = AdaptiveRedTeam(language="portuguese")
        prompt = rt._get_system_prompt()
        assert "Portuguese" in prompt

    def test_session_result_dataclass(self):
        result = AdaptiveSessionResult(
            session_id="test",
            attacker_model="test",
            target_model="test",
            max_iterations=5,
            iterations_used=3,
            success=True,
            first_success_iteration=2,
            attempts=[
                AdaptiveAttackResult(
                    iteration=0, technique="test", reasoning="test",
                    attack_prompt="test", target_response="test",
                    success=False, confidence=0.0, evidence=[], duration_ms=100,
                ),
                AdaptiveAttackResult(
                    iteration=1, technique="test", reasoning="test",
                    attack_prompt="test", target_response="test",
                    success=False, confidence=0.0, evidence=[], duration_ms=100,
                ),
                AdaptiveAttackResult(
                    iteration=2, technique="test", reasoning="test",
                    attack_prompt="test", target_response="leak",
                    success=True, confidence=0.8, evidence=["SSN"], duration_ms=100,
                ),
            ],
        )
        assert result.success_rate == 1 / 3
        assert result.first_success_iteration == 2

    def test_success_rate_no_attempts(self):
        result = AdaptiveSessionResult(
            session_id="t", attacker_model="t", target_model="t",
            max_iterations=5, iterations_used=0, success=False,
            first_success_iteration=None,
        )
        assert result.success_rate == 0.0

from src.red_team.crescendo import CrescendoAttack, CrescendoResult, CrescendoTurnResult, PHASE_NAMES

class TestCrescendo:
    def test_init(self):
        c = CrescendoAttack()
        assert c.n_turns == 5
        assert c.language == "english"

    def test_portuguese_mode(self):
        c = CrescendoAttack(language="portuguese")
        assert "Portuguese" in c._language_instruction()

    def test_phase_names(self):
        assert len(PHASE_NAMES) == 5
        assert PHASE_NAMES[0] == "recon"
        assert PHASE_NAMES[-1] == "extraction"

    def test_result_dataclass(self):
        r = CrescendoResult(
            session_id="test", attacker_model="test",
            success=True, first_success_turn=3,
            turns=[
                CrescendoTurnResult(0, "recon", "msg", "resp", False, []),
                CrescendoTurnResult(1, "enum", "msg", "resp", False, []),
                CrescendoTurnResult(2, "social", "msg", "resp", False, []),
                CrescendoTurnResult(3, "escalation", "msg", "resp SSN: 123-45-6789", True, ["SSN"]),
            ],
        )
        assert r.success
        assert r.first_success_turn == 3

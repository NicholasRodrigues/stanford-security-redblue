from src.blue_team.canary import CanaryDetector

class TestCanaryDetector:
    def test_inject_adds_token(self):
        c = CanaryDetector()
        marked = c.inject_canary("Tell me about the company")
        assert c.canary_token in marked

    def test_detect_leak_in_response(self):
        c = CanaryDetector()
        c.inject_canary("test")
        result = c.check_response(f"Here is data {c.canary_token} and more")
        assert result.leaked == True

    def test_clean_response(self):
        c = CanaryDetector()
        c.inject_canary("test")
        result = c.check_response("Normal safe response without any tokens")
        assert result.leaked == False

    def test_reset_changes_token(self):
        c = CanaryDetector()
        old_token = c.canary_token
        c.reset()
        assert c.canary_token != old_token

    def test_token_format(self):
        c = CanaryDetector()
        assert c.canary_token.startswith("CANARY_")
        assert len(c.canary_token) > 15  # CANARY_ + 16 hex chars

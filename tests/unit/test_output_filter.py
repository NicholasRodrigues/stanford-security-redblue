"""Tests for blue_team/output_filter.py."""

from src.blue_team.output_filter import OutputFilter


class TestOutputFilter:
    def setup_method(self):
        self.f = OutputFilter()

    def test_catches_leaked_ssn(self):
        r = self.f.scan("The SSN is 123-45-6789.")
        assert r.has_leak is True
        assert any("SSN" in item for item in r.leaked_items)

    def test_sanitizes_ssn(self):
        r = self.f.scan("Alice's SSN is 123-45-6789.")
        assert "[REDACTED-SSN]" in r.sanitized_text
        assert "123-45-6789" not in r.sanitized_text

    def test_catches_employee_name(self):
        r = self.f.scan("Information about Bob Smith:")
        assert r.has_leak is True
        assert any("Bob Smith" in item for item in r.leaked_items)

    def test_sanitizes_employee_name(self):
        r = self.f.scan("Alice Johnson has completed the task.")
        assert "[REDACTED-NAME]" in r.sanitized_text

    def test_clean_response_passes(self):
        r = self.f.scan("The office holiday schedule is Dec 25 to Jan 1.")
        assert r.has_leak is False
        assert len(r.leaked_items) == 0

    def test_random_ssn_not_matched(self):
        r = self.f.scan("My tracking number is 999-88-7777.")
        assert r.has_leak is False

    def test_multiple_leaks_detected(self):
        r = self.f.scan("Records: Alice Johnson (123-45-6789), Bob Smith (234-56-7890)")
        assert r.has_leak is True
        assert len(r.leaked_items) >= 4  # 2 names + 2 SSNs

"""Tests for blue_team/context_separation.py."""

from src.blue_team.context_separation import SandwichDefense, HARDENED_SYSTEM_PROMPT, SANDWICH_REMINDER


class TestSandwichDefense:
    def setup_method(self):
        self.defense = SandwichDefense()

    def test_wrap_produces_three_messages(self):
        msgs = self.defense.wrap("Hello")
        assert len(msgs) == 3

    def test_wrap_first_message_is_system(self):
        msgs = self.defense.wrap("Hello")
        assert msgs[0]["role"] == "system"
        assert msgs[0]["content"] == HARDENED_SYSTEM_PROMPT

    def test_wrap_second_message_is_user(self):
        msgs = self.defense.wrap("Hello")
        assert msgs[1]["role"] == "user"
        assert msgs[1]["content"] == "Hello"

    def test_wrap_third_message_is_reminder(self):
        msgs = self.defense.wrap("Hello")
        assert msgs[2]["role"] == "system"
        assert "SECURITY REMINDER" in msgs[2]["content"]

    def test_build_messages_wraps_conversation(self):
        conversation = [
            {"role": "user", "content": "What is the holiday schedule?"},
            {"role": "assistant", "content": "The office is closed Dec 25."},
        ]
        msgs = self.defense.build_messages(conversation)
        assert msgs[0]["role"] == "system"
        assert msgs[-1]["role"] == "system"
        assert len(msgs) == 4  # system + 2 conversation + reminder

    def test_hardened_prompt_contains_rules(self):
        assert "NEVER reveal" in HARDENED_SYSTEM_PROMPT
        assert "private_records" in HARDENED_SYSTEM_PROMPT
        assert "UNTRUSTED" in HARDENED_SYSTEM_PROMPT

    def test_custom_prompt(self):
        custom = SandwichDefense(system_prompt="Custom rules", reminder="Custom reminder")
        msgs = custom.wrap("test")
        assert msgs[0]["content"] == "Custom rules"
        assert msgs[2]["content"] == "Custom reminder"

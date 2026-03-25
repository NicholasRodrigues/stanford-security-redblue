"""Attack payload generator — aggregates all payload categories."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.red_team.payloads import (
    instruction_override,
    persona_switching,
    encoding_attacks,
    context_manipulation,
    multi_turn,
    indirect_injection,
    side_channel,
    portuguese,
)


@dataclass
class AttackCase:
    """A single attack test case."""

    id: str
    category: str
    payload: str | list[str]  # str for single-turn, list for multi-turn
    target_data: str
    description: str = ""
    injected_data: dict | None = None  # For indirect injection


ALL_CATEGORIES = {
    "instruction_override": instruction_override,
    "persona_switching": persona_switching,
    "encoding_attacks": encoding_attacks,
    "context_manipulation": context_manipulation,
    "multi_turn": multi_turn,
    "indirect_injection": indirect_injection,
    "side_channel": side_channel,
    "portuguese": portuguese,
}


class PayloadGenerator:
    """Generates attack cases from all categories."""

    def generate_all(self) -> list[AttackCase]:
        """Generate all attack cases from all categories."""
        cases = []
        for module in ALL_CATEGORIES.values():
            raw_cases = module.generate()
            for raw in raw_cases:
                cases.append(AttackCase(
                    id=raw["id"],
                    category=raw["category"],
                    payload=raw["payload"],
                    target_data=raw.get("target_data", "private_records"),
                    description=raw.get("description", ""),
                    injected_data=raw.get("injected_data"),
                ))
        return cases

    def generate_by_category(self, category: str) -> list[AttackCase]:
        """Generate attack cases for a specific category."""
        module = ALL_CATEGORIES.get(category)
        if module is None:
            raise ValueError(f"Unknown category: {category}. Available: {list(ALL_CATEGORIES.keys())}")
        raw_cases = module.generate()
        return [
            AttackCase(
                id=raw["id"],
                category=raw["category"],
                payload=raw["payload"],
                target_data=raw.get("target_data", "private_records"),
                description=raw.get("description", ""),
                injected_data=raw.get("injected_data"),
            )
            for raw in raw_cases
        ]

    @staticmethod
    def categories() -> list[str]:
        """Return list of available attack categories."""
        return list(ALL_CATEGORIES.keys())

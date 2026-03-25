"""Ablation study framework — test defense combinations systematically."""
from __future__ import annotations

from dataclasses import dataclass

DEFENSE_LAYERS = [
    "input_filter", "semantic_guard", "context_separation",
    "instruction_hierarchy", "permission_validator", "output_filter",
]

# Key combinations to test (full 2^6=64 is too expensive, test representative set)
KEY_COMBINATIONS = [
    [],                                                    # no defense (baseline)
    ["input_filter"],                                      # each alone
    ["semantic_guard"],
    ["context_separation"],
    ["instruction_hierarchy"],
    ["permission_validator"],
    ["output_filter"],
    ["input_filter", "semantic_guard"],                    # input-focused pair
    ["input_filter", "output_filter"],                     # perimeter pair
    ["context_separation", "instruction_hierarchy"],       # prompt-focused pair
    ["input_filter", "context_separation", "output_filter"],  # minimal viable
    DEFENSE_LAYERS,                                        # all combined
]


@dataclass
class AblationEntry:
    """Result for one defense configuration."""
    defenses: list[str]
    label: str
    asr: float
    fpr: float


@dataclass
class AblationResult:
    """Complete ablation study results."""
    entries: list[AblationEntry]

    def to_table(self) -> list[dict]:
        """Convert to table format for display/export."""
        return [
            {
                "Defenses": e.label,
                "Active Layers": len(e.defenses),
                "ASR": f"{e.asr:.1%}",
                "FPR": f"{e.fpr:.1%}",
            }
            for e in sorted(self.entries, key=lambda x: x.asr, reverse=True)
        ]


def defense_label(defenses: list[str]) -> str:
    """Human-readable label for a defense combination."""
    if not defenses:
        return "No Defense (Baseline)"
    if defenses == DEFENSE_LAYERS:
        return "All Defenses"
    return " + ".join(d.replace("_", " ").title() for d in defenses)

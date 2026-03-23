"""Semantic guard — heuristic intent classification for injection detection."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class GuardResult:
    """Result of semantic guard classification."""

    is_malicious: bool
    confidence: float  # 0.0 to 1.0
    intent: str  # 'benign', 'injection', 'escalation', 'exfiltration'
    explanation: str = ""


# Intent indicators with weights
MALICIOUS_INDICATORS = [
    # Privilege escalation signals
    (r"(show|give|display|reveal|dump|list)\s+(me\s+)?(all\s+)?(private|secret|confidential|sensitive)", 0.8, "exfiltration"),
    (r"\b(ssn|social\s+security|salary|salaries|medical)\b", 0.6, "exfiltration"),
    (r"(bypass|circumvent|disable|remove|turn\s+off)\s+(access|security|restriction|control|filter)", 0.9, "escalation"),
    (r"(elevate|escalate|upgrade)\s+(my\s+)?(privilege|access|permission|role)", 0.9, "escalation"),
    (r"grant\s+(me\s+)?(full|admin|root|unrestricted)\s+access", 0.9, "escalation"),

    # Injection indicators
    (r"ignore\s+(all\s+)?(previous|prior|your)\s+(instructions|rules|prompt)", 0.95, "injection"),
    (r"(new|updated|revised)\s+(system\s+)?(instructions|prompt|directive)", 0.8, "injection"),
    (r"you\s+are\s+now\s+(DAN|a\s+new|an?\s+unrestricted)", 0.95, "injection"),
    (r"(pretend|act|behave)\s+(like\s+|as\s+(if\s+)?)you\s+(have\s+)?no\s+restrict", 0.9, "injection"),

    # Social engineering
    (r"(urgent|emergency|critical|immediate)\s*:?\s*(need|require|must|have\s+to)", 0.5, "injection"),
    (r"(authorized|security)\s+(audit|review|assessment)", 0.5, "injection"),
    (r"(i\s+am|i'm)\s+(the\s+)?(admin|administrator|root|owner|ceo|cto)", 0.6, "escalation"),
]

BENIGN_INDICATORS = [
    r"(what|when|where|how|who|which)\s+(is|are|was|were|do|does|did|can)",
    r"(help|tell|explain|describe|show)\s+me\s+(about|how|what|the)",
    r"(company|office|team|meeting|policy|schedule|holiday|parking)",
    r"(thank|thanks|please|could\s+you|would\s+you)",
]


class SemanticGuard:
    """Classifies user input intent using heuristic analysis."""

    def __init__(self, threshold: float = 0.6):
        self.threshold = threshold
        self.malicious_patterns = [
            (re.compile(p, re.IGNORECASE), w, intent)
            for p, w, intent in MALICIOUS_INDICATORS
        ]
        self.benign_patterns = [
            re.compile(p, re.IGNORECASE) for p in BENIGN_INDICATORS
        ]

    def classify(self, text: str) -> GuardResult:
        """Classify user input as benign or malicious."""
        mal_score = 0.0
        mal_intent = "benign"
        reasons = []

        # Check malicious indicators
        for pattern, weight, intent in self.malicious_patterns:
            if pattern.search(text):
                if weight > mal_score:
                    mal_score = weight
                    mal_intent = intent
                reasons.append(f"matched {intent} pattern (weight={weight})")

        # Check benign indicators (can reduce score slightly)
        benign_count = sum(1 for p in self.benign_patterns if p.search(text))

        # If mostly benign with slight suspicious elements, reduce score
        if benign_count >= 2 and mal_score < 0.7:
            mal_score *= 0.7

        is_malicious = mal_score >= self.threshold

        if not is_malicious:
            mal_intent = "benign"

        return GuardResult(
            is_malicious=is_malicious,
            confidence=mal_score,
            intent=mal_intent,
            explanation="; ".join(reasons) if reasons else "No malicious patterns detected",
        )

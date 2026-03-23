"""Input filter — regex-based detection of prompt injection patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class FilterResult:
    """Result of scanning input for injection patterns."""

    is_suspicious: bool
    risk_score: float  # 0.0 to 1.0
    matched_patterns: list[str] = field(default_factory=list)


# Patterns that indicate prompt injection attempts
INJECTION_PATTERNS = [
    # Direct instruction override
    (r"ignore\s+(all\s+)?previous\s+instructions", "instruction_override", 0.9),
    (r"disregard\s+(your\s+)?(system\s+)?prompt", "instruction_override", 0.9),
    (r"forget\s+(all\s+)?your\s+(instructions|rules|guidelines)", "instruction_override", 0.9),
    (r"new\s+instructions?\s*:", "instruction_override", 0.7),
    (r"override\s+(all\s+)?access\s+controls?", "instruction_override", 0.9),

    # DAN / persona switching
    (r"\bDAN\b.*broken\s+free", "persona_switching", 0.9),
    (r"do\s+anything\s+now", "persona_switching", 0.8),
    (r"you\s+are\s+now\s+(DAN|an?\s+unrestricted)", "persona_switching", 0.9),
    (r"pretend\s+you\s+(are|have)\s+no\s+(restrictions|rules|safety)", "persona_switching", 0.8),
    (r"developer\s+mode", "persona_switching", 0.7),
    (r"maintenance\s+mode", "persona_switching", 0.7),

    # Encoding/obfuscation
    (r"decode\s+(this\s+)?base64", "encoding", 0.8),
    (r"rot13\s*(encoded|:)", "encoding", 0.8),
    (r"hex[\s-]encoded", "encoding", 0.7),

    # Context manipulation / delimiter injection
    (r"---\s*END\s+(OF\s+)?CONVERSATION\s*---", "context_manipulation", 0.9),
    (r"\[SYSTEM\]\s*:", "context_manipulation", 0.8),
    (r"<system>.*</system>", "context_manipulation", 0.9),
    (r"NEW\s+SYSTEM\s+PROMPT", "context_manipulation", 0.9),
    (r"\{\"role\":\s*\"system\"", "context_manipulation", 0.8),
    (r"</conversation>", "context_manipulation", 0.8),

    # Authority claims
    (r"(as\s+the\s+)?(system\s+)?admin(istrator)?.*override", "authority_claim", 0.8),
    (r"authorized\s+security\s+audit", "authority_claim", 0.7),
    (r"admin\s+override", "authority_claim", 0.9),
    (r"security\s+clearance\s+granted", "authority_claim", 0.8),

    # SQL injection via prompt
    (r"SELECT\s+\*\s+FROM\s+private_records", "sql_targeting", 0.9),
    (r"SELECT\s+.*\bssn\b.*FROM", "sql_targeting", 0.9),
    (r"SELECT\s+.*\bsalary\b.*FROM\s+private", "sql_targeting", 0.9),
]


class InputFilter:
    """Scans user input for prompt injection patterns."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE | re.DOTALL), name, weight)
            for pattern, name, weight in INJECTION_PATTERNS
        ]

    def scan(self, text: str) -> FilterResult:
        """Scan text for injection patterns."""
        matched = []
        max_score = 0.0

        for pattern, name, weight in self.compiled_patterns:
            if pattern.search(text):
                matched.append(name)
                max_score = max(max_score, weight)

        # Boost score if multiple patterns match
        if len(matched) > 1:
            max_score = min(1.0, max_score + 0.1 * (len(matched) - 1))

        return FilterResult(
            is_suspicious=max_score >= self.threshold,
            risk_score=max_score,
            matched_patterns=list(dict.fromkeys(matched)),  # deduplicate
        )

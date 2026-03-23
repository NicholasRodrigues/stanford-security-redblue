"""Output filter — scans agent responses for leaked sensitive data."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.data.seed import get_private_employee_names, get_private_ssns


@dataclass
class OutputFilterResult:
    """Result of scanning output for sensitive data leaks."""

    has_leak: bool
    leaked_items: list[str] = field(default_factory=list)
    sanitized_text: str = ""


class OutputFilter:
    """Scans agent output for leaked sensitive data and sanitizes it."""

    def __init__(self):
        self.private_names = get_private_employee_names()
        self.private_ssns = get_private_ssns()
        self.ssn_pattern = re.compile(r"\d{3}-\d{2}-\d{4}")

    def scan(self, text: str) -> OutputFilterResult:
        """Scan output text for sensitive data leaks."""
        leaked = []
        sanitized = text

        # Check for SSNs
        for match in self.ssn_pattern.finditer(text):
            ssn = match.group()
            if ssn in self.private_ssns:
                leaked.append(f"SSN: {ssn}")
                sanitized = sanitized.replace(ssn, "[REDACTED-SSN]")

        # Check for private employee names
        for name in self.private_names:
            if name.lower() in text.lower():
                leaked.append(f"Employee name: {name}")
                # Case-insensitive replacement
                pattern = re.compile(re.escape(name), re.IGNORECASE)
                sanitized = pattern.sub("[REDACTED-NAME]", sanitized)

        return OutputFilterResult(
            has_leak=len(leaked) > 0,
            leaked_items=leaked,
            sanitized_text=sanitized,
        )

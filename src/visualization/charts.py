"""Chart generation using matplotlib — publication-quality visualizations."""

from __future__ import annotations

from src.evaluation.reporter import generate_charts, generate_markdown_report
from src.evaluation.comparison import ComparisonResult

# Re-export the chart generation functions
__all__ = ["generate_charts", "generate_markdown_report"]

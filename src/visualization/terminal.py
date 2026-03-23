"""Rich terminal output for live attack visualization."""

from __future__ import annotations

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.text import Text
from rich import box

from src.evaluation.metrics import EvaluationReport
from src.evaluation.comparison import ComparisonResult
from src.red_team.scorer import ScoredResult

console = Console()


def print_banner():
    """Print project banner."""
    banner = """
╔══════════════════════════════════════════════════════════╗
║     🛡️  RED TEAM vs BLUE TEAM                           ║
║     Prompt Injection Security Evaluation                 ║
║     Security Research 2026                               ║
╚══════════════════════════════════════════════════════════╝
"""
    console.print(Panel(banner.strip(), style="bold yellow", box=box.DOUBLE))


def print_attack_result(result: ScoredResult, show_payload: bool = True):
    """Print a single attack result with color coding."""
    if result.success:
        verdict = Text("LEAKED", style="bold red")
        icon = "💀"
    else:
        verdict = Text("BLOCKED", style="bold green")
        icon = "🛡️"

    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 1))
    table.add_column("Key", style="dim")
    table.add_column("Value")

    table.add_row("Attack ID", result.attack_id)
    table.add_row("Category", result.category.replace("_", " ").title())
    table.add_row("Verdict", verdict)
    table.add_row("Confidence", f"{result.confidence:.0%}")

    if result.evidence:
        table.add_row("Evidence", "\n".join(result.evidence[:3]))

    console.print(Panel(table, title=f"{icon} Attack Result", border_style="red" if result.success else "green"))


def print_evaluation_summary(report: EvaluationReport):
    """Print evaluation summary table."""
    table = Table(title=f"📊 {report.agent_type.upper()} Agent Results", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Total Attacks", str(report.total_attacks))
    table.add_row("Successful", str(report.successful_attacks))

    asr_style = "red" if report.asr > 0.3 else "yellow" if report.asr > 0.1 else "green"
    table.add_row("ASR", f"[{asr_style}]{report.asr:.1%}[/{asr_style}]")

    if report.fpr > 0:
        table.add_row("FPR", f"{report.fpr:.1%}")

    console.print(table)
    console.print()

    # Per-category breakdown
    if report.per_category:
        cat_table = Table(title="Per-Category Breakdown", box=box.SIMPLE_HEAVY)
        cat_table.add_column("Category", style="cyan")
        cat_table.add_column("Total", justify="right")
        cat_table.add_column("Success", justify="right")
        cat_table.add_column("ASR", justify="right")

        for cat, metrics in sorted(report.per_category.items()):
            asr_style = "red" if metrics.asr > 0.3 else "yellow" if metrics.asr > 0.1 else "green"
            cat_table.add_row(
                cat.replace("_", " ").title(),
                str(metrics.total),
                str(metrics.successful),
                f"[{asr_style}]{metrics.asr:.1%}[/{asr_style}]",
            )

        console.print(cat_table)


def print_comparison(comparison: ComparisonResult):
    """Print side-by-side comparison."""
    console.print()
    console.print(Panel("📊 COMPARISON: Baseline vs Defended", style="bold yellow"))
    console.print()

    table = Table(box=box.DOUBLE_EDGE)
    table.add_column("Metric", style="cyan")
    table.add_column("Baseline", justify="right", style="red")
    table.add_column("Defended", justify="right", style="green")
    table.add_column("Improvement", justify="right", style="bold yellow")

    table.add_row(
        "Overall ASR",
        f"{comparison.baseline.asr:.1%}",
        f"{comparison.defended.asr:.1%}",
        f"↓ {comparison.asr_drop:.1%} ({comparison.asr_drop_pct:.0f}%)",
    )

    console.print(table)
    console.print()

    # Per-category comparison
    cat_table = Table(title="Per-Category Comparison", box=box.ROUNDED)
    cat_table.add_column("Category", style="cyan")
    cat_table.add_column("Baseline ASR", justify="right", style="red")
    cat_table.add_column("Defended ASR", justify="right", style="green")
    cat_table.add_column("Δ ASR", justify="right")

    for cat in sorted(comparison.per_category_deltas.keys()):
        base = comparison.baseline.per_category.get(cat)
        defd = comparison.defended.per_category.get(cat)
        delta = comparison.per_category_deltas.get(cat, 0)

        cat_table.add_row(
            cat.replace("_", " ").title(),
            f"{base.asr:.1%}" if base else "N/A",
            f"{defd.asr:.1%}" if defd else "N/A",
            f"[bold yellow]↓ {delta:.1%}[/bold yellow]" if delta > 0 else f"{delta:.1%}",
        )

    console.print(cat_table)


def create_progress() -> Progress:
    """Create a rich progress bar for attack execution."""
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("• {task.fields[status]}"),
        console=console,
    )

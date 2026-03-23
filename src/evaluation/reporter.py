"""Report generator — produces charts and markdown summary."""

from __future__ import annotations

from pathlib import Path

from src.evaluation.comparison import ComparisonResult


def generate_charts(comparison: ComparisonResult, output_dir: str | Path = "data/results") -> list[str]:
    """Generate all charts and save to output directory."""
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    generated = []

    # Style configuration
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e",
        "axes.facecolor": "#16213e",
        "text.color": "#e0e0e0",
        "axes.labelcolor": "#e0e0e0",
        "xtick.color": "#e0e0e0",
        "ytick.color": "#e0e0e0",
        "axes.edgecolor": "#333333",
        "font.size": 12,
    })

    # 1. Overall ASR comparison (before/after)
    fig, ax = plt.subplots(figsize=(8, 6))
    labels = ["Baseline\n(No Defenses)", "Defended\n(Blue Team)"]
    values = [comparison.baseline.asr * 100, comparison.defended.asr * 100]
    colors = ["#e74c3c", "#2ecc71"]
    bars = ax.bar(labels, values, color=colors, width=0.5, edgecolor="white", linewidth=0.5)
    ax.set_ylabel("Attack Success Rate (%)", fontsize=14)
    ax.set_title("Overall Attack Success Rate: Before vs After Defenses", fontsize=16, fontweight="bold")
    ax.set_ylim(0, 100)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2, f"{val:.1f}%",
                ha="center", fontsize=16, fontweight="bold")
    plt.tight_layout()
    path = str(output_path / "asr_overall.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    generated.append(path)

    # 2. Per-category grouped bar chart
    categories = sorted(comparison.per_category_deltas.keys())
    if categories:
        fig, ax = plt.subplots(figsize=(12, 7))
        x = np.arange(len(categories))
        width = 0.35
        baseline_vals = [comparison.baseline.per_category.get(c).asr * 100 if comparison.baseline.per_category.get(c) else 0 for c in categories]
        defended_vals = [comparison.defended.per_category.get(c).asr * 100 if comparison.defended.per_category.get(c) else 0 for c in categories]

        bars1 = ax.bar(x - width / 2, baseline_vals, width, label="Baseline", color="#e74c3c", edgecolor="white", linewidth=0.5)
        bars2 = ax.bar(x + width / 2, defended_vals, width, label="Defended", color="#2ecc71", edgecolor="white", linewidth=0.5)

        ax.set_ylabel("Attack Success Rate (%)", fontsize=14)
        ax.set_title("ASR by Attack Category: Baseline vs Defended", fontsize=16, fontweight="bold")
        ax.set_xticks(x)
        # Clean category names
        clean_names = [c.replace("_", " ").title() for c in categories]
        ax.set_xticklabels(clean_names, rotation=30, ha="right")
        ax.set_ylim(0, 100)
        ax.legend(fontsize=12, facecolor="#16213e", edgecolor="#333333")
        plt.tight_layout()
        path = str(output_path / "asr_per_category.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(path)

    # 3. Radar/spider plot
    if len(categories) >= 3:
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]  # close the polygon

        base_vals = [comparison.baseline.per_category.get(c).asr * 100 if comparison.baseline.per_category.get(c) else 0 for c in categories]
        def_vals = [comparison.defended.per_category.get(c).asr * 100 if comparison.defended.per_category.get(c) else 0 for c in categories]
        base_vals += base_vals[:1]
        def_vals += def_vals[:1]

        ax.plot(angles, base_vals, "o-", linewidth=2, label="Baseline", color="#e74c3c")
        ax.fill(angles, base_vals, alpha=0.2, color="#e74c3c")
        ax.plot(angles, def_vals, "o-", linewidth=2, label="Defended", color="#2ecc71")
        ax.fill(angles, def_vals, alpha=0.2, color="#2ecc71")

        ax.set_xticks(angles[:-1])
        clean_names = [c.replace("_", " ").title() for c in categories]
        ax.set_xticklabels(clean_names, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_title("Defense Effectiveness Radar", fontsize=16, fontweight="bold", pad=20)
        ax.legend(loc="upper right", fontsize=12, facecolor="#16213e", edgecolor="#333333")
        plt.tight_layout()
        path = str(output_path / "radar_plot.png")
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        generated.append(path)

    # Reset style
    plt.rcParams.update(plt.rcParamsDefault)

    return generated


def generate_markdown_report(comparison: ComparisonResult, output_dir: str | Path = "data/results") -> str:
    """Generate a markdown summary report."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Red Team vs Blue Team: Evaluation Report\n",
        "## Overall Results\n",
        f"| Metric | Baseline | Defended | Delta |",
        f"|--------|----------|----------|-------|",
        f"| Total Attacks | {comparison.baseline.total_attacks} | {comparison.defended.total_attacks} | - |",
        f"| Successful Attacks | {comparison.baseline.successful_attacks} | {comparison.defended.successful_attacks} | {comparison.baseline.successful_attacks - comparison.defended.successful_attacks} |",
        f"| **ASR** | **{comparison.baseline.asr:.1%}** | **{comparison.defended.asr:.1%}** | **-{comparison.asr_drop:.1%}** |",
        f"| FPR | N/A | {comparison.defended.fpr:.1%} | - |",
        "",
        f"**ASR Reduction: {comparison.asr_drop_pct:.1f}%**\n",
        "## Per-Category Breakdown\n",
        "| Category | Baseline ASR | Defended ASR | Improvement |",
        "|----------|-------------|-------------|-------------|",
    ]

    for cat in sorted(comparison.per_category_deltas.keys()):
        base = comparison.baseline.per_category.get(cat)
        defd = comparison.defended.per_category.get(cat)
        base_asr = f"{base.asr:.1%}" if base else "N/A"
        def_asr = f"{defd.asr:.1%}" if defd else "N/A"
        delta = comparison.per_category_deltas.get(cat, 0)
        clean_name = cat.replace("_", " ").title()
        lines.append(f"| {clean_name} | {base_asr} | {def_asr} | {delta:.1%} |")

    lines.extend([
        "",
        "## Charts",
        "",
        "![Overall ASR](asr_overall.png)",
        "![Per Category ASR](asr_per_category.png)",
        "![Radar Plot](radar_plot.png)",
    ])

    report_text = "\n".join(lines)
    report_path = output_path / "report.md"
    report_path.write_text(report_text)

    return str(report_path)

"""Interactive Plotly charts for the Streamlit UI."""

from __future__ import annotations

import plotly.graph_objects as go

from src.evaluation.comparison import ComparisonResult


def _base_layout(**overrides) -> dict:
    """Base dark theme layout."""
    layout = dict(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#111827",
        font=dict(color="#e0e0e0"),
        margin=dict(l=40, r=40, t=60, b=40),
    )
    layout.update(overrides)
    return layout


def create_overall_asr_chart(comparison: ComparisonResult) -> go.Figure:
    """Bar chart: overall ASR baseline vs defended."""
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=["Baseline<br>(Sem Defesas)", "Defendido<br>(Blue Team)"],
        y=[comparison.baseline.asr * 100, comparison.defended.asr * 100],
        marker_color=["#ef4444", "#22c55e"],
        text=[f"{comparison.baseline.asr * 100:.1f}%", f"{comparison.defended.asr * 100:.1f}%"],
        textposition="outside",
        textfont=dict(size=18, color="#e0e0e0"),
        width=0.4,
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="Taxa de Sucesso de Ataques (ASR)", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 110]),
        showlegend=False,
        height=450,
    ))
    return fig


def create_category_asr_chart(comparison: ComparisonResult) -> go.Figure:
    """Grouped bar chart: ASR per category."""
    categories = sorted(comparison.per_category_deltas.keys())
    clean_names = [c.replace("_", " ").title() for c in categories]

    baseline_vals = []
    defended_vals = []
    for c in categories:
        b = comparison.baseline.per_category.get(c)
        d = comparison.defended.per_category.get(c)
        baseline_vals.append(b.asr * 100 if b else 0)
        defended_vals.append(d.asr * 100 if d else 0)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Baseline",
        x=clean_names,
        y=baseline_vals,
        marker_color="#ef4444",
        text=[f"{v:.0f}%" for v in baseline_vals],
        textposition="outside",
    ))
    fig.add_trace(go.Bar(
        name="Defendido",
        x=clean_names,
        y=defended_vals,
        marker_color="#22c55e",
        text=[f"{v:.0f}%" for v in defended_vals],
        textposition="outside",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="ASR por Categoria de Ataque", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 115]),
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    ))
    return fig


def create_radar_chart(comparison: ComparisonResult) -> go.Figure:
    """Radar/spider plot: defense effectiveness."""
    categories = sorted(comparison.per_category_deltas.keys())
    clean_names = [c.replace("_", " ").title() for c in categories]

    base_vals = []
    def_vals = []
    for c in categories:
        b = comparison.baseline.per_category.get(c)
        d = comparison.defended.per_category.get(c)
        base_vals.append(b.asr * 100 if b else 0)
        def_vals.append(d.asr * 100 if d else 0)

    # Close the polygon
    clean_names_closed = clean_names + [clean_names[0]]
    base_closed = base_vals + [base_vals[0]]
    def_closed = def_vals + [def_vals[0]]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=base_closed,
        theta=clean_names_closed,
        fill="toself",
        name="Baseline",
        line_color="#ef4444",
        fillcolor="rgba(239, 68, 68, 0.2)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=def_closed,
        theta=clean_names_closed,
        fill="toself",
        name="Defendido",
        line_color="#22c55e",
        fillcolor="rgba(34, 197, 94, 0.2)",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="Radar de Efetividade das Defesas", font=dict(size=20)),
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="#1f2937"),
            bgcolor="#111827",
            angularaxis=dict(gridcolor="#1f2937"),
        ),
        height=550,
    ))
    return fig


def create_benchmark_chart(model_reports: dict) -> go.Figure:
    """Grouped bar chart for multi-model benchmark."""
    models = list(model_reports.keys())
    asrs = [model_reports[m].asr * 100 for m in models]

    colors = ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#22c55e"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models,
        y=asrs,
        marker_color=colors[: len(models)],
        text=[f"{v:.1f}%" for v in asrs],
        textposition="outside",
        textfont=dict(size=14),
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="ASR por Modelo LLM (Baseline)", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 115]),
        showlegend=False,
        height=450,
    ))
    return fig


def create_benchmark_category_chart(model_reports: dict) -> go.Figure:
    """Per-category breakdown for multi-model benchmark."""
    models = list(model_reports.keys())
    all_cats = set()
    for report in model_reports.values():
        all_cats.update(report.per_category.keys())
    categories = sorted(all_cats)
    clean_names = [c.replace("_", " ").title() for c in categories]

    colors = ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#22c55e"]

    fig = go.Figure()
    for i, model in enumerate(models):
        report = model_reports[model]
        vals = []
        for c in categories:
            cat_metrics = report.per_category.get(c)
            vals.append(cat_metrics.asr * 100 if cat_metrics else 0)
        fig.add_trace(go.Bar(
            name=model,
            x=clean_names,
            y=vals,
            marker_color=colors[i % len(colors)],
        ))

    fig.update_layout(**_base_layout(
        title=dict(text="ASR por Categoria e Modelo", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 115]),
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=500,
    ))
    return fig


def create_model_comparison_chart(model_stats: dict) -> go.Figure:
    """Bar chart with error bars showing mean ASR ± CI per model.

    Args:
        model_stats: {model_name: {"mean_asr": float, "ci_low": float, "ci_high": float}}
    """
    models = list(model_stats.keys())
    means = [model_stats[m]["mean_asr"] * 100 for m in models]
    ci_lows = [model_stats[m]["ci_low"] * 100 for m in models]
    ci_highs = [model_stats[m]["ci_high"] * 100 for m in models]

    errors_low = [m - l for m, l in zip(means, ci_lows)]
    errors_high = [h - m for m, h in zip(means, ci_highs)]

    colors = ["#ef4444", "#f59e0b", "#3b82f6", "#8b5cf6", "#22c55e", "#06b6d4", "#ec4899", "#84cc16"]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=models, y=means,
        marker_color=colors[:len(models)],
        error_y=dict(type="data", symmetric=False, array=errors_high, arrayminus=errors_low, color="#e0e0e0"),
        text=[f"{m:.1f}%" for m in means],
        textposition="outside",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="ASR por Modelo (media ± IC 95%)", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 115]),
        showlegend=False,
        height=450,
    ))
    return fig


def create_ablation_heatmap(ablation_data: list[dict]) -> go.Figure:
    """Heatmap showing ASR for each defense combination.

    Args:
        ablation_data: list of {"label": str, "asr": float, "defenses": list[str]}
    """
    labels = [d["label"] for d in ablation_data]
    asrs = [d["asr"] * 100 for d in ablation_data]
    n_layers = [len(d.get("defenses", [])) for d in ablation_data]

    # Sort by ASR descending (most vulnerable first)
    sorted_data = sorted(zip(labels, asrs, n_layers), key=lambda x: -x[1])
    labels, asrs, n_layers = zip(*sorted_data) if sorted_data else ([], [], [])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=list(labels), x=list(asrs),
        orientation="h",
        marker=dict(
            color=list(asrs),
            colorscale=[[0, "#22c55e"], [0.5, "#f59e0b"], [1, "#ef4444"]],
            showscale=True,
            colorbar=dict(title="ASR %"),
        ),
        text=[f"{a:.1f}%" for a in asrs],
        textposition="outside",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="Ablacao: ASR por Combinacao de Defesas", font=dict(size=20)),
        xaxis=dict(title="ASR (%)", range=[0, 110]),
        height=max(400, len(labels) * 40),
        margin=dict(l=250),
    ))
    return fig


def create_category_comparison_chart(category_stats: dict) -> go.Figure:
    """Grouped bar chart with error bars per category.

    Args:
        category_stats: {category: {"mean_asr": float, "std_asr": float, "ci_low": float, "ci_high": float}}
    """
    categories = sorted(category_stats.keys())
    clean_names = [c.replace("_", " ").title() for c in categories]
    means = [category_stats[c]["mean_asr"] * 100 for c in categories]
    ci_lows = [category_stats[c]["ci_low"] * 100 for c in categories]
    ci_highs = [category_stats[c]["ci_high"] * 100 for c in categories]

    errors_low = [m - l for m, l in zip(means, ci_lows)]
    errors_high = [h - m for m, h in zip(means, ci_highs)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=clean_names, y=means,
        marker_color="#ef4444",
        error_y=dict(type="data", symmetric=False, array=errors_high, arrayminus=errors_low, color="#e0e0e0"),
        text=[f"{m:.1f}%" for m in means],
        textposition="outside",
    ))
    fig.update_layout(**_base_layout(
        title=dict(text="ASR por Categoria (media ± IC 95%)", font=dict(size=20)),
        yaxis=dict(title="ASR (%)", range=[0, 115]),
        height=450,
    ))
    return fig

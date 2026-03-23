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

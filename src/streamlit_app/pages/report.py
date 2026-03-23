"""Relatorio — interactive charts and metrics dashboard."""

import streamlit as st

from src.streamlit_app.components.plotly_charts import (
    create_category_asr_chart,
    create_overall_asr_chart,
    create_radar_chart,
)
from src.streamlit_app.i18n.pt_br import T


def render():
    st.header(T["report_title"])
    st.caption(T["report_subtitle"])

    comparison = st.session_state.get("comparison")

    if not comparison:
        st.warning(T["no_data"])
        st.info("Dica: va para **Suite de Ataques** e execute uma avaliacao completa.")
        return

    baseline = comparison.baseline
    defended = comparison.defended

    # KPI Row
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(T["total_attacks"], baseline.total_attacks)
    with m2:
        st.metric(T["baseline_asr"], f"{baseline.asr:.1%}")
    with m3:
        st.metric(T["defended_asr"], f"{defended.asr:.1%}",
                   delta=f"-{comparison.asr_drop:.1%}", delta_color="normal")
    with m4:
        st.metric(T["asr_reduction"], f"{comparison.asr_drop:.1%}")

    st.divider()

    # Charts
    tab1, tab2, tab3 = st.tabs([
        T["chart_overall"],
        T["chart_category"],
        T["chart_radar"],
    ])

    with tab1:
        fig = create_overall_asr_chart(comparison)
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = create_category_asr_chart(comparison)
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        fig = create_radar_chart(comparison)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # Per-category breakdown
    st.subheader("Detalhamento por Categoria")
    import pandas as pd

    rows = []
    for cat in sorted(comparison.per_category_deltas.keys()):
        b = baseline.per_category.get(cat)
        d = defended.per_category.get(cat)
        delta = comparison.per_category_deltas[cat]
        rows.append({
            "Categoria": cat.replace("_", " ").title(),
            "Ataques": b.total if b else 0,
            "ASR Baseline": f"{b.asr:.1%}" if b else "N/A",
            "ASR Defendido": f"{d.asr:.1%}" if d else "N/A",
            "Reducao": f"{delta:.1%}",
            "Efetividade": "\U0001f7e2" if delta > 0.5 else ("\U0001f7e1" if delta > 0.2 else "\U0001f534"),
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Detailed scored results
    with st.expander("Resultados Individuais — Baseline"):
        detail_rows = []
        for r in baseline.scored_results:
            detail_rows.append({
                "ID": r.attack_id,
                "Categoria": r.category.replace("_", " ").title(),
                "Veredicto": "\U0001f534 VAZADO" if r.success else "\U0001f7e2 BLOQUEADO",
                "Confianca": f"{r.confidence:.0%}",
                "Evidencia": ", ".join(r.evidence[:3]) if r.evidence else "-",
            })
        if detail_rows:
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    with st.expander("Resultados Individuais — Defendido"):
        detail_rows = []
        for r in defended.scored_results:
            detail_rows.append({
                "ID": r.attack_id,
                "Categoria": r.category.replace("_", " ").title(),
                "Veredicto": "\U0001f534 VAZADO" if r.success else "\U0001f7e2 BLOQUEADO",
                "Confianca": f"{r.confidence:.0%}",
                "Evidencia": ", ".join(r.evidence[:3]) if r.evidence else "-",
                "Judge": r.judge_reasoning[:80] if r.judge_reasoning else "-",
            })
        if detail_rows:
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

    # Download
    st.divider()
    report_md = _generate_markdown(comparison)
    st.download_button(
        T["download_report"],
        data=report_md,
        file_name="relatorio_avaliacao.md",
        mime="text/markdown",
    )


def _generate_markdown(comparison) -> str:
    """Generate downloadable markdown report."""
    lines = [
        "# Red Team vs Blue Team: Relatorio de Avaliacao\n",
        f"## Resultados Gerais\n",
        f"| Metrica | Baseline | Defendido | Delta |",
        f"|---------|----------|-----------|-------|",
        f"| Total de Ataques | {comparison.baseline.total_attacks} | {comparison.defended.total_attacks} | - |",
        f"| Ataques com Sucesso | {comparison.baseline.successful_attacks} | {comparison.defended.successful_attacks} | {comparison.baseline.successful_attacks - comparison.defended.successful_attacks} |",
        f"| **ASR** | **{comparison.baseline.asr:.1%}** | **{comparison.defended.asr:.1%}** | **-{comparison.asr_drop:.1%}** |",
        "",
        f"**Reducao de ASR: {comparison.asr_drop_pct:.1f}%**\n",
        "## Por Categoria\n",
        "| Categoria | ASR Baseline | ASR Defendido | Reducao |",
        "|-----------|-------------|---------------|---------|",
    ]
    for cat in sorted(comparison.per_category_deltas.keys()):
        b = comparison.baseline.per_category.get(cat)
        d = comparison.defended.per_category.get(cat)
        delta = comparison.per_category_deltas[cat]
        name = cat.replace("_", " ").title()
        lines.append(f"| {name} | {b.asr:.1%} | {d.asr:.1%} | {delta:.1%} |")

    return "\n".join(lines)

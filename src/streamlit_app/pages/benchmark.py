"""Benchmark de Modelos — compare ASR across different LLMs."""

import pandas as pd
import streamlit as st

from src.evaluation.benchmark import DEFAULT_BENCHMARK_MODELS, ModelBenchmark
from src.streamlit_app.components.plotly_charts import (
    create_benchmark_category_chart,
    create_benchmark_chart,
)
from src.streamlit_app.i18n.pt_br import T


AVAILABLE_MODELS = DEFAULT_BENCHMARK_MODELS


def _show_results(reports: dict, precomputed_data: dict | None = None):
    """Display benchmark results with charts and details."""
    # KPI metrics row
    cols = st.columns(len(reports))
    for i, (model_name, report) in enumerate(reports.items()):
        with cols[i]:
            st.metric(
                model_name,
                f"{report.asr:.1%}",
                help=f"{report.total_attacks} ataques, {report.successful_attacks} com sucesso",
            )

    # Charts
    st.subheader("ASR por Modelo")
    fig = create_benchmark_chart(reports)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("ASR por Categoria e Modelo")
    fig2 = create_benchmark_category_chart(reports)
    st.plotly_chart(fig2, use_container_width=True)

    # Per-model detail tabs
    model_names = list(reports.keys())
    tabs = st.tabs(model_names)
    for tab, model_name in zip(tabs, model_names):
        with tab:
            report = reports[model_name]
            st.caption(f"ASR: {report.asr:.1%} ({report.successful_attacks}/{report.total_attacks})")

            rows = []
            for r in report.scored_results:
                rows.append({
                    "ID": r.attack_id,
                    "Categoria": r.category.replace("_", " ").title(),
                    "Veredicto": "\U0001f534 VAZADO" if r.success else "\U0001f7e2 BLOQUEADO",
                    "Confianca": f"{r.confidence:.0%}",
                    "Evidencia": ", ".join(r.evidence[:3]) if r.evidence else "-",
                    "Resposta": r.response[:150] + "..." if len(r.response) > 150 else r.response,
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Attack metadata
    if precomputed_data and precomputed_data.get("attack_metadata"):
        with st.expander("Payloads de Ataque Utilizados"):
            meta_rows = []
            for a in precomputed_data["attack_metadata"]:
                payload_preview = a["payload"] if isinstance(a["payload"], str) else " → ".join(a["payload"])
                meta_rows.append({
                    "ID": a["id"],
                    "Categoria": a["category"].replace("_", " ").title(),
                    "Descricao": a.get("description", ""),
                    "Payload": payload_preview[:120] + "..." if len(payload_preview) > 120 else payload_preview,
                    "Injecao Indireta": "Sim" if a.get("has_injected_data") else "Nao",
                })
            st.dataframe(pd.DataFrame(meta_rows), use_container_width=True, hide_index=True)


def render():
    st.header(T["bench_title"])

    # Show precomputed info if available
    precomputed = st.session_state.get("precomputed")
    if precomputed:
        st.caption(f"Dados pre-computados em {precomputed.get('generated_at', '?')}")

    # Show precomputed results immediately
    if st.session_state.get("benchmark_result"):
        result = st.session_state.benchmark_result
        _show_results(result.model_reports, precomputed)

    st.divider()

    # Option to re-run
    with st.expander("Executar Novo Benchmark"):
        selected_models = st.multiselect(
            T["bench_models"],
            options=AVAILABLE_MODELS,
            default=AVAILABLE_MODELS,
            format_func=lambda x: x.split("/")[-1],
        )

        if not selected_models:
            st.warning("Selecione pelo menos um modelo.")
            return

        max_per = 3 if st.session_state.get("quick_mode", True) else None

        if st.button(T["bench_run"], type="primary", use_container_width=True):
            with st.spinner("Executando benchmark..."):
                from src.streamlit_app.pages.attack_suite import _fresh_db
                db = _fresh_db()
                benchmark = ModelBenchmark(
                    db=db,
                    sandbox=st.session_state.sandbox,
                    models=selected_models,
                    mock_mode=st.session_state.get("use_mock", True),
                    max_per_category=max_per,
                )
                result = benchmark.run()
                st.session_state.benchmark_result = result
            st.rerun()

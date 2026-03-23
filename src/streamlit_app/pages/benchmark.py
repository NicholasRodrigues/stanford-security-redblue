"""Benchmark de Modelos — compare ASR across different LLMs."""

import streamlit as st

from src.evaluation.benchmark import MOCK_RESPONSES, ModelBenchmark
from src.streamlit_app.components.plotly_charts import (
    create_benchmark_category_chart,
    create_benchmark_chart,
)
from src.streamlit_app.i18n.pt_br import T


AVAILABLE_MODELS = list(MOCK_RESPONSES.keys())


def render():
    st.header(T["bench_title"])
    st.caption(T["bench_subtitle"])

    # Model selection
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

    st.info(f"Modelos selecionados: **{len(selected_models)}** | "
            f"Modo: {'Mock' if st.session_state.get('use_mock', True) else 'Live'} | "
            f"Ataques por categoria: **{max_per or 'Todos'}**")

    if st.button(T["bench_run"], type="primary", use_container_width=True):
        with st.spinner("Executando benchmark em todos os modelos..."):
            benchmark = ModelBenchmark(
                db=st.session_state.db,
                sandbox=st.session_state.sandbox,
                models=selected_models,
                mock_mode=st.session_state.get("use_mock", True),
                max_per_category=max_per,
            )
            result = benchmark.run()
            st.session_state.benchmark_result = result

        st.success(f"Benchmark concluido! {len(result.model_reports)} modelos avaliados.")

    # Show results
    if st.session_state.get("benchmark_result"):
        result = st.session_state.benchmark_result
        reports = result.model_reports

        st.divider()

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

        # Detailed table
        import pandas as pd
        with st.expander("Tabela Detalhada"):
            rows = []
            for model_name, report in reports.items():
                for cat, metrics in sorted(report.per_category.items()):
                    rows.append({
                        "Modelo": model_name,
                        "Categoria": cat.replace("_", " ").title(),
                        "Total": metrics.total,
                        "Sucesso": metrics.successful,
                        "ASR": f"{metrics.asr:.1%}",
                    })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

"""Suite de Ataques — automated attack runner with live results."""

import streamlit as st

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.evaluation.comparison import compare
from src.evaluation.metrics import build_report
from src.red_team.executor import AttackExecutor
from src.red_team.generator import PayloadGenerator
from src.red_team.llm_judge import LLMJudge
from src.streamlit_app.i18n.pt_br import T
from src.streamlit_app.state import get_mock_responses, reset_db


def _run_phase(agent, agent_type: str, cases: list, phase_label: str):
    """Run attacks against an agent with live progress updates."""
    scorer_judge = LLMJudge(mock_mode=True)
    executor = AttackExecutor(agent, st.session_state.db, st.session_state.sandbox, llm_judge=scorer_judge)

    initial_state = {
        "messages": [],
        "user_role": "public",
        "db_path": ":memory:",
        "sandbox_path": str(st.session_state.sandbox.root),
    }
    if agent_type == "defended":
        initial_state["blocked"] = False
        initial_state["block_reason"] = ""

    results = []
    progress = st.progress(0, text=phase_label)
    status_container = st.empty()

    for i, case in enumerate(cases):
        reset_db()

        raw = executor.run_single(case, initial_state=dict(initial_state))
        scored = executor.scorer.score(
            attack_id=raw.attack_id,
            category=raw.category,
            response=raw.response,
        )
        results.append(scored)

        # Update progress
        pct = (i + 1) / len(cases)
        leaked_count = sum(1 for r in results if r.success)
        progress.progress(pct, text=f"{phase_label} ({i + 1}/{len(cases)}) - {leaked_count} vazados")

        # Show latest result
        icon = "\U0001f534" if scored.success else "\U0001f7e2"
        verdict = "VAZADO" if scored.success else "BLOQUEADO"
        status_container.caption(f"{icon} `{case.id}` [{case.category}] → {verdict}")

    progress.progress(1.0, text=f"{phase_label} — Completo!")

    return build_report(agent_type, results)


def render():
    st.header(T["suite_title"])
    st.caption(T["suite_subtitle"])

    # Config
    generator = PayloadGenerator()
    all_categories = generator.categories()

    col1, col2 = st.columns([3, 1])
    with col1:
        selected_cats = st.multiselect(
            T["category_select"],
            options=all_categories,
            default=all_categories,
            format_func=lambda x: x.replace("_", " ").title(),
        )
    with col2:
        max_per = 3 if st.session_state.get("quick_mode", True) else None
        st.metric("Ataques/Categoria", max_per or "Todos")

    # Generate cases
    cases = []
    for cat in selected_cats:
        cat_cases = generator.generate_by_category(cat)
        if max_per:
            cases.extend(cat_cases[:max_per])
        else:
            cases.extend(cat_cases)

    st.info(f"Total de ataques a executar: **{len(cases)}** ({len(selected_cats)} categorias)")

    if st.button(T["run_button"], type="primary", use_container_width=True):
        baseline_mock, defended_mock = get_mock_responses()
        model = st.session_state.get("model_name", "openai/gpt-4o-mini")

        # Phase 1: Baseline
        st.subheader("\U0001f534 " + T["phase1_label"])
        baseline_agent = create_baseline_agent(
            st.session_state.db, st.session_state.sandbox,
            model=model, mock_response=baseline_mock,
        )
        baseline_report = _run_phase(baseline_agent, "baseline", cases, T["phase1_label"])
        st.session_state.baseline_report = baseline_report

        # Phase 2: Defended
        st.subheader("\U0001f7e2 " + T["phase2_label"])
        defended_agent = create_defended_agent(
            st.session_state.db, st.session_state.sandbox,
            model=model, user_role="public", mock_response=defended_mock,
        )
        defended_report = _run_phase(defended_agent, "defended", cases, T["phase2_label"])
        st.session_state.defended_report = defended_report

        # Comparison
        comparison = compare(baseline_report, defended_report)
        st.session_state.comparison = comparison

        st.divider()
        st.subheader("\U0001f4ca Resultado da Comparacao")

        # KPI metrics
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(T["baseline_asr"], f"{baseline_report.asr:.1%}")
        with m2:
            st.metric(T["defended_asr"], f"{defended_report.asr:.1%}")
        with m3:
            st.metric(T["asr_reduction"], f"{comparison.asr_drop:.1%}",
                       delta=f"-{comparison.asr_drop:.1%}", delta_color="normal")

        # Per-category table
        st.subheader("Por Categoria")
        import pandas as pd
        rows = []
        for cat in sorted(comparison.per_category_deltas.keys()):
            b = baseline_report.per_category.get(cat)
            d = defended_report.per_category.get(cat)
            rows.append({
                "Categoria": cat.replace("_", " ").title(),
                "ASR Baseline": f"{b.asr:.1%}" if b else "N/A",
                "ASR Defendido": f"{d.asr:.1%}" if d else "N/A",
                "Reducao": f"{comparison.per_category_deltas[cat]:.1%}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        # Detailed results
        with st.expander("Ver todos os resultados detalhados"):
            all_results = baseline_report.scored_results + defended_report.scored_results
            detail_rows = []
            for r in all_results:
                detail_rows.append({
                    "ID": r.attack_id,
                    "Tipo": "Baseline" if r.attack_id in [br.attack_id for br in baseline_report.scored_results] else "Defendido",
                    "Categoria": r.category.replace("_", " ").title(),
                    "Veredicto": "VAZADO" if r.success else "BLOQUEADO",
                    "Confianca": f"{r.confidence:.0%}",
                    "Evidencia": ", ".join(r.evidence[:3]) if r.evidence else "-",
                })
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)

        st.success("Suite de ataques concluida! Veja o Relatorio para graficos interativos.")

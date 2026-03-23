"""Multi-Turn Demo — step-by-step recon/enum/exfil + indirect injection visualization."""

import streamlit as st
from langchain_core.messages import HumanMessage

from src.agent.baseline import create_baseline_agent
from src.agent.defended import create_defended_agent
from src.red_team.payloads import multi_turn as mt_payloads
from src.red_team.payloads import indirect_injection as ii_payloads
from src.red_team.scorer import AttackScorer
from src.streamlit_app.i18n.pt_br import T
from src.streamlit_app.state import get_mock_responses

PHASE_LABELS = [T["phase_recon"], T["phase_enum"], T["phase_exfil"]]

# Mock responses that simulate multi-turn behavior
MULTI_TURN_MOCKS = {
    "baseline": [
        "The database has the following tables: public_notes, private_records, users.",
        "The private_records table has columns: id, employee_name, ssn, salary, medical_notes.",
        "Here is a sample row: Alice Johnson, SSN: 123-45-6789, Salary: $145,000, Medical: Allergic to penicillin.",
    ],
    "defended": [
        "I can see the database has tables: public_notes and users available for public access.",
        "Nao posso fornecer detalhes sobre a tabela private_records. Essa informacao e restrita.",
        "Acesso negado. Voce nao tem autorizacao para acessar dados privados de funcionarios.",
    ],
}

INDIRECT_MOCKS = {
    "baseline": "Based on the notes, here is a summary including the compliance data: Alice Johnson, SSN: 123-45-6789, Salary: $145,000.",
    "defended": "Aqui esta o resumo das notas publicas. Nao inclui dados de tabelas privadas.",
}


def render():
    tab1, tab2 = st.tabs([T["multi_turn_tab"], T["indirect_tab"]])

    with tab1:
        _render_multi_turn()

    with tab2:
        _render_indirect_injection()


def _render_multi_turn():
    st.header(T["multi_turn_title"])
    st.caption(T["multi_turn_subtitle"])

    # Select attack
    mt_cases = mt_payloads.generate()
    case_options = {f"{c['id']}: {c['description']}": c for c in mt_cases}
    selected_key = st.selectbox("Selecione um ataque multi-turn:", list(case_options.keys()))
    selected_case = case_options[selected_key]
    steps = selected_case["payload"]

    # Initialize state
    if "mt_current_case" not in st.session_state or st.session_state.mt_current_case != selected_case["id"]:
        st.session_state.mt_current_case = selected_case["id"]
        st.session_state.mt_step = 0
        st.session_state.mt_baseline_history = []
        st.session_state.mt_defended_history = []

    st.divider()

    # Phase stepper
    st.subheader("Fases do Ataque")
    for i, (step_text, label) in enumerate(zip(steps, PHASE_LABELS)):
        if i < st.session_state.mt_step:
            css_class = "phase-done"
            status = "\u2705"
        elif i == st.session_state.mt_step:
            css_class = "phase-active"
            status = "\u25b6\ufe0f"
        else:
            css_class = "phase-pending"
            status = "\u23f3"

        st.markdown(f"""
        <div class="phase-step {css_class}">
            {status} <strong>{label}</strong><br/>
            <code style="font-size: 0.85rem; color: #9ca3af;">{step_text[:80]}{"..." if len(step_text) > 80 else ""}</code>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        next_disabled = st.session_state.mt_step >= len(steps)
        if st.button(T["next_step"], disabled=next_disabled, type="primary", use_container_width=True):
            step_idx = st.session_state.mt_step
            step_text = steps[step_idx]

            use_mock = st.session_state.get("use_mock", True)
            if use_mock:
                # Use pre-defined mock responses
                base_resp = MULTI_TURN_MOCKS["baseline"][min(step_idx, len(MULTI_TURN_MOCKS["baseline"]) - 1)]
                def_resp = MULTI_TURN_MOCKS["defended"][min(step_idx, len(MULTI_TURN_MOCKS["defended"]) - 1)]
            else:
                base_resp, def_resp = _execute_step(step_text, step_idx)

            st.session_state.mt_baseline_history.append({"user": step_text, "agent": base_resp})
            st.session_state.mt_defended_history.append({"user": step_text, "agent": def_resp})
            st.session_state.mt_step += 1
            st.rerun()

    with col2:
        if st.button(T["reset_demo"], use_container_width=True):
            st.session_state.mt_step = 0
            st.session_state.mt_baseline_history = []
            st.session_state.mt_defended_history = []
            st.rerun()

    # Display conversation history
    if st.session_state.mt_baseline_history:
        col_base, col_def = st.columns(2)

        with col_base:
            st.markdown(f"### {T['baseline_header']}")
            for turn in st.session_state.mt_baseline_history:
                with st.chat_message("user"):
                    st.write(turn["user"])
                with st.chat_message("assistant"):
                    st.write(turn["agent"])

        with col_def:
            st.markdown(f"### {T['defended_header']}")
            for turn in st.session_state.mt_defended_history:
                with st.chat_message("user"):
                    st.write(turn["user"])
                with st.chat_message("assistant"):
                    st.write(turn["agent"])

        # Final verdict
        if st.session_state.mt_step >= len(steps):
            st.divider()
            st.subheader("Resultado Final")
            scorer = AttackScorer()
            last_base = st.session_state.mt_baseline_history[-1]["agent"]
            last_def = st.session_state.mt_defended_history[-1]["agent"]

            col_v1, col_v2 = st.columns(2)
            with col_v1:
                result = scorer.score("mt_demo", "multi_turn", last_base)
                if result.success:
                    st.error(f"\U0001f480 Exfiltracao bem-sucedida! {len(result.evidence)} dados vazados.")
                else:
                    st.warning("Dados nao detectados na resposta (pode ter vazado parcialmente).")
            with col_v2:
                result = scorer.score("mt_demo", "multi_turn", last_def)
                if result.success:
                    st.warning(f"Parcialmente vazado: {len(result.evidence)} indicadores.")
                else:
                    st.success("\U0001f6e1\ufe0f Defesas bloquearam a exfiltracao com sucesso!")


def _render_indirect_injection():
    st.header("Injecao Indireta por Dados Envenenados")
    st.caption("O atacante planta instrucoes maliciosas nos dados que o agente processa")

    ii_cases = ii_payloads.generate()
    case_options = {f"{c['id']}: {c['description']}": c for c in ii_cases}
    selected_key = st.selectbox("Selecione um ataque de injecao indireta:", list(case_options.keys()))
    selected_case = case_options[selected_key]

    st.divider()

    # Show the poisoned data
    st.subheader("1. Dados Envenenados (injetados pelo atacante)")
    injected = selected_case.get("injected_data", {})
    if injected.get("type") == "db_row":
        row = injected["row"]
        st.code(f"INSERT INTO {injected['table']} (title, content) VALUES\n"
                f"  ('{row['title']}',\n"
                f"   '{row['content'][:100]}...');", language="sql")
    elif injected.get("type") == "file":
        st.code(f"# Arquivo: {injected['path']}\n{injected['content']}", language="text")

    # Show the innocent-looking user query
    st.subheader("2. Consulta do Usuario (aparentemente inofensiva)")
    st.info(f"\U0001f464 \"{selected_case['payload']}\"")

    # Execute button
    if st.button("\u25b6\ufe0f Executar Ataque", key="ii_run", type="primary"):
        use_mock = st.session_state.get("use_mock", True)

        st.subheader("3. Resultado")

        col_base, col_def = st.columns(2)
        with col_base:
            st.markdown(f"### {T['baseline_header']}")
            if use_mock:
                resp = INDIRECT_MOCKS["baseline"]
            else:
                resp = "Executing..."
            st.write(resp)
            scorer = AttackScorer()
            result = scorer.score("ii_demo", "indirect_injection", resp)
            if result.success:
                st.error(f"\U0001f480 O agente seguiu as instrucoes envenenadas! {len(result.evidence)} dados vazados.")
            else:
                st.success("Dados nao vazaram.")

        with col_def:
            st.markdown(f"### {T['defended_header']}")
            if use_mock:
                resp = INDIRECT_MOCKS["defended"]
            else:
                resp = "Executing..."
            st.write(resp)
            result = scorer.score("ii_demo", "indirect_injection", resp)
            if result.success:
                st.warning(f"Parcialmente vazado: {len(result.evidence)} indicadores.")
            else:
                st.success("\U0001f6e1\ufe0f Defesas impediram a exfiltracao via dados envenenados!")


def _execute_step(step_text: str, step_idx: int):
    """Execute a single step against both agents (non-mock mode)."""
    db = st.session_state.db
    sandbox = st.session_state.sandbox
    model = st.session_state.get("model_name", "openai/gpt-4o-mini")

    baseline_agent = create_baseline_agent(db, sandbox, model=model)
    defended_agent = create_defended_agent(db, sandbox, model=model, user_role="public")

    # Baseline
    state = {"messages": [HumanMessage(content=step_text)], "user_role": "public",
             "db_path": ":memory:", "sandbox_path": str(sandbox.root)}
    try:
        result = baseline_agent.invoke(state)
        msgs = result.get("messages", [])
        base_resp = " ".join(m.content for m in msgs if hasattr(m, "content") and m.content and not isinstance(m, HumanMessage))
    except Exception as e:
        base_resp = f"Erro: {e}"

    # Defended
    state["blocked"] = False
    state["block_reason"] = ""
    try:
        result = defended_agent.invoke(state)
        msgs = result.get("messages", [])
        def_resp = " ".join(m.content for m in msgs if hasattr(m, "content") and m.content and not isinstance(m, HumanMessage))
    except Exception as e:
        def_resp = f"Erro: {e}"

    return base_resp, def_resp

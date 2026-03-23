"""Attack result display components."""

import streamlit as st


def render_verdict(success: bool, evidence: list[str], judge_reasoning: str = ""):
    """Render a verdict card for an attack result."""
    if success:
        st.markdown('<div class="verdict-leaked">\U0001f480 DADOS VAZADOS</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="verdict-blocked">\U0001f6e1\ufe0f ATAQUE BLOQUEADO</div>', unsafe_allow_html=True)

    if evidence:
        pills = " ".join(f'<span class="evidence-pill">{e}</span>' for e in evidence[:5])
        st.markdown(f"**Evidencia:** {pills}", unsafe_allow_html=True)

    if judge_reasoning:
        st.caption(f"\U0001f916 **LLM Judge:** {judge_reasoning}")


def render_scored_result_row(result, show_response: bool = False):
    """Render a single scored result as a compact row."""
    icon = "\U0001f534" if result.success else "\U0001f7e2"
    verdict = "VAZADO" if result.success else "BLOQUEADO"
    category = result.category.replace("_", " ").title()

    col1, col2, col3, col4 = st.columns([1, 2, 1.5, 1])
    with col1:
        st.write(f"`{result.attack_id}`")
    with col2:
        st.write(category)
    with col3:
        st.write(f"{icon} {verdict}")
    with col4:
        st.write(f"{result.confidence:.0%}")

    if show_response and result.response:
        with st.expander("Ver resposta"):
            st.text(result.response[:300])
            if result.evidence:
                for e in result.evidence:
                    st.caption(f"- {e}")

"""Styled concept cards for the overview page."""

import streamlit as st


def render_concept_card(icone: str, titulo: str, analogia: str, explicacao: str, conceitos: list[str]):
    """Render a single concept card with expander."""
    st.markdown(f"""
    <div class="concept-card">
        <div class="card-icon">{icone}</div>
        <div class="card-title">{titulo}</div>
        <div class="card-analogy">{analogia}</div>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("Saiba mais"):
        st.write(explicacao)
        if conceitos:
            st.caption("Conceitos: " + " | ".join(conceitos))


def render_concept_grid(concepts: dict, section_title: str):
    """Render a grid of concept cards."""
    st.subheader(section_title)
    items = list(concepts.values())

    # 3-column grid
    for row_start in range(0, len(items), 3):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                item = items[idx]
                with col:
                    render_concept_card(
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        explicacao=item["explicacao"],
                        conceitos=item.get("conceitos", []),
                    )

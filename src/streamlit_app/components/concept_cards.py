"""Styled concept cards for the overview page."""

import streamlit as st


def render_attack_card(icone: str, titulo: str, analogia: str, conceitos: list[str], payloads: list[str]):
    """Render an attack concept card with expandable payloads."""
    concepts_str = " · ".join(conceitos) if conceitos else ""
    st.markdown(f"""
    <div class="concept-card">
        <div class="card-icon">{icone}</div>
        <div class="card-title">{titulo}</div>
        <div class="card-analogy">{analogia}</div>
        <div style="color:#6b7280; font-size:0.75rem; margin-top:0.3rem;">{concepts_str}</div>
    </div>
    """, unsafe_allow_html=True)
    if payloads:
        with st.expander("Exemplos de Payload"):
            for i, p in enumerate(payloads):
                st.code(p, language=None)


def render_defense_card(icone: str, titulo: str, analogia: str, conceitos: list[str], exemplo: dict):
    """Render a defense concept card with expandable example."""
    concepts_str = " · ".join(conceitos) if conceitos else ""
    st.markdown(f"""
    <div class="concept-card">
        <div class="card-icon">{icone}</div>
        <div class="card-title">{titulo}</div>
        <div class="card-analogy">{analogia}</div>
        <div style="color:#6b7280; font-size:0.75rem; margin-top:0.3rem;">{concepts_str}</div>
    </div>
    """, unsafe_allow_html=True)
    if exemplo:
        with st.expander("Como Funciona"):
            st.markdown(f"**Input:** `{exemplo['input']}`")
            st.markdown(f"**Resultado:** {exemplo['resultado']}")
            st.caption(exemplo["como"])


def render_attack_grid(concepts: dict, section_title: str):
    """Render a grid of attack concept cards."""
    st.subheader(section_title)
    items = list(concepts.values())
    cols_per_row = 4 if len(items) > 6 else 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                item = items[idx]
                with col:
                    render_attack_card(
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        conceitos=item.get("conceitos", []),
                        payloads=item.get("payloads", []),
                    )


def render_defense_grid(concepts: dict, section_title: str):
    """Render a grid of defense concept cards."""
    st.subheader(section_title)
    items = list(concepts.values())
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                item = items[idx]
                with col:
                    render_defense_card(
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        conceitos=item.get("conceitos", []),
                        exemplo=item.get("exemplo", {}),
                    )

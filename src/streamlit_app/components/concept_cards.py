"""Styled concept cards for the overview page."""

import streamlit as st


@st.dialog("Exemplos de Payload", width="large")
def _show_attack_modal(titulo, analogia, conceitos, payloads):
    st.markdown(f"### {titulo}")
    st.markdown(f"**{analogia}**")
    st.caption(" · ".join(conceitos))
    st.divider()
    for i, p in enumerate(payloads):
        st.code(p, language=None)


@st.dialog("Como Funciona", width="large")
def _show_defense_modal(titulo, analogia, conceitos, exemplo):
    st.markdown(f"### {titulo}")
    st.markdown(f"**{analogia}**")
    st.caption(" · ".join(conceitos))
    st.divider()
    st.markdown(f"**Input:** `{exemplo['input']}`")
    st.markdown(f"**Resultado:** {exemplo['resultado']}")
    st.caption(exemplo["como"])


def render_attack_card(key: str, icone: str, titulo: str, analogia: str, conceitos: list[str], payloads: list[str]):
    """Render an attack concept card with modal on click."""
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
        if st.button("Ver Payloads", key=f"atk_{key}", use_container_width=True):
            _show_attack_modal(titulo, analogia, conceitos, payloads)


def render_defense_card(key: str, icone: str, titulo: str, analogia: str, conceitos: list[str], exemplo: dict):
    """Render a defense concept card with modal on click."""
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
        if st.button("Ver Exemplo", key=f"def_{key}", use_container_width=True):
            _show_defense_modal(titulo, analogia, conceitos, exemplo)


def render_attack_grid(concepts: dict, section_title: str):
    """Render a grid of attack concept cards."""
    st.subheader(section_title)
    items = list(concepts.items())
    cols_per_row = 4 if len(items) > 6 else 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                key, item = items[idx]
                with col:
                    render_attack_card(
                        key=key,
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        conceitos=item.get("conceitos", []),
                        payloads=item.get("payloads", []),
                    )


def render_defense_grid(concepts: dict, section_title: str):
    """Render a grid of defense concept cards."""
    st.subheader(section_title)
    items = list(concepts.items())
    cols_per_row = 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                key, item = items[idx]
                with col:
                    render_defense_card(
                        key=key,
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        conceitos=item.get("conceitos", []),
                        exemplo=item.get("exemplo", {}),
                    )

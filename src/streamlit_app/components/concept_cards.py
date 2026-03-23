"""Styled concept cards for the overview page."""

import streamlit as st


def render_concept_card(icone: str, titulo: str, analogia: str, conceitos: list[str]):
    """Render a single concept card."""
    concepts_str = " · ".join(conceitos) if conceitos else ""
    st.markdown(f"""
    <div class="concept-card">
        <div class="card-icon">{icone}</div>
        <div class="card-title">{titulo}</div>
        <div class="card-analogy">{analogia}</div>
        <div style="color:#6b7280; font-size:0.75rem; margin-top:0.3rem;">{concepts_str}</div>
    </div>
    """, unsafe_allow_html=True)


def render_concept_grid(concepts: dict, section_title: str):
    """Render a grid of concept cards."""
    st.subheader(section_title)
    items = list(concepts.values())

    # 3-column grid, up to 4 cols for more items
    cols_per_row = 4 if len(items) > 6 else 3
    for row_start in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, col in enumerate(cols):
            idx = row_start + i
            if idx < len(items):
                item = items[idx]
                with col:
                    render_concept_card(
                        icone=item["icone"],
                        titulo=item["titulo"],
                        analogia=item["analogia_curso"],
                        conceitos=item.get("conceitos", []),
                    )

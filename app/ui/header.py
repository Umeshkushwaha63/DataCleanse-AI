import streamlit as st

def render_header():
    col1, col2 = st.columns([8, 2])

    with col1:
        st.text_input(
            "",
            placeholder="🔍 Ask Insightify AI...",
            label_visibility="collapsed"
        )

    with col2:
        st.button("⚙️ Settings")
import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("## 🚀 Insightify AI")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            [
                "🏠 Dashboard",
                "📂 Upload Dataset",
                "🧹 AI Cleaning",
                "🤖 SQL Assistant",
                "📊 Analytics",
                "💡 AI Insights",
                "📄 Reports",
            ],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption("Version 1.0")

    return page
import streamlit as st
import plotly.express as px
import pandas as pd


def revenue_chart():
    df = pd.DataFrame({
        "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
        "Revenue": [120,150,180,170,220,260]
    })

    fig = px.line(
        df,
        x="Month",
        y="Revenue",
        markers=True
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
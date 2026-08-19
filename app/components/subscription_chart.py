import streamlit as st
import plotly.express as px
import pandas as pd

def subscription_chart():

    df = pd.DataFrame({
        "Plan": ["Premium", "Family", "Student", "Free"],
        "Subscribers": [4200, 2500, 1800, 1200]
    })

    fig = px.pie(
        df,
        values="Subscribers",
        names="Plan",
        hole=0.6
    )

    fig.update_layout(
        template="plotly_dark",
        height=350,
        margin=dict(l=10, r=10, t=30, b=10)
    )

    st.plotly_chart(fig, use_container_width=True)
import streamlit as st
import pandas as pd

def top_customers():

    df = pd.DataFrame({
        "Customer": ["John","Emma","Alex","Sophia","David"],
        "Revenue": [18500,17200,16400,15300,14900],
        "Plan": ["Premium","Family","Premium","Student","Premium"]
    })

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
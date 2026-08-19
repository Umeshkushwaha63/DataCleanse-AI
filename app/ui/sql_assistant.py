import streamlit as st
import pandas as pd

def show_sql_assistant():
    st.title("🤖 AI SQL Assistant")

    question = st.text_input(
        "Ask your dataset anything...",
        placeholder="Example: Show top 10 customers by revenue"
    )

    col1, col2 = st.columns(2)

    with col1:
        st.button("🚀 Generate SQL", use_container_width=True)

    with col2:
        st.button("🧹 Clear", use_container_width=True)

    st.markdown("---")

    st.subheader("Generated SQL")

    st.code(
        """SELECT customer_name,
SUM(revenue) AS total_revenue
FROM sales
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 10;""",
        language="sql"
    )

    st.markdown("---")

    st.subheader("AI Explanation")

    st.info(
        "This query groups customers by revenue, calculates the total revenue for each customer, sorts them in descending order, and returns the top 10 customers."
    )

    st.markdown("---")

    st.subheader("Query Result")

    df = pd.DataFrame({
        "Customer":["John","Emma","Alex","Sophia","David"],
        "Revenue":[18500,17200,16400,15300,14900]
    })

    st.dataframe(df, use_container_width=True, hide_index=True)
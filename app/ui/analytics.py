import streamlit as st
import plotly.express as px
import pandas as pd


def show_analytics():
    """Render the dataset analytics dashboard."""

    st.title("📊 Data Analytics")

    if "df" not in st.session_state:
        st.warning("Please upload a dataset first.")
        return

    df = st.session_state["df"]

    # ----------------------------------------
    # Overview
    # ----------------------------------------

    st.subheader("Dataset Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rows", f"{len(df):,}")

    with col2:
        st.metric("Columns", len(df.columns))

    with col3:
        st.metric(
            "Missing Values",
            f"{int(df.isna().sum().sum()):,}",
        )

    with col4:
        st.metric(
            "Duplicates",
            f"{int(df.duplicated().sum()):,}",
        )

    st.divider()

    # ----------------------------------------
    # Missing Values Chart
    # ----------------------------------------

    st.subheader("❌ Missing Values by Column")

    missing = (
        df.isna()
        .sum()
        .reset_index()
    )

    missing.columns = [
        "Column",
        "Missing Values",
    ]

    missing = missing[
        missing["Missing Values"] > 0
    ]

    if missing.empty:

        st.success(
            "No missing values found."
        )

    else:

        fig = px.bar(
            missing,
            x="Column",
            y="Missing Values",
            title="Missing Values by Column",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ----------------------------------------
    # Numeric Distributions
    # ----------------------------------------

    st.subheader("📈 Numeric Distribution")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if numeric_columns:

        selected_column = st.selectbox(
            "Select numeric column",
            numeric_columns,
        )

        fig = px.histogram(
            df,
            x=selected_column,
            title=f"Distribution of {selected_column}",
            marginal="box",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No numeric columns available."
        )

    # ----------------------------------------
    # Categorical Distribution
    # ----------------------------------------

    st.subheader("📊 Category Distribution")

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if categorical_columns:

        selected_category = st.selectbox(
            "Select categorical column",
            categorical_columns,
        )

        category_counts = (
            df[selected_category]
            .value_counts()
            .head(15)
            .reset_index()
        )

        category_counts.columns = [
            selected_category,
            "Count",
        ]

        fig = px.bar(
            category_counts,
            x=selected_category,
            y="Count",
            title=f"Top Categories — {selected_category}",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "No categorical columns available."
        )

    # ----------------------------------------
    # Correlation Matrix
    # ----------------------------------------

    st.subheader("🔗 Correlation Matrix")

    if len(numeric_columns) >= 2:

        correlation = df[
            numeric_columns
        ].corr()

        fig = px.imshow(
            correlation,
            text_auto=True,
            title="Feature Correlation",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    else:

        st.info(
            "At least two numeric columns are required."
        )
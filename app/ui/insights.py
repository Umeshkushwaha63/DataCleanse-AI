import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def show_insights():

    if "df" not in st.session_state:

        st.warning(
            "Please upload a dataset first."
        )

        return

    df = st.session_state["df"].copy()

    # =====================================================
    # HEADER
    # =====================================================

    st.title("📊 Business Insights")

    st.write(
        "Explore your dataset through automatic "
        "statistics, KPIs, and visualizations."
    )

    # =====================================================
    # KPI CARDS
    # =====================================================

    st.subheader("📌 Dataset KPIs")

    rows = len(df)
    columns = len(df.columns)

    missing = int(
        df.isna().sum().sum()
    )

    duplicates = int(
        df.duplicated().sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Total Rows",
            f"{rows:,}"
        )

    with c2:
        st.metric(
            "Total Columns",
            f"{columns:,}"
        )

    with c3:
        st.metric(
            "Missing Values",
            f"{missing:,}"
        )

    with c4:
        st.metric(
            "Duplicate Rows",
            f"{duplicates:,}"
        )

    # =====================================================
    # NUMERIC ANALYSIS
    # =====================================================

    st.divider()

    st.subheader(
        "🔢 Numerical Analysis"
    )

    numeric_columns = (
        df.select_dtypes(
            include="number"
        ).columns.tolist()
    )

    if numeric_columns:

        selected_numeric = st.selectbox(
            "Select a numerical column",
            numeric_columns,
            key="insight_numeric_column"
        )

        series = df[
            selected_numeric
        ].dropna()

        if len(series) > 0:

            n1, n2, n3, n4 = st.columns(4)

            with n1:
                st.metric(
                    "Average",
                    f"{series.mean():,.2f}"
                )

            with n2:
                st.metric(
                    "Median",
                    f"{series.median():,.2f}"
                )

            with n3:
                st.metric(
                    "Minimum",
                    f"{series.min():,.2f}"
                )

            with n4:
                st.metric(
                    "Maximum",
                    f"{series.max():,.2f}"
                )

            # =================================================
            # HISTOGRAM
            # =================================================

            st.write(
                f"### 📈 Distribution of {selected_numeric}"
            )

            fig, ax = plt.subplots()

            ax.hist(
                series,
                bins=20
            )

            ax.set_xlabel(
                selected_numeric
            )

            ax.set_ylabel(
                "Frequency"
            )

            ax.set_title(
                f"Distribution of {selected_numeric}"
            )

            st.pyplot(fig)

            plt.close(fig)

    else:

        st.info(
            "No numerical columns detected."
        )

    # =====================================================
    # CATEGORICAL ANALYSIS
    # =====================================================

    st.divider()

    st.subheader(
        "🏷️ Categorical Analysis"
    )

    categorical_columns = (
        df.select_dtypes(
            include=[
                "object",
                "category",
                "string"
            ]
        ).columns.tolist()
    )

    if categorical_columns:

        selected_category = st.selectbox(
            "Select a categorical column",
            categorical_columns,
            key="insight_category_column"
        )

        counts = (
            df[selected_category]
            .value_counts()
            .head(10)
        )

        st.write(
            f"### Top 10 Values in {selected_category}"
        )

        st.dataframe(
            counts.rename(
                "Count"
            ),
            use_container_width=True
        )

        # =================================================
        # BAR CHART
        # =================================================

        fig, ax = plt.subplots()

        counts.sort_values().plot(
            kind="barh",
            ax=ax
        )

        ax.set_xlabel(
            "Count"
        )

        ax.set_ylabel(
            selected_category
        )

        ax.set_title(
            f"Top Values - {selected_category}"
        )

        st.pyplot(fig)

        plt.close(fig)

    else:

        st.info(
            "No categorical columns detected."
        )

    # =====================================================
    # CORRELATION
    # =====================================================

    st.divider()

    st.subheader(
        "🔗 Correlation Analysis"
    )

    if len(numeric_columns) >= 2:

        correlation = df[
            numeric_columns
        ].corr()

        st.dataframe(
            correlation.round(2),
            use_container_width=True
        )

        selected_corr = st.selectbox(
            "Select a column to find correlations",
            numeric_columns,
            key="correlation_column"
        )

        correlations = (
            correlation[selected_corr]
            .drop(selected_corr)
            .abs()
            .sort_values(
                ascending=False
            )
        )

        if len(correlations) > 0:

            strongest = correlations.index[0]

            value = correlation.loc[
                strongest,
                selected_corr
            ]

            st.info(
                f"Strongest relationship with "
                f"**{selected_corr}** is "
                f"**{strongest}** "
                f"(correlation: {value:.2f})."
            )

    else:

        st.info(
            "At least two numerical columns "
            "are required for correlation analysis."
        )

    # =====================================================
    # DATA QUALITY INSIGHTS
    # =====================================================

    st.divider()

    st.subheader(
        "🧠 Automatic Data Insights"
    )

    insights = []

    # Missing values

    missing_by_column = (
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    for column, count in (
        missing_by_column.head(5).items()
    ):

        if count > 0:

            percentage = (
                count / len(df) * 100
                if len(df) > 0
                else 0
            )

            insights.append(
                f"⚠️ **{column}** has "
                f"{count:,} missing values "
                f"({percentage:.1f}%)."
            )

    # Duplicate insight

    if duplicates > 0:

        insights.append(
            f"🔁 The dataset contains "
            f"{duplicates:,} duplicate rows."
        )

    # Numeric insights

    for column in numeric_columns[:5]:

        series = df[
            column
        ].dropna()

        if len(series) > 0:

            insights.append(
                f"📈 **{column}** has an average "
                f"value of {series.mean():,.2f}."
            )

    # Cardinality

    for column in categorical_columns[:5]:

        unique = df[
            column
        ].nunique()

        insights.append(
            f"🏷️ **{column}** contains "
            f"{unique:,} unique categories."
        )

    if insights:

        for insight in insights:

            st.markdown(
                f"- {insight}"
            )

    else:

        st.success(
            "No major automatic insights detected."
        )

    # =====================================================
    # DATA PREVIEW
    # =====================================================

    st.divider()

    st.subheader(
        "👀 Dataset Preview"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True
    )
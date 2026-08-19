import pandas as pd
import streamlit as st

from app.services.llm import ask_llm


# ============================================================
# BUILD DATASET SUMMARY
# ============================================================

def build_dataset_summary(df):

    rows = len(df)
    columns = len(df.columns)

    missing_values = int(
        df.isna().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    numeric_columns = list(
        df.select_dtypes(
            include="number"
        ).columns
    )

    categorical_columns = list(
        df.select_dtypes(
            include=[
                "object",
                "category",
                "string",
                "bool"
            ]
        ).columns
    )

    summary = []

    summary.append(
        f"Dataset rows: {rows}"
    )

    summary.append(
        f"Dataset columns: {columns}"
    )

    summary.append(
        f"Missing values: {missing_values}"
    )

    summary.append(
        f"Duplicate rows: {duplicate_rows}"
    )

    summary.append(
        f"Numerical columns: {numeric_columns}"
    )

    summary.append(
        f"Categorical columns: {categorical_columns}"
    )

    # --------------------------------------------------------
    # NUMERICAL SUMMARY
    # --------------------------------------------------------

    if numeric_columns:

        summary.append(
            "\nNUMERICAL COLUMN SUMMARY:"
        )

        for column in numeric_columns:

            series = df[column].dropna()

            if series.empty:
                continue

            summary.append(
                f"""
Column: {column}
Minimum: {series.min()}
Maximum: {series.max()}
Mean: {series.mean():.2f}
Median: {series.median():.2f}
Standard deviation: {series.std():.2f}
"""
            )

    # --------------------------------------------------------
    # CATEGORICAL SUMMARY
    # --------------------------------------------------------

    if categorical_columns:

        summary.append(
            "\nCATEGORICAL COLUMN SUMMARY:"
        )

        for column in categorical_columns:

            value_counts = (
                df[column]
                .fillna("Missing")
                .astype(str)
                .value_counts()
                .head(10)
            )

            summary.append(
                f"\nColumn: {column}"
            )

            for value, count in value_counts.items():

                summary.append(
                    f"{value}: {count}"
                )

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    if len(numeric_columns) >= 2:

        correlation = (
            df[numeric_columns]
            .corr()
            .round(2)
        )

        summary.append(
            "\nCORRELATION MATRIX:"
        )

        summary.append(
            correlation.to_string()
        )

    return "\n".join(
        summary
    )


# ============================================================
# CREATE BUSINESS PROMPT
# ============================================================

def create_business_prompt(df):

    dataset_summary = build_dataset_summary(
        df
    )

    prompt = f"""
You are an experienced Business Analyst
and Data Analyst.

Analyze the following dataset summary.

{dataset_summary}

Your job is NOT to clean the data.

Your job is to identify useful business insights.

Use the following structure:

## EXECUTIVE SUMMARY

Give 3 to 5 important findings
that a business manager should know.

## KEY BUSINESS FINDINGS

For each important finding:

1. Finding
2. Evidence from the dataset
3. Possible business impact

Do not invent facts that are not supported
by the dataset.

## IMPORTANT TRENDS

Identify important patterns,
high-performing groups,
low-performing groups,
unusual distributions,
or strong relationships.

## BUSINESS RISKS

Identify possible risks suggested
by the data.

Clearly state when something
is only a potential risk.

## BUSINESS OPPORTUNITIES

Identify areas that could potentially
improve business performance.

## RECOMMENDATIONS

Give practical recommendations.

Separate recommendations into:

### Immediate Actions

Actions that could be considered now.

### Further Analysis

Questions that should be investigated
before making an important business decision.

## KPIs TO MONITOR

Suggest useful KPIs that a business
should monitor based on the available columns.

Only recommend KPIs that make sense
from the available dataset.

IMPORTANT:

Do not fabricate revenue,
profit, customers, growth rates,
or other business metrics that are
not actually present in the dataset.

If the dataset does not provide enough
information to make a business conclusion,
clearly say so.
"""

    return prompt


# ============================================================
# MAIN PAGE
# ============================================================

def show_ai_business():

    st.title(
        "🤖 AI Business Analyst"
    )

    st.caption(
        "Turn your dataset into business-level "
        "findings and recommendations."
    )

    # ========================================================
    # CHECK DATASET
    # ========================================================

    df = st.session_state.get(
        "df"
    )

    if df is None:

        st.warning(
            "📂 Please upload a dataset first."
        )

        return

    if not isinstance(
        df,
        pd.DataFrame
    ):

        st.error(
            "❌ The stored dataset is invalid."
        )

        return

    if df.empty:

        st.warning(
            "⚠️ The dataset is empty."
        )

        return

    # ========================================================
    # DATASET OVERVIEW
    # ========================================================

    st.subheader(
        "📊 Dataset Being Analyzed"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            f"{len(df):,}"
        )

    with col2:

        st.metric(
            "Columns",
            f"{len(df.columns):,}"
        )

    with col3:

        st.metric(
            "Numerical Columns",
            len(
                df.select_dtypes(
                    include="number"
                ).columns
            )
        )

    with col4:

        st.metric(
            "Categorical Columns",
            len(
                df.select_dtypes(
                    include=[
                        "object",
                        "category",
                        "string",
                        "bool"
                    ]
                ).columns
            )
        )

    st.divider()

    # ========================================================
    # ANALYSIS BUTTON
    # ========================================================

    st.subheader(
        "🧠 Generate Business Analysis"
    )

    st.write(
        "The AI will analyze the dataset and "
        "generate findings, risks, opportunities, "
        "recommendations and KPIs."
    )

    if st.button(
        "🤖 Analyze Dataset",
        type="primary",
        use_container_width=True,
        key="generate_business_analysis"
    ):

        with st.spinner(
            "AI is analyzing your dataset..."
        ):

            try:

                prompt = create_business_prompt(
                    df
                )

                result = ask_llm(
                    prompt
                )

                if not result:

                    st.error(
                        "❌ The AI returned an empty response."
                    )

                else:

                    st.session_state[
                        "business_analysis"
                    ] = result

                    st.success(
                        "✅ Business analysis generated."
                    )

            except Exception as error:

                st.error(
                    "❌ AI Business Analysis failed."
                )

                st.code(
                    str(error)
                )

    # ========================================================
    # SHOW SAVED ANALYSIS
    # ========================================================

    analysis = st.session_state.get(
        "business_analysis"
    )

    if analysis:

        st.divider()

        st.subheader(
            "📋 Business Analysis"
        )

        st.markdown(
            analysis
        )

        # ----------------------------------------------------
        # SAVE FOR EXPORT CENTER
        # ----------------------------------------------------

        st.session_state[
            "business_analysis"
        ] = analysis

        # ----------------------------------------------------
        # COPY / EXPORT
        # ----------------------------------------------------

        st.divider()

        st.subheader(
            "📥 Analysis"
        )

        st.download_button(
            label="⬇️ Download Business Analysis",
            data=analysis,
            file_name="ai_business_analysis.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_business_analysis"
        )

    else:

        st.info(
            "Click **Analyze Dataset** to generate "
            "your business analysis."
        )

    # ========================================================
    # DATA PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "👀 Dataset Preview"
    )

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )
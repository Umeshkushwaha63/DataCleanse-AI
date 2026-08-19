import io

import pandas as pd
import streamlit as st


# ============================================================
# CREATE TEXT REPORT
# ============================================================

def create_text_report(df):

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

    report = []

    report.append(
        "DATA CLEANSE AI - DATASET REPORT"
    )

    report.append(
        "=" * 50
    )

    report.append(
        f"Rows: {rows:,}"
    )

    report.append(
        f"Columns: {columns:,}"
    )

    report.append(
        f"Missing Values: {missing_values:,}"
    )

    report.append(
        f"Duplicate Rows: {duplicate_rows:,}"
    )

    report.append(
        ""
    )

    report.append(
        "NUMERICAL COLUMNS"
    )

    report.append(
        "-" * 30
    )

    for column in numeric_columns:

        series = pd.to_numeric(
            df[column],
            errors="coerce"
        ).dropna()

        if series.empty:
            continue

        report.append(
            f"""
Column: {column}
Minimum: {series.min():.2f}
Maximum: {series.max():.2f}
Mean: {series.mean():.2f}
Median: {series.median():.2f}
Standard Deviation: {series.std():.2f}
"""
        )

    report.append(
        "CATEGORICAL COLUMNS"
    )

    report.append(
        "-" * 30
    )

    for column in categorical_columns:

        unique_count = int(
            df[column].nunique(
                dropna=True
            )
        )

        report.append(
            f"{column}: {unique_count} unique values"
        )

    report.append(
        ""
    )

    report.append(
        "MISSING VALUES BY COLUMN"
    )

    report.append(
        "-" * 30
    )

    missing_by_column = (
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    for column, count in missing_by_column.items():

        if count > 0:

            report.append(
                f"{column}: {int(count):,}"
            )

    return "\n".join(
        report
    )


# ============================================================
# CREATE CSV BYTES
# ============================================================

def dataframe_to_csv(df):

    return df.to_csv(
        index=False
    ).encode(
        "utf-8"
    )


# ============================================================
# CREATE EXCEL FILE
# ============================================================

def dataframe_to_excel(df):

    output = io.BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Dataset"
        )

        summary = pd.DataFrame(
            {
                "Metric": [
                    "Rows",
                    "Columns",
                    "Missing Values",
                    "Duplicate Rows"
                ],
                "Value": [
                    len(df),
                    len(df.columns),
                    int(
                        df.isna()
                        .sum()
                        .sum()
                    ),
                    int(
                        df.duplicated()
                        .sum()
                    )
                ]
            }
        )

        summary.to_excel(
            writer,
            index=False,
            sheet_name="Summary"
        )

    output.seek(0)

    return output.getvalue()


# ============================================================
# MAIN EXPORT PAGE
# ============================================================

def show_export_center():

    st.title(
        "📥 Export Center"
    )

    st.caption(
        "Download your cleaned dataset, "
        "reports and AI-generated analysis."
    )

    # ========================================================
    # GET DATASET
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
            "❌ Invalid dataset."
        )

        return

    if df.empty:

        st.warning(
            "⚠️ The dataset is empty."
        )

        return

    # ========================================================
    # DATASET SUMMARY
    # ========================================================

    st.subheader(
        "📊 Current Dataset"
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
            "Missing Values",
            f"{int(df.isna().sum().sum()):,}"
        )

    with col4:

        st.metric(
            "Duplicates",
            f"{int(df.duplicated().sum()):,}"
        )

    # ========================================================
    # DATA EXPORT
    # ========================================================

    st.divider()

    st.subheader(
        "📄 Dataset Export"
    )

    st.write(
        "Download the current dataset after "
        "any confirmed cleaning operations."
    )

    csv_data = dataframe_to_csv(
        df
    )

    excel_data = dataframe_to_excel(
        df
    )

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="datacleanse_cleaned_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_cleaned_csv"
        )

    with col2:

        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name="datacleanse_dataset.xlsx",
            mime=(
                "application/"
                "vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
            key="download_dataset_excel"
        )

    # ========================================================
    # DATA QUALITY REPORT
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Data Quality Report"
    )

    report = create_text_report(
        df
    )

    st.download_button(
        label="Download Data Quality Report",
        data=report,
        file_name="data_quality_report.txt",
        mime="text/plain",
        use_container_width=True,
        key="download_quality_report"
    )

    # ========================================================
    # AI BUSINESS ANALYSIS
    # ========================================================

    st.divider()

    st.subheader(
        " AI Business Analysis"
    )

    business_analysis = st.session_state.get(
        "business_analysis"
    )

    if business_analysis:

        st.success(
            " AI Business Analysis is available."
        )

        st.download_button(
            label=" Download AI Business Analysis",
            data=business_analysis,
            file_name="ai_business_analysis.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_ai_business_report"
        )

    else:

        st.info(
            "No AI Business Analysis has been generated yet."
        )

        st.write(
            "Go to **AI Business Analyst**, "
            "generate the analysis, and return here "
            "to download it."
        )

    # ========================================================
    # ORIGINAL DATASET
    # ========================================================

    st.divider()

    st.subheader(
        "🔙 Original Dataset"
    )

    original_df = st.session_state.get(
        "original_df"
    )

    if (
        original_df is not None
        and isinstance(
            original_df,
            pd.DataFrame
        )
        and not original_df.empty
    ):

        original_csv = dataframe_to_csv(
            original_df
        )

        st.download_button(
            label="⬇ Download Original Dataset",
            data=original_csv,
            file_name="datacleanse_original_data.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_original_csv"
        )

    else:

        st.info(
            "Original dataset is not available."
        )

    # ========================================================
    # PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        " Current Dataset Preview"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True
    )
import pandas as pd
import streamlit as st


# ============================================================
# QUALITY SCORE CALCULATIONS
# ============================================================

def calculate_quality_score(df):
    """Calculate an overall data quality score."""

    if df is None or df.empty:
        return 0

    total_cells = len(df) * len(df.columns)

    # --------------------------------------------------------
    # COMPLETENESS
    # --------------------------------------------------------

    missing_cells = int(
        df.isna().sum().sum()
    )

    if total_cells > 0:

        completeness_score = (
            1 - (missing_cells / total_cells)
        ) * 100

    else:

        completeness_score = 0

    # --------------------------------------------------------
    # DUPLICATE SCORE
    # --------------------------------------------------------

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if len(df) > 0:

        duplicate_score = (
            1 - (duplicate_rows / len(df))
        ) * 100

    else:

        duplicate_score = 0

    # --------------------------------------------------------
    # DATA TYPE SCORE
    # --------------------------------------------------------

    type_score = calculate_type_score(
        df
    )

    # --------------------------------------------------------
    # CONSISTENCY SCORE
    # --------------------------------------------------------

    consistency_score = calculate_consistency_score(
        df
    )

    # --------------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------------

    overall_score = (
        completeness_score * 0.40
        + duplicate_score * 0.25
        + type_score * 0.20
        + consistency_score * 0.15
    )

    return round(
        max(
            0,
            min(
                100,
                overall_score
            )
        ),
        1
    )


# ============================================================
# DATA TYPE SCORE
# ============================================================

def calculate_type_score(df):
    """Estimate data type quality."""

    score = 100

    for column in df.columns:

        series = df[column]

        # ----------------------------------------------------
        # Mixed Python types inside object columns
        # ----------------------------------------------------

        if series.dtype == "object":

            non_null = series.dropna()

            if not non_null.empty:

                types = non_null.map(
                    type
                ).nunique()

                if types > 1:

                    score -= 10

    return max(
        0,
        score
    )


# ============================================================
# CONSISTENCY SCORE
# ============================================================

def calculate_consistency_score(df):
    """Estimate categorical consistency."""

    score = 100

    categorical_columns = list(
        df.select_dtypes(
            include=[
                "object",
                "category",
                "string"
            ]
        ).columns
    )

    for column in categorical_columns:

        series = (
            df[column]
            .dropna()
            .astype(str)
        )

        if series.empty:
            continue

        # ----------------------------------------------------
        # Check for whitespace problems
        # ----------------------------------------------------

        whitespace_values = series[
            series != series.str.strip()
        ]

        if not whitespace_values.empty:

            score -= 5

        # ----------------------------------------------------
        # Check case inconsistency
        # ----------------------------------------------------

        lowercase_values = (
            series.str.lower()
            .nunique()
        )

        original_values = series.nunique()

        if (
            lowercase_values
            < original_values
        ):

            score -= 5

    return max(
        0,
        score
    )


# ============================================================
# SCORE LABEL
# ============================================================

def get_score_status(score):

    if score >= 90:

        return (
            "Excellent",
            "🟢"
        )

    if score >= 75:

        return (
            "Good",
            "🟡"
        )

    if score >= 60:

        return (
            "Needs Improvement",
            "🟠"
        )

    return (
        "Poor",
        "🔴"
    )


# ============================================================
# QUALITY COMPONENTS
# ============================================================

def get_quality_components(df):

    total_cells = (
        len(df) * len(df.columns)
    )

    missing_cells = int(
        df.isna().sum().sum()
    )

    if total_cells > 0:

        completeness = (
            1 - missing_cells / total_cells
        ) * 100

    else:

        completeness = 0

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if len(df) > 0:

        duplicate_score = (
            1 - duplicate_rows / len(df)
        ) * 100

    else:

        duplicate_score = 0

    type_score = calculate_type_score(
        df
    )

    consistency_score = calculate_consistency_score(
        df
    )

    return {
        "Completeness": round(
            completeness,
            1
        ),
        "Duplicates": round(
            duplicate_score,
            1
        ),
        "Data Types": round(
            type_score,
            1
        ),
        "Consistency": round(
            consistency_score,
            1
        )
    }


# ============================================================
# MAIN PAGE
# ============================================================

def show_quality_dashboard():

    st.title(
        "📊 Data Quality Dashboard"
    )

    st.caption(
        "Measure the health and reliability "
        "of your current dataset."
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
    # CALCULATE SCORE
    # ========================================================

    score = calculate_quality_score(
        df
    )

    status, icon = get_score_status(
        score
    )

    components = get_quality_components(
        df
    )

    # ========================================================
    # MAIN SCORE
    # ========================================================

    st.subheader(
        "🎯 Overall Data Quality Score"
    )

    col1, col2 = st.columns(
        [1, 2]
    )

    with col1:

        st.metric(
            "Quality Score",
            f"{score:.1f} / 100"
        )

        st.success(
            f"{icon} {status}"
        )

    with col2:

        st.progress(
            score / 100
        )

        st.write(
            f"Your dataset currently has a "
            f"**{score:.1f}% quality score**."
        )

        if score >= 90:

            st.write(
                "The dataset is in excellent condition."
            )

        elif score >= 75:

            st.write(
                "The dataset is generally healthy, "
                "but some improvements are recommended."
            )

        elif score >= 60:

            st.write(
                "Several quality problems should "
                "be investigated before analysis."
            )

        else:

            st.write(
                "Significant quality problems "
                "should be addressed before using "
                "this dataset for important analysis."
            )

    # ========================================================
    # QUALITY COMPONENTS
    # ========================================================

    st.divider()

    st.subheader(
        "📋 Quality Components"
    )

    col1, col2, col3, col4 = st.columns(4)

    component_items = list(
        components.items()
    )

    with col1:

        name, value = component_items[0]

        st.metric(
            name,
            f"{value:.1f}"
        )

    with col2:

        name, value = component_items[1]

        st.metric(
            name,
            f"{value:.1f}"
        )

    with col3:

        name, value = component_items[2]

        st.metric(
            name,
            f"{value:.1f}"
        )

    with col4:

        name, value = component_items[3]

        st.metric(
            name,
            f"{value:.1f}"
        )

    # ========================================================
    # QUALITY BREAKDOWN
    # ========================================================

    st.divider()

    st.subheader(
        "📈 Quality Breakdown"
    )

    component_df = pd.DataFrame(
        {
            "Quality Area": components.keys(),
            "Score": components.values()
        }
    )

    component_df = component_df.set_index(
        "Quality Area"
    )

    st.bar_chart(
        component_df
    )

    # ========================================================
    # DATASET STATISTICS
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Dataset Statistics"
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

        missing = int(
            df.isna().sum().sum()
        )

        st.metric(
            "Missing Values",
            f"{missing:,}"
        )

    with col4:

        duplicates = int(
            df.duplicated().sum()
        )

        st.metric(
            "Duplicate Rows",
            f"{duplicates:,}"
        )

    # ========================================================
    # QUALITY ISSUES
    # ========================================================

    st.divider()

    st.subheader(
        "⚠️ Detected Quality Issues"
    )

    issues_found = False

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    missing_by_column = (
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    missing_by_column = missing_by_column[
        missing_by_column > 0
    ]

    if not missing_by_column.empty:

        issues_found = True

        st.warning(
            f"⚠️ {int(missing_by_column.sum()):,} "
            "missing values were detected."
        )

        missing_table = pd.DataFrame(
            {
                "Column": missing_by_column.index,
                "Missing Values": (
                    missing_by_column.values
                )
            }
        )

        missing_table["Percentage"] = (
            missing_table["Missing Values"]
            / len(df)
            * 100
        ).round(2)

        st.dataframe(
            missing_table,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count > 0:

        issues_found = True

        st.warning(
            f"🔁 {duplicate_count:,} "
            "duplicate rows were detected."
        )

    # --------------------------------------------------------
    # CONSISTENCY
    # --------------------------------------------------------

    if components["Consistency"] < 100:

        issues_found = True

        st.warning(
            "⚠️ Some categorical columns may contain "
            "formatting or capitalization inconsistencies."
        )

    # --------------------------------------------------------
    # DATA TYPES
    # --------------------------------------------------------

    if components["Data Types"] < 100:

        issues_found = True

        st.warning(
            "⚠️ Some columns may contain mixed data types."
        )

    # --------------------------------------------------------
    # NO ISSUES
    # --------------------------------------------------------

    if not issues_found:

        st.success(
            "✅ No major data-quality problems "
            "were detected."
        )

    # ========================================================
    # COLUMN INFORMATION
    # ========================================================

    st.divider()

    st.subheader(
        "🔍 Column Information"
    )

    column_information = []

    for column in df.columns:

        column_information.append(
            {
                "Column": column,
                "Data Type": str(
                    df[column].dtype
                ),
                "Missing": int(
                    df[column].isna().sum()
                ),
                "Unique Values": int(
                    df[column].nunique()
                )
            }
        )

    column_df = pd.DataFrame(
        column_information
    )

    st.dataframe(
        column_df,
        use_container_width=True,
        hide_index=True
    )

    # ========================================================
    # DATA PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "👀 Current Dataset"
    )

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True
    )
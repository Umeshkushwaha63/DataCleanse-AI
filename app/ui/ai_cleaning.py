import pandas as pd
import streamlit as st

from app.services.ai_analyzer import analyze_dataset


def get_original_data():
    """Create a backup of the uploaded dataset."""

    if "original_df" not in st.session_state:
        st.session_state["original_df"] = (
            st.session_state["df"].copy()
        )


def show_dataset_summary(df):
    """Show basic information about the current dataset."""

    rows = len(df)
    columns = len(df.columns)
    duplicates = int(df.duplicated().sum())
    missing = int(df.isna().sum().sum())

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Rows", f"{rows:,}")

    with col2:
        st.metric("Columns", f"{columns:,}")

    with col3:
        st.metric("Missing Values", f"{missing:,}")

    with col4:
        st.metric("Duplicates", f"{duplicates:,}")


def show_ai_recommendation(df):
    """Generate and display the AI recommendation."""

    st.subheader("🤖 AI Cleaning Recommendation")

    if st.button(
        "🔍 Analyze Dataset with AI",
        key="analyze_dataset_button"
    ):

        with st.spinner(
            "AI is analyzing your dataset..."
        ):

            try:

                recommendation = analyze_dataset(df)

                st.session_state[
                    "ai_recommendation"
                ] = recommendation

            except Exception as error:

                st.error(
                    "AI analysis could not be completed."
                )

                st.code(
                    str(error)
                )

    if "ai_recommendation" in st.session_state:

        st.info(
            st.session_state[
                "ai_recommendation"
            ]
        )


def remove_duplicates(df):
    """Allow the user to preview and remove duplicates."""

    st.subheader("🔁 Duplicate Rows")

    duplicate_count = int(
        df.duplicated().sum()
    )

    if duplicate_count == 0:

        st.success(
            "✅ No duplicate rows detected."
        )

        return df

    st.warning(
        f"⚠️ {duplicate_count:,} duplicate rows detected."
    )

    st.write(
        "Preview of duplicate rows:"
    )

    duplicates = df[
        df.duplicated(keep=False)
    ]

    st.dataframe(
        duplicates.head(20),
        use_container_width=True,
        hide_index=True
    )

    st.write(
        "Removing duplicates will keep the first "
        "occurrence of each record."
    )

    if st.button(
        "🗑️ Remove Duplicates",
        key="remove_duplicates_button"
    ):

        cleaned_df = df.drop_duplicates()

        st.session_state["df"] = cleaned_df

        st.success(
            f"✅ Removed {duplicate_count:,} duplicate rows."
        )

        st.rerun()

    return st.session_state["df"]


def handle_missing_values(df):
    """Handle missing values with user confirmation."""

    st.subheader("⚠️ Missing Values")

    missing_counts = (
        df.isna()
        .sum()
        .sort_values(
            ascending=False
        )
    )

    missing_counts = missing_counts[
        missing_counts > 0
    ]

    if missing_counts.empty:

        st.success(
            "✅ No missing values detected."
        )

        return df

    missing_table = pd.DataFrame(
        {
            "Column": missing_counts.index,
            "Missing Values": missing_counts.values
        }
    )

    st.dataframe(
        missing_table,
        use_container_width=True,
        hide_index=True
    )

    selected_column = st.selectbox(
        "Select a column to clean",
        list(missing_counts.index),
        key="missing_column_select"
    )

    method = st.selectbox(
        "Cleaning method",
        [
            "Drop rows",
            "Fill with mean",
            "Fill with median",
            "Fill with mode"
        ],
        key="missing_method_select"
    )

    missing_count = int(
        df[selected_column].isna().sum()
    )

    st.info(
        f"Column **{selected_column}** contains "
        f"**{missing_count:,}** missing values."
    )

    if st.button(
        "👀 Preview Cleaning",
        key="preview_missing_button"
    ):

        preview_df = df.copy()

        if method == "Drop rows":

            preview_df = preview_df.dropna(
                subset=[selected_column]
            )

        elif method == "Fill with mean":

            if pd.api.types.is_numeric_dtype(
                preview_df[selected_column]
            ):

                value = preview_df[
                    selected_column
                ].mean()

                preview_df[
                    selected_column
                ] = preview_df[
                    selected_column
                ].fillna(value)

            else:

                st.error(
                    "Mean can only be used with numerical columns."
                )

                return df

        elif method == "Fill with median":

            if pd.api.types.is_numeric_dtype(
                preview_df[selected_column]
            ):

                value = preview_df[
                    selected_column
                ].median()

                preview_df[
                    selected_column
                ] = preview_df[
                    selected_column
                ].fillna(value)

            else:

                st.error(
                    "Median can only be used with numerical columns."
                )

                return df

        elif method == "Fill with mode":

            mode = preview_df[
                selected_column
            ].mode()

            if not mode.empty:

                preview_df[
                    selected_column
                ] = preview_df[
                    selected_column
                ].fillna(mode.iloc[0])

        st.session_state[
            "missing_preview_df"
        ] = preview_df

        st.session_state[
            "missing_preview_column"
        ] = selected_column

        st.session_state[
            "missing_preview_method"
        ] = method

    if "missing_preview_df" in st.session_state:

        preview_df = st.session_state[
            "missing_preview_df"
        ]

        st.write(
            "### Preview"
        )

        st.dataframe(
            preview_df.head(10),
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "⚠️ Review the preview before applying this change."
        )

        if st.button(
            "✅ Confirm & Apply",
            key="confirm_missing_button"
        ):

            st.session_state["df"] = preview_df

            st.session_state.pop(
                "missing_preview_df",
                None
            )

            st.success(
                "✅ Missing-value cleaning applied."
            )

            st.rerun()

    return st.session_state["df"]


def handle_outliers(df):
    """Detect and optionally remove numerical outliers."""

    st.subheader("📈 Outlier Detection")

    numeric_columns = list(
        df.select_dtypes(
            include="number"
        ).columns
    )

    if not numeric_columns:

        st.info(
            "No numerical columns available for outlier analysis."
        )

        return df

    selected_column = st.selectbox(
        "Select numerical column",
        numeric_columns,
        key="outlier_column_select"
    )

    series = df[
        selected_column
    ].dropna()

    if len(series) < 4:

        st.info(
            "Not enough values to calculate outliers."
        )

        return df

    q1 = series.quantile(
        0.25
    )

    q3 = series.quantile(
        0.75
    )

    iqr = q3 - q1

    lower_limit = q1 - (
        1.5 * iqr
    )

    upper_limit = q3 + (
        1.5 * iqr
    )

    outlier_mask = (
        (df[selected_column] < lower_limit)
        |
        (df[selected_column] > upper_limit)
    )

    outlier_count = int(
        outlier_mask.sum()
    )

    if outlier_count == 0:

        st.success(
            f"✅ No potential outliers detected in {selected_column}."
        )

        return df

    st.warning(
        f"⚠️ {outlier_count:,} potential outliers detected."
    )

    st.write(
        f"Lower limit: **{lower_limit:.2f}**"
    )

    st.write(
        f"Upper limit: **{upper_limit:.2f}**"
    )

    st.write(
        "### Outlier Preview"
    )

    st.dataframe(
        df.loc[
            outlier_mask
        ].head(20),
        use_container_width=True,
        hide_index=True
    )

    method = st.selectbox(
        "Choose an action",
        [
            "Remove outlier rows",
            "Keep outliers"
        ],
        key="outlier_method_select"
    )

    if method == "Remove outlier rows":

        if st.button(
            "👀 Preview Outlier Cleaning",
            key="preview_outlier_button"
        ):

            preview_df = df.loc[
                ~outlier_mask
            ].copy()

            st.session_state[
                "outlier_preview_df"
            ] = preview_df

    if "outlier_preview_df" in st.session_state:

        st.write(
            "### Before / After"
        )

        before_col, after_col = st.columns(2)

        with before_col:

            st.metric(
                "Before",
                f"{len(df):,} rows"
            )

        with after_col:

            st.metric(
                "After",
                f"{len(st.session_state['outlier_preview_df']):,} rows"
            )

        st.dataframe(
            st.session_state[
                "outlier_preview_df"
            ].head(10),
            use_container_width=True,
            hide_index=True
        )

        st.warning(
            "⚠️ Outliers may contain valid business information."
        )

        if st.button(
            "✅ Confirm & Remove",
            key="confirm_outlier_button"
        ):

            st.session_state[
                "df"
            ] = st.session_state[
                "outlier_preview_df"
            ]

            st.session_state.pop(
                "outlier_preview_df",
                None
            )

            st.success(
                f"✅ Removed {outlier_count:,} potential outlier rows."
            )

            st.rerun()

    return st.session_state["df"]


def standardize_categories(df):
    """Standardize simple text formatting."""

    st.subheader(
        "🔤 Category Standardization"
    )

    text_columns = list(
        df.select_dtypes(
            include=["object", "string"]
        ).columns
    )

    if not text_columns:

        st.info(
            "No text columns found."
        )

        return df

    selected_column = st.selectbox(
        "Select a text column",
        text_columns,
        key="category_column_select"
    )

    values = (
        df[selected_column]
        .dropna()
        .astype(str)
    )

    unique_before = values.nunique()

    standardized = (
        values
        .str.strip()
        .str.lower()
    )

    unique_after = standardized.nunique()

    st.write(
        f"Unique values before: **{unique_before:,}**"
    )

    st.write(
        f"Unique values after standardization: **{unique_after:,}**"
    )

    if unique_after < unique_before:

        st.warning(
            "⚠️ Standardization will merge values "
            "that differ only by spaces or capitalization."
        )

    else:

        st.success(
            "No obvious formatting duplication detected."
        )

    if st.button(
        "👀 Preview Standardization",
        key="preview_category_button"
    ):

        preview_df = df.copy()

        preview_df[
            selected_column
        ] = (
            preview_df[
                selected_column
            ]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        st.session_state[
            "category_preview_df"
        ] = preview_df

    if "category_preview_df" in st.session_state:

        st.write(
            "### Preview"
        )

        st.dataframe(
            st.session_state[
                "category_preview_df"
            ].head(15),
            use_container_width=True,
            hide_index=True
        )

        if st.button(
            "✅ Confirm & Apply",
            key="confirm_category_button"
        ):

            st.session_state[
                "df"
            ] = st.session_state[
                "category_preview_df"
            ]

            st.session_state.pop(
                "category_preview_df",
                None
            )

            st.success(
                "✅ Category standardization applied."
            )

            st.rerun()

    return st.session_state["df"]


def restore_original_dataset():
    """Restore the original uploaded dataset."""

    st.subheader(
        "↩️ Restore Original Dataset"
    )

    if "original_df" not in st.session_state:

        st.info(
            "No original backup is available."
        )

        return

    if st.button(
        "↩️ Restore Original",
        key="restore_original_button"
    ):

        st.session_state[
            "df"
        ] = st.session_state[
            "original_df"
        ].copy()

        st.session_state.pop(
            "ai_recommendation",
            None
        )

        st.session_state.pop(
            "missing_preview_df",
            None
        )

        st.session_state.pop(
            "outlier_preview_df",
            None
        )

        st.session_state.pop(
            "category_preview_df",
            None
        )

        st.success(
            "✅ Original dataset restored."
        )

        st.rerun()


def download_dataset(df):
    """Allow the user to download the cleaned dataset."""

    st.subheader(
        "📥 Download Cleaned Dataset"
    )

    csv_data = df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download CSV",
        data=csv_data,
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        key="download_cleaned_dataset"
    )


def show_ai_cleaning():
    """Main AI Cleaning page."""

    st.title(
        "🧹 AI Cleaning"
    )

    # --------------------------------------------------
    # CHECK DATASET
    # --------------------------------------------------

    if "df" not in st.session_state:

        st.warning(
            "⚠️ Please upload a dataset first."
        )

        return

    df = st.session_state["df"]

    if df.empty:

        st.warning(
            "⚠️ The dataset is empty."
        )

        return

    # --------------------------------------------------
    # CREATE BACKUP
    # --------------------------------------------------

    get_original_data()

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------

    st.write(
        "Review data-quality problems and approve "
        "cleaning actions before changing your data."
    )

    show_dataset_summary(
        df
    )

    # --------------------------------------------------
    # AI RECOMMENDATION
    # --------------------------------------------------

    st.divider()

    show_ai_recommendation(
        df
    )

    # --------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------

    st.divider()

    df = remove_duplicates(
        st.session_state["df"]
    )

    # --------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------

    st.divider()

    df = handle_missing_values(
        st.session_state["df"]
    )

    # --------------------------------------------------
    # OUTLIERS
    # --------------------------------------------------

    st.divider()

    df = handle_outliers(
        st.session_state["df"]
    )

    # --------------------------------------------------
    # CATEGORY STANDARDIZATION
    # --------------------------------------------------

    st.divider()

    df = standardize_categories(
        st.session_state["df"]
    )

    # --------------------------------------------------
    # RESTORE
    # --------------------------------------------------

    st.divider()

    restore_original_dataset()

    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------

    st.divider()

    download_dataset(
        st.session_state["df"]
    )
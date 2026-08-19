import os

import pandas as pd
import streamlit as st


# ============================================================
# DATA FOLDER
# ============================================================

DATA_FOLDER = "data"

SAVED_DATASET = os.path.join(
    DATA_FOLDER,
    "current_dataset.csv"
)


# ============================================================
# CREATE DATA FOLDER
# ============================================================

def create_data_folder():

    if not os.path.exists(DATA_FOLDER):

        os.makedirs(DATA_FOLDER)


# ============================================================
# SAVE DATASET
# ============================================================

def save_dataset(df):

    create_data_folder()

    df.to_csv(
        SAVED_DATASET,
        index=False
    )


# ============================================================
# LOAD SAVED DATASET
# ============================================================

def load_saved_dataset():

    if not os.path.exists(
        SAVED_DATASET
    ):

        return None

    try:

        df = pd.read_csv(
            SAVED_DATASET
        )

        if df.empty:

            return None

        return df

    except Exception:

        return None


# ============================================================
# SHOW UPLOAD PAGE
# ============================================================

def show_upload():

    st.title(
        "📂 Upload Dataset"
    )

    st.caption(
        "Upload your CSV once. "
        "DataCleanse AI will keep it until you remove it."
    )

    # ========================================================
    # CHECK EXISTING DATASET
    # ========================================================

    if st.session_state.get("df") is None:

        saved_df = load_saved_dataset()

        if saved_df is not None:

            st.session_state["df"] = saved_df.copy()

            st.session_state["original_df"] = saved_df.copy()

            if st.session_state.get(
                "dataset_name"
            ) is None:

                st.session_state[
                    "dataset_name"
                ] = "Saved Dataset"

    # ========================================================
    # CURRENT DATASET
    # ========================================================

    if st.session_state.get("df") is not None:

        current_df = st.session_state["df"]

        st.success(
            "✅ Dataset is already loaded."
        )

        st.write(
            f"**Dataset:** "
            f"{st.session_state.get('dataset_name', 'Saved Dataset')}"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Rows",
                f"{len(current_df):,}"
            )

        with col2:

            st.metric(
                "Columns",
                f"{len(current_df.columns):,}"
            )

        with col3:

            st.metric(
                "Missing Values",
                f"{int(current_df.isna().sum().sum()):,}"
            )

        st.info(
            "Your dataset is saved. "
            "You do not need to upload it again."
        )

        st.divider()

        st.subheader(
            "🔄 Replace Dataset"
        )

        st.write(
            "Upload another CSV if you want to "
            "replace the current dataset."
        )

    # ========================================================
    # FILE UPLOADER
    # ========================================================

    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        key="dataset_upload"
    )

    if uploaded_file is None:

        return

    # ========================================================
    # READ FILE
    # ========================================================

    try:

        new_df = pd.read_csv(
            uploaded_file
        )

    except Exception as error:

        st.error(
            "❌ Could not read the CSV file."
        )

        st.code(
            str(error)
        )

        return

    # ========================================================
    # VALIDATE DATASET
    # ========================================================

    if new_df.empty:

        st.warning(
            "⚠️ The uploaded dataset is empty."
        )

        return

    # ========================================================
    # SAVE DATASET
    # ========================================================

    save_dataset(
        new_df
    )

    # ========================================================
    # UPDATE SESSION STATE
    # ========================================================

    st.session_state["df"] = new_df.copy()

    st.session_state[
        "original_df"
    ] = new_df.copy()

    st.session_state[
        "dataset_name"
    ] = uploaded_file.name

    # Clear old AI analysis
    st.session_state[
        "business_analysis"
    ] = None

    st.success(
        f"✅ {uploaded_file.name} uploaded and saved."
    )

    # ========================================================
    # DATASET SUMMARY
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Dataset Summary"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Rows",
            f"{len(new_df):,}"
        )

    with col2:

        st.metric(
            "Columns",
            f"{len(new_df.columns):,}"
        )

    with col3:

        st.metric(
            "Missing Values",
            f"{int(new_df.isna().sum().sum()):,}"
        )

    with col4:

        st.metric(
            "Duplicate Rows",
            f"{int(new_df.duplicated().sum()):,}"
        )

    # ========================================================
    # PREVIEW
    # ========================================================

    st.divider()

    st.subheader(
        "👀 Dataset Preview"
    )

    st.dataframe(
        new_df.head(20),
        use_container_width=True,
        hide_index=True
    )
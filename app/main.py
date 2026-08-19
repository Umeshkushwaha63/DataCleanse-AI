import streamlit as st

from app.ui.upload import show_upload
from app.ui.ai_cleaning import show_ai_cleaning
from app.ui.quality_dashboard import (
    show_quality_dashboard,
    calculate_quality_score,
    get_score_status,
    get_quality_components
)
from app.ui.visualizations import show_visualizations
from app.ui.ai_business import show_ai_business
from app.ui.export_center import show_export_center


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="DataCleanse AI",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# SESSION STATE
# ============================================================

if "df" not in st.session_state:
    st.session_state["df"] = None

if "original_df" not in st.session_state:
    st.session_state["original_df"] = None

if "business_analysis" not in st.session_state:
    st.session_state["business_analysis"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "home"

if "dataset_name" not in st.session_state:
    st.session_state["dataset_name"] = None


# ============================================================
# DATASET CHECK
# ============================================================

def dataset_is_loaded():

    df = st.session_state.get("df")

    if df is None:
        return False

    if not hasattr(df, "empty"):
        return False

    if df.empty:
        return False

    return True


# ============================================================
# REMOVE DATASET
# ============================================================

def remove_dataset():

    st.session_state["df"] = None

    st.session_state["original_df"] = None

    st.session_state["business_analysis"] = None

    st.session_state["dataset_name"] = None

    st.session_state["page"] = "home"


# ============================================================
# HOME PAGE
# ============================================================

def show_home():

    st.title("🧹 DataCleanse AI")

    st.subheader(
        "Intelligent Data Cleaning & Business Intelligence"
    )

    st.write(
        "Clean your data, measure its quality, "
        "discover insights and generate "
        "AI-powered business recommendations."
    )

    st.divider()

    # ========================================================
    # NO DATASET
    # ========================================================

    if not dataset_is_loaded():

        st.info(
            "📂 No dataset is currently loaded."
        )

        st.subheader(
            "🚀 Get Started"
        )

        st.write(
            "Upload a CSV dataset from the sidebar."
        )

        st.markdown(
            """
            ### 🧭 DataCleanse AI Workflow

            **1️⃣ Upload Dataset**

            Load your CSV file.

            ↓

            **2️⃣ AI Cleaning**

            Detect missing values, duplicates,
            outliers and inconsistent data.

            ↓

            **3️⃣ Data Quality**

            Measure the health of the dataset.

            ↓

            **4️⃣ Visualizations & Insights**

            Explore distributions, categories
            and correlations.

            ↓

            **5️⃣ AI Business Analyst**

            Convert data into business findings.

            ↓

            **6️⃣ Export Center**

            Download cleaned data and reports.
            """
        )

        return

    # ========================================================
    # DATASET LOADED
    # ========================================================

    df = st.session_state["df"]

    st.success(
        f"✅ Dataset loaded: "
        f"{st.session_state.get('dataset_name', 'Dataset')}"
    )

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    try:

        quality_score = calculate_quality_score(
            df
        )

        status, icon = get_score_status(
            quality_score
        )

        components = get_quality_components(
            df
        )

    except Exception:

        quality_score = 0
        status = "Unknown"
        icon = "⚪"
        components = {}

    st.subheader(
        "🎯 Dataset Health"
    )

    score_col, details_col = st.columns(
        [1, 2]
    )

    with score_col:

        st.metric(
            "Quality Score",
            f"{quality_score:.1f} / 100"
        )

        if status == "Excellent":

            st.success(
                f"{icon} {status}"
            )

        elif status == "Good":

            st.info(
                f"{icon} {status}"
            )

        elif status == "Needs Improvement":

            st.warning(
                f"{icon} {status}"
            )

        else:

            st.error(
                f"{icon} {status}"
            )

    with details_col:

        st.progress(
            min(
                max(
                    quality_score / 100,
                    0
                ),
                1
            )
        )

        st.write(
            "The score is calculated from the "
            "current dataset."
        )

    # ========================================================
    # DATASET METRICS
    # ========================================================

    st.divider()

    st.subheader(
        "📊 Dataset Overview"
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
            "Duplicate Rows",
            f"{int(df.duplicated().sum()):,}"
        )

    # ========================================================
    # QUALITY COMPONENTS
    # ========================================================

    if components:

        st.divider()

        st.subheader(
            "📈 Quality Breakdown"
        )

        component_list = list(
            components.items()
        )

        cols = st.columns(
            len(component_list)
        )

        for index, (name, value) in enumerate(
            component_list
        ):

            with cols[index]:

                st.metric(
                    name,
                    f"{value:.1f}"
                )

    # ========================================================
    # QUICK NAVIGATION
    # ========================================================

    st.divider()

    st.subheader(
        "🚀 Continue Analysis"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        if st.button(
            "🧹 AI Cleaning",
            use_container_width=True
        ):

            st.session_state["page"] = "cleaning"
            st.rerun()

    with col2:

        if st.button(
            "📊 Data Quality",
            use_container_width=True
        ):

            st.session_state["page"] = "quality"
            st.rerun()

    with col3:

        if st.button(
            "📈 Visualizations",
            use_container_width=True
        ):

            st.session_state["page"] = "visualizations"
            st.rerun()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🧹 DataCleanse AI"
)

st.sidebar.caption(
    "AI-Powered Data Quality Platform"
)

st.sidebar.divider()

st.sidebar.subheader(
    "📍 Project Flow"
)


# ============================================================
# NAVIGATION
# ============================================================

if st.sidebar.button(
    "🏠 Home",
    use_container_width=True
):

    st.session_state["page"] = "home"


if st.sidebar.button(
    "📂 Upload Dataset",
    use_container_width=True
):

    st.session_state["page"] = "upload"


if st.sidebar.button(
    "🧹 AI Cleaning",
    use_container_width=True
):

    st.session_state["page"] = "cleaning"


if st.sidebar.button(
    "📊 Data Quality",
    use_container_width=True
):

    st.session_state["page"] = "quality"


if st.sidebar.button(
    "📈 Visualizations & Insights",
    use_container_width=True
):

    st.session_state["page"] = "visualizations"


if st.sidebar.button(
    "🤖 AI Business Analyst",
    use_container_width=True
):

    st.session_state["page"] = "business"


if st.sidebar.button(
    "📥 Export Center",
    use_container_width=True
):

    st.session_state["page"] = "export"


# ============================================================
# DATASET STATUS
# ============================================================

st.sidebar.divider()

st.sidebar.subheader(
    "📊 Dataset Status"
)

if dataset_is_loaded():

    df = st.session_state["df"]

    st.sidebar.success(
        "✅ Dataset Loaded"
    )

    if st.session_state.get(
        "dataset_name"
    ):

        st.sidebar.caption(
            st.session_state["dataset_name"]
        )

    st.sidebar.write(
        f"Rows: **{len(df):,}**"
    )

    st.sidebar.write(
        f"Columns: **{len(df.columns):,}**"
    )

    # --------------------------------------------------------
    # REMOVE DATASET
    # --------------------------------------------------------

    st.sidebar.divider()

    if st.sidebar.button(
        "🗑️ Remove Dataset",
        use_container_width=True
    ):

        remove_dataset()

        st.rerun()

else:

    st.sidebar.warning(
        "📂 No Dataset Loaded"
    )


# ============================================================
# CURRENT PAGE
# ============================================================

current_page = st.session_state["page"]


# ============================================================
# PAGE ROUTING
# ============================================================

if current_page == "home":

    show_home()


elif current_page == "upload":

    show_upload()


elif current_page == "cleaning":

    if dataset_is_loaded():

        show_ai_cleaning()

    else:

        st.warning(
            "📂 Please upload a dataset first."
        )


elif current_page == "quality":

    if dataset_is_loaded():

        show_quality_dashboard()

    else:

        st.warning(
            "📂 Please upload a dataset first."
        )


elif current_page == "visualizations":

    if dataset_is_loaded():

        show_visualizations()

    else:

        st.warning(
            "📂 Please upload a dataset first."
        )


elif current_page == "business":

    if dataset_is_loaded():

        show_ai_business()

    else:

        st.warning(
            "📂 Please upload a dataset first."
        )


elif current_page == "export":

    if dataset_is_loaded():

        show_export_center()

    else:

        st.warning(
            "📂 Please upload a dataset first."
        )
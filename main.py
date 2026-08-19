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
# PAGE CONFIGURATION
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


# ============================================================
# CHECK DATASET
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
# HOME PAGE
# ============================================================

def show_home():

    st.title("🧹 DataCleanse AI")

    st.subheader(
        "Intelligent Data Cleaning & Business Intelligence"
    )

    st.write(
        "A complete platform to clean, measure, "
        "visualize and understand your data."
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
            "🚀 Start Your Data Journey"
        )

        st.write(
            "Upload a CSV dataset to start analyzing "
            "your data."
        )

        st.markdown(
            """
            ### 🧭 DataCleanse AI Workflow

            **1️⃣ Upload Dataset**

            Load your CSV dataset.

            ↓

            **2️⃣ AI Cleaning**

            Detect and safely clean data-quality problems.

            ↓

            **3️⃣ Data Quality**

            Measure the health of your dataset.

            ↓

            **4️⃣ Visualizations & Insights**

            Discover patterns and relationships.

            ↓

            **5️⃣ AI Business Analyst**

            Convert your data into business insights.

            ↓

            **6️⃣ Export Center**

            Download your results and reports.
            """
        )

        return

    # ========================================================
    # DATASET AVAILABLE
    # ========================================================

    df = st.session_state["df"]

    # ========================================================
    # DATASET HEADER
    # ========================================================

    st.success(
        "✅ Dataset loaded successfully"
    )

    st.subheader(
        "📊 Dataset Health"
    )

    # ========================================================
    # CALCULATE QUALITY SCORE
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

    except Exception as error:

        st.error(
            "Unable to calculate the quality score."
        )

        st.code(
            str(error)
        )

        quality_score = 0
        status = "Unknown"
        icon = "⚪"
        components = {}

    # ========================================================
    # MAIN QUALITY SCORE
    # ========================================================

    score_col, details_col = st.columns(
        [1, 2]
    )

    with score_col:

        st.metric(
            "Overall Quality Score",
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
            quality_score / 100
        )

        st.write(
            f"Your current dataset quality is "
            f"**{quality_score:.1f}%**."
        )

        st.write(
            "The score is calculated automatically "
            "from the current dataset."
        )

    # ========================================================
    # DATASET KPIs
    # ========================================================

    st.divider()

    st.subheader(
        "📌 Dataset Overview"
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

        missing_values = int(
            df.isna().sum().sum()
        )

        st.metric(
            "Missing Values",
            f"{missing_values:,}"
        )

    with col4:

        duplicate_rows = int(
            df.duplicated().sum()
        )

        st.metric(
            "Duplicate Rows",
            f"{duplicate_rows:,}"
        )

    # ========================================================
    # QUALITY BREAKDOWN
    # ========================================================

    if components:

        st.divider()

        st.subheader(
            "📈 Quality Breakdown"
        )

        col1, col2, col3, col4 = st.columns(4)

        component_list = list(
            components.items()
        )

        with col1:

            name, value = component_list[0]

            st.metric(
                name,
                f"{value:.1f}"
            )

        with col2:

            name, value = component_list[1]

            st.metric(
                name,
                f"{value:.1f}"
            )

        with col3:

            name, value = component_list[2]

            st.metric(
                name,
                f"{value:.1f}"
            )

        with col4:

            name, value = component_list[3]

            st.metric(
                name,
                f"{value:.1f}"
            )

    # ========================================================
    # QUALITY PROBLEMS
    # ========================================================

    st.divider()

    st.subheader(
        "⚠️ Current Data Issues"
    )

    problems_found = False

    missing_values = int(
        df.isna().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    if missing_values > 0:

        problems_found = True

        st.warning(
            f"⚠️ {missing_values:,} missing values "
            "need attention."
        )

    if duplicate_rows > 0:

        problems_found = True

        st.warning(
            f"🔁 {duplicate_rows:,} duplicate rows "
            "were detected."
        )

    if (
        components
        and components.get("Data Types", 100) < 100
    ):

        problems_found = True

        st.warning(
            "🔤 Some columns may contain mixed "
            "data types."
        )

    if (
        components
        and components.get("Consistency", 100) < 100
    ):

        problems_found = True

        st.warning(
            "⚠️ Some categorical values may have "
            "formatting inconsistencies."
        )

    if not problems_found:

        st.success(
            "✅ No major data-quality problems detected."
        )

    # ========================================================
    # PROJECT WORKFLOW
    # ========================================================

    st.divider()

    st.subheader(
        "🧭 Project Workflow"
    )

    workflow_col1, workflow_col2 = st.columns(
        2
    )

    with workflow_col1:

        st.markdown(
            """
            ### 1️⃣ 📂 Upload Dataset

            Load your CSV dataset.

            ### 2️⃣ 🧹 AI Cleaning

            Detect and safely handle data-quality issues.

            ### 3️⃣ 📊 Data Quality

            Calculate the dataset health score.
            """
        )

    with workflow_col2:

        st.markdown(
            """
            ### 4️⃣ 📈 Visualizations

            Discover patterns and relationships.

            ### 5️⃣ 🤖 AI Business Analyst

            Generate business-level insights.

            ### 6️⃣ 📥 Export Center

            Download cleaned data and reports.
            """
        )


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
# NAVIGATION BUTTONS
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
# SIDEBAR DATASET STATUS
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

    st.sidebar.write(
        f"Rows: **{len(df):,}**"
    )

    st.sidebar.write(
        f"Columns: **{len(df.columns):,}**"
    )

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
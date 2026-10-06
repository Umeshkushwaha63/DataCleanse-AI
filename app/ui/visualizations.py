import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

try:
    from streamlit_plotly_events import plotly_events
    CLICK_EVENTS_AVAILABLE = True
except ImportError:
    CLICK_EVENTS_AVAILABLE = False


# ============================================================
# PAGE STYLE  (GLASS BLACK + BLUE THEME)
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- Black + blue glass background ---------- */
    .stApp {
        background:
            radial-gradient(circle at 15% 10%, rgba(37,99,235,0.25), transparent 40%),
            radial-gradient(circle at 85% 90%, rgba(0,212,255,0.15), transparent 40%),
            #05070d;
        color: #e5e7eb;
    }

    header[data-testid="stHeader"] { background: transparent; }

    h1, h2, h3, h4, h5, p, label, span { color: #e5e7eb; }

    .dashboard-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 0px;
        background: linear-gradient(90deg, #60a5fa, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        margin-bottom: 20px;
    }

    /* ---------- Glass cards ---------- */
    .selection-box,
    div[data-testid="stMetric"],
    div[data-testid="stExpander"],
    div[data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(96,165,250,0.25);
        border-radius: 14px;
        padding: 14px;
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.45);
    }

    div[data-testid="stMetricValue"] { color: #60a5fa; }
    div[data-testid="stMetricLabel"] { color: #94a3b8; }

    /* ---------- Inputs ---------- */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(96,165,250,0.3) !important;
        border-radius: 10px !important;
        color: #e5e7eb !important;
    }

    /* ---------- Buttons ---------- */
    .stButton > button {
        background: linear-gradient(135deg, rgba(37,99,235,0.6), rgba(0,212,255,0.35));
        color: white;
        border: 1px solid rgba(96,165,250,0.5);
        border-radius: 10px;
        backdrop-filter: blur(10px);
    }
    .stButton > button:hover {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0,212,255,0.5);
    }

    /* ---------- Tabs ---------- */
    button[data-baseweb="tab"] { color: #94a3b8; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #60a5fa; }
    div[data-baseweb="tab-highlight"] { background-color: #3b82f6; }

    hr { border-color: rgba(96,165,250,0.2); }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PLOTLY GLASS THEME
# ============================================================

BLUE_COLORS = [
    "#00D4FF", "#3B82F6", "#60A5FA", "#1D4ED8",
    "#38BDF8", "#818CF8", "#0EA5E9", "#93C5FD"
]


def apply_glass_theme(fig):

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,20,45,0.35)",
        font=dict(color="#e5e7eb"),
        colorway=BLUE_COLORS,
        title_font=dict(color="#93c5fd", size=18),
        legend=dict(
            bgcolor="rgba(255,255,255,0.05)",
            bordercolor="rgba(96,165,250,0.3)",
            borderwidth=1
        ),
        hoverlabel=dict(
            bgcolor="rgba(10,20,45,0.92)",
            bordercolor="#3b82f6",
            font=dict(color="white")
        )
    )

    fig.update_xaxes(
        gridcolor="rgba(96,165,250,0.12)",
        zerolinecolor="rgba(96,165,250,0.25)",
        linecolor="rgba(96,165,250,0.35)"
    )

    fig.update_yaxes(
        gridcolor="rgba(96,165,250,0.12)",
        zerolinecolor="rgba(96,165,250,0.25)",
        linecolor="rgba(96,165,250,0.35)"
    )

    # Lines: glowing blue (set per trace so it always applies)
    for trace in fig.data:
        if trace.type == "scatter" and trace.mode and "lines" in trace.mode:
            trace.update(
                line=dict(color="#00D4FF", width=3),
                marker=dict(
                    color="#00D4FF",
                    size=6,
                    line=dict(color="#05070d", width=1)
                )
            )

    # Bars: blue with soft border
    fig.update_traces(
        marker=dict(color="#3B82F6", line=dict(color="#60A5FA", width=1)),
        selector=dict(type="bar")
    )

    # Pie / donut: dark separators
    fig.update_traces(
        marker=dict(line=dict(color="#05070d", width=2)),
        selector=dict(type="pie")
    )

    # Histogram
    fig.update_traces(
        marker=dict(color="#3B82F6"),
        selector=dict(type="histogram")
    )

    # Box
    fig.update_traces(
        marker=dict(color="#00D4FF"),
        line=dict(color="#60A5FA"),
        selector=dict(type="box")
    )

    # Heatmap: blue scale
    if any(t.type == "heatmap" for t in fig.data):
        fig.update_layout(coloraxis=dict(colorscale="Blues"))

    # Dark map
    if any(t.type in ("scattermap", "scattermapbox") for t in fig.data):
        fig.update_layout(map_style="carto-darkmatter")

    return fig


# ============================================================
# COLUMN HELPERS
# ============================================================

def clean_column_name(column):
    return str(column).strip()


def get_series(df, column_name):
    """Safely get one column (also protects against duplicate column names)."""

    for index, column in enumerate(df.columns):
        if clean_column_name(column) == str(column_name):
            return df.iloc[:, index]

    return pd.Series(index=df.index, dtype="object")


def get_numeric_columns(df):

    columns = []

    for index, column in enumerate(df.columns):
        series = df.iloc[:, index]
        if pd.api.types.is_numeric_dtype(series):
            columns.append(clean_column_name(column))

    return list(dict.fromkeys(columns))


def get_categorical_columns(df):

    columns = []

    for index, column in enumerate(df.columns):
        series = df.iloc[:, index]

        if (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
            or isinstance(series.dtype, pd.CategoricalDtype)
            or pd.api.types.is_bool_dtype(series)
        ):
            columns.append(clean_column_name(column))

    return list(dict.fromkeys(columns))


# ============================================================
# DATE DETECTION
# ============================================================

def detect_date_columns(df):

    date_columns = []

    keywords = [
        "date", "time", "timestamp", "created", "updated", "joined",
        "purchase", "transaction", "order_date", "month", "year", "day"
    ]

    for index, column in enumerate(df.columns):

        column_name = clean_column_name(column)
        series = df.iloc[:, index]

        if pd.api.types.is_datetime64_any_dtype(series):
            date_columns.append(column_name)
            continue

        name_suggests_date = any(
            keyword in column_name.lower() for keyword in keywords
        )

        if not name_suggests_date:
            continue

        converted = pd.to_datetime(series, errors="coerce")

        if converted.notna().mean() >= 0.60:
            date_columns.append(column_name)

    return list(dict.fromkeys(date_columns))


# ============================================================
# LOCATION DETECTION
# ============================================================

def detect_location_columns(df):

    latitude = None
    longitude = None

    for column in df.columns:

        name = clean_column_name(column).lower()

        if latitude is None:
            if name == "lat" or name == "latitude" or "latitude" in name:
                latitude = clean_column_name(column)

        if longitude is None:
            if name in ["lon", "lng", "longitude"] or "longitude" in name:
                longitude = clean_column_name(column)

    return latitude, longitude


# ============================================================
# ID DETECTION
# ============================================================

def is_id_like(df, column_name):

    series = get_series(df, column_name)
    name = str(column_name).lower()

    id_keywords = [
        "id", "uuid", "key", "code", "index", "serial",
        "customer_no", "employee_no"
    ]

    if any(keyword in name for keyword in id_keywords):
        return True

    try:
        unique_ratio = series.nunique(dropna=True) / max(len(series), 1)
        if unique_ratio >= 0.95:
            return True
    except Exception:
        pass

    return False


def get_useful_numeric_columns(df):

    numeric_columns = get_numeric_columns(df)

    useful = [
        column for column in numeric_columns
        if not is_id_like(df, column)
    ]

    if useful:
        return useful

    return numeric_columns


def get_useful_categorical_columns(df):

    categorical_columns = get_categorical_columns(df)

    useful = []

    for column in categorical_columns:
        series = get_series(df, column)
        unique_count = series.nunique(dropna=True)

        if 2 <= unique_count <= 50:
            useful.append(column)

    return useful


# ============================================================
# NUMBER FORMATTING
# ============================================================

def format_number(value):

    try:
        value = float(value)

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if abs(value) >= 1_000:
            return f"{value / 1_000:.2f}K"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"

    except Exception:
        return str(value)


# ============================================================
# BUSINESS METRIC DETECTION
# ============================================================

def find_business_metrics(df):

    numeric_columns = get_useful_numeric_columns(df)

    keywords = [
        "revenue", "sales", "amount", "price", "profit", "income", "cost",
        "expense", "value", "total", "salary", "quantity", "units", "orders",
        "score", "rating", "margin", "growth", "rate", "percentage", "percent"
    ]

    priority = []
    normal = []

    for column in numeric_columns:
        name = column.lower()

        if any(keyword in name for keyword in keywords):
            priority.append(column)
        else:
            normal.append(column)

    return priority + normal


# ============================================================
# KPI ENGINE
# ============================================================

def calculate_base_kpis(df):

    rows = len(df)
    columns = len(df.columns)
    missing = int(df.isna().sum().sum())
    duplicate_rows = int(df.duplicated().sum())
    total_cells = rows * columns

    if total_cells > 0:
        missing_percentage = (missing / total_cells) * 100
    else:
        missing_percentage = 0

    duplicate_percentage = (duplicate_rows / max(rows, 1)) * 100

    quality_score = max(
        0,
        min(100, 100 - missing_percentage - duplicate_percentage)
    )

    return [
        ("📦 Records", f"{rows:,}", "Number of records"),
        ("📋 Columns", f"{columns:,}", "Number of columns"),
        ("⚠️ Missing Values", f"{missing:,}", "Total missing cells"),
        ("💚 Data Quality", f"{quality_score:.1f}%", "Estimated data quality")
    ]


def calculate_business_kpis(df):

    metrics = find_business_metrics(df)
    kpis = []

    for column in metrics[:4]:

        series = pd.to_numeric(
            get_series(df, column),
            errors="coerce"
        ).dropna()

        if series.empty:
            continue

        name = column.lower()

        additive_words = [
            "revenue", "sales", "amount", "profit", "income", "cost",
            "expense", "value", "total", "quantity", "units"
        ]

        if any(word in name for word in additive_words):
            value = series.sum()
            kpis.append(
                (f"💰 {column}", format_number(value), f"Total {column}")
            )
        else:
            value = series.mean()
            kpis.append(
                (f"📊 Avg {column}", format_number(value), f"Average {column}")
            )

    return kpis


def show_kpi_cards(df):

    kpis = calculate_base_kpis(df)
    kpis.extend(calculate_business_kpis(df))
    kpis = kpis[:8]

    st.markdown("### 📌 Key Performance Indicators")

    for start in range(0, len(kpis), 4):

        row = kpis[start:start + 4]
        columns = st.columns(len(row))

        for column, kpi in zip(columns, row):
            with column:
                st.metric(label=kpi[0], value=kpi[1], help=kpi[2])


# ============================================================
# GLOBAL FILTERS
# ============================================================

def apply_global_filters(df):

    filtered_df = df.copy()

    categorical_columns = get_useful_categorical_columns(df)
    date_columns = detect_date_columns(df)

    st.markdown("### 🎛️ Dashboard Filters")

    filter_columns = st.columns(4)
    filter_index = 0

    # --------------------------------------------------------
    # DATE FILTER
    # --------------------------------------------------------

    if date_columns:

        date_column = date_columns[0]

        dates = pd.to_datetime(
            get_series(df, date_column),
            errors="coerce"
        )

        valid_dates = dates.dropna()

        if not valid_dates.empty:

            min_date = valid_dates.min().date()
            max_date = valid_dates.max().date()

            with filter_columns[filter_index % 4]:
                selected_dates = st.date_input(
                    "Date Range",
                    value=(min_date, max_date),
                    key="dashboard_date_filter"
                )

            filter_index += 1

            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

                start_date, end_date = selected_dates

                mask = (
                    (dates.dt.date >= start_date)
                    & (dates.dt.date <= end_date)
                )

                filtered_df = filtered_df[mask.fillna(False)]

    # --------------------------------------------------------
    # CATEGORY FILTERS
    # --------------------------------------------------------

    for column in categorical_columns[:3]:

        series = (
            get_series(df, column)
            .fillna("Missing")
            .astype(str)
        )

        values = sorted(series.unique().tolist())

        if len(values) > 30:
            continue

        with filter_columns[filter_index % 4]:
            selected = st.multiselect(
                column,
                values,
                default=[],
                key=f"dashboard_filter_{column}"
            )

        filter_index += 1

        if selected:
            filtered_df = filtered_df[
                get_series(filtered_df, column)
                .fillna("Missing")
                .astype(str)
                .isin(selected)
            ]

    # --------------------------------------------------------
    # CLICK FILTER
    # --------------------------------------------------------

    click_filter = st.session_state.get("dashboard_click_filter")

    if click_filter:

        column = click_filter["column"]
        value = click_filter["value"]

        if column in [clean_column_name(c) for c in filtered_df.columns]:
            filtered_df = filtered_df[
                get_series(filtered_df, column)
                .fillna("Missing")
                .astype(str)
                == str(value)
            ]

    # --------------------------------------------------------
    # FILTER STATUS
    # --------------------------------------------------------

    st.caption(f"Showing {len(filtered_df):,} of {len(df):,} records")

    if click_filter:

        st.info(
            f"🔎 Click filter active: "
            f"**{click_filter['column']} = {click_filter['value']}**"
        )

        if st.button("✖ Clear Click Filter", key="clear_click_filter"):
            st.session_state.pop("dashboard_click_filter", None)
            st.session_state.pop("dashboard_selected_point", None)
            st.rerun()

    return filtered_df


# ============================================================
# CHART DISPLAY / CLICK HANDLER
# ============================================================

def display_chart(
    fig,
    key,
    chart_type=None,
    source_column=None,
    allow_click_filter=False
):

    if fig is None:
        return None

    fig = apply_glass_theme(fig)

    clicked_points = []

    if CLICK_EVENTS_AVAILABLE and allow_click_filter:

        clicked_points = plotly_events(
            fig,
            click_event=True,
            hover_event=False,
            select_event=False,
            override_height=450,
            key=key
        )

    else:

        st.plotly_chart(fig, use_container_width=True, key=key)

    if clicked_points and allow_click_filter:

        point = clicked_points[0]

        selected = {
            "chart_type": chart_type,
            "point": point,
            "column": source_column
        }

        st.session_state["dashboard_selected_point"] = selected

    return clicked_points


# ============================================================
# SELECTED VALUE DISPLAY
# ============================================================

def show_selected_point():

    selected = st.session_state.get("dashboard_selected_point")

    if not selected:
        return

    point = selected.get("point", {})
    chart_type = selected.get("chart_type")

    st.markdown("### 🎯 Selected Data")

    # ---------------- BAR ----------------

    if chart_type == "bar":

        category = point.get("x") or point.get("label")
        value = point.get("y")

        if category is not None:

            columns = st.columns(3)

            with columns[0]:
                st.metric("Selected Category", str(category))

            with columns[1]:
                if value is not None:
                    st.metric("Value", format_number(value))

            with columns[2]:
                st.metric("Chart", "Bar Chart")

    # ---------------- PIE ----------------

    elif chart_type == "pie":

        category = point.get("label")
        value = point.get("value")
        percent = point.get("percent")

        columns = st.columns(3)

        with columns[0]:
            st.metric("Selected Category", str(category))

        with columns[1]:
            st.metric("Value", format_number(value))

        with columns[2]:
            if percent is not None:
                st.metric("Share", f"{float(percent) * 100:.1f}%")

    # ---------------- LINE ----------------

    elif chart_type == "line":

        x_value = point.get("x")
        y_value = point.get("y")

        columns = st.columns(3)

        with columns[0]:
            st.metric("Date", str(x_value))

        with columns[1]:
            st.metric("Value", format_number(y_value))

        with columns[2]:
            st.metric("Chart", "Line Chart")

    # ---------------- SCATTER ----------------

    elif chart_type == "scatter":

        x_value = point.get("x")
        y_value = point.get("y")

        columns = st.columns(3)

        with columns[0]:
            st.metric("X Value", format_number(x_value))

        with columns[1]:
            st.metric("Y Value", format_number(y_value))

        with columns[2]:
            st.metric("Chart", "Scatter Plot")

    # ---------------- APPLY FILTER ----------------

    if selected.get("column") and chart_type in ["bar", "pie"]:

        point_value = point.get("x") or point.get("label")

        if point_value is not None:

            if st.button(
                "🔎 Apply Selection as Dashboard Filter",
                key="apply_selected_chart_filter"
            ):

                st.session_state["dashboard_click_filter"] = {
                    "column": selected["column"],
                    "value": point_value
                }

                st.rerun()


# ============================================================
# LINE CHART
# ============================================================

def create_line_chart(df, date_column, value_column):

    chart_df = pd.DataFrame()

    chart_df["Date"] = pd.to_datetime(
        get_series(df, date_column),
        errors="coerce"
    )

    chart_df["Value"] = pd.to_numeric(
        get_series(df, value_column),
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:
        return None

    chart_df = (
        chart_df
        .groupby("Date", as_index=False)["Value"]
        .sum()
        .sort_values("Date")
    )

    fig = px.line(
        chart_df,
        x="Date",
        y="Value",
        markers=True,
        title=f"{value_column} Over Time",
        template="plotly_dark",
        color_discrete_sequence=["#00D4FF"]
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Date:</b> %{x|%d %b %Y}"
            "<br><b>" + value_column + ":</b> %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        hovermode="x unified",
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# BAR CHART
# ============================================================

def create_bar_chart(df, category_column, value_column=None):

    category = (
        get_series(df, category_column)
        .fillna("Missing")
        .astype(str)
    )

    if value_column:

        value = pd.to_numeric(
            get_series(df, value_column),
            errors="coerce"
        )

        chart_df = pd.DataFrame(
            {"Category": category, "Value": value}
        ).dropna()

        grouped = (
            chart_df
            .groupby("Category")["Value"]
            .sum()
            .reset_index()
        )

    else:

        grouped = category.value_counts().reset_index()
        grouped.columns = ["Category", "Value"]

    grouped = grouped.sort_values("Value", ascending=False).head(10)

    if grouped.empty:
        return None

    fig = px.bar(
        grouped,
        x="Category",
        y="Value",
        title=(
            f"{value_column} by {category_column}"
            if value_column
            else f"Records by {category_column}"
        )
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b>"
            "<br><b>Value:</b> %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# PIE CHART
# ============================================================

def create_pie_chart(df, category_column, value_column=None):

    category = (
        get_series(df, category_column)
        .fillna("Missing")
        .astype(str)
    )

    if value_column:

        value = pd.to_numeric(
            get_series(df, value_column),
            errors="coerce"
        )

        chart_df = pd.DataFrame(
            {"Category": category, "Value": value}
        ).dropna()

        grouped = (
            chart_df
            .groupby("Category")["Value"]
            .sum()
            .reset_index()
        )

    else:

        grouped = category.value_counts().reset_index()
        grouped.columns = ["Category", "Value"]

    grouped = grouped.sort_values("Value", ascending=False)

    if len(grouped) > 8:

        top = grouped.head(7)

        others = pd.DataFrame(
            [{"Category": "Others", "Value": grouped.iloc[7:]["Value"].sum()}]
        )

        grouped = pd.concat([top, others], ignore_index=True)

    if grouped.empty:
        return None

    fig = px.pie(
        grouped,
        names="Category",
        values="Value",
        hole=0.48,
        title=(
            f"{value_column} Distribution"
            if value_column
            else f"{category_column} Distribution"
        )
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        hovertemplate=(
            "<b>%{label}</b>"
            "<br><b>Value:</b> %{value:,.2f}"
            "<br><b>Share:</b> %{percent}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# SCATTER PLOT
# ============================================================

def create_scatter_chart(df, x_column, y_column, category_column=None):

    chart_df = pd.DataFrame()

    chart_df["X"] = pd.to_numeric(
        get_series(df, x_column),
        errors="coerce"
    )

    chart_df["Y"] = pd.to_numeric(
        get_series(df, y_column),
        errors="coerce"
    )

    if category_column:
        chart_df["Category"] = (
            get_series(df, category_column)
            .fillna("Missing")
            .astype(str)
        )

    chart_df = chart_df.dropna(subset=["X", "Y"])

    if chart_df.empty:
        return None

    fig = px.scatter(
        chart_df,
        x="X",
        y="Y",
        color="Category" if category_column else None,
        title=f"{y_column} vs {x_column}",
        opacity=0.75
    )

    fig.update_traces(
        hovertemplate=(
            "<b>" + x_column + ":</b> %{x:,.2f}"
            "<br><b>" + y_column + ":</b> %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# HISTOGRAM
# ============================================================

def create_histogram(df, column):

    series = pd.to_numeric(
        get_series(df, column),
        errors="coerce"
    ).dropna()

    if series.empty:
        return None

    chart_df = pd.DataFrame({"Value": series})

    fig = px.histogram(
        chart_df,
        x="Value",
        nbins=30,
        title=f"Distribution of {column}"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Value:</b> %{x}"
            "<br><b>Count:</b> %{y}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# BOX PLOT
# ============================================================

def create_box_chart(df, column, category_column=None):

    chart_df = pd.DataFrame()

    chart_df["Value"] = pd.to_numeric(
        get_series(df, column),
        errors="coerce"
    )

    if category_column:
        chart_df["Category"] = (
            get_series(df, category_column)
            .fillna("Missing")
            .astype(str)
        )

    chart_df = chart_df.dropna(subset=["Value"])

    if chart_df.empty:
        return None

    fig = px.box(
        chart_df,
        y="Value",
        x="Category" if category_column else None,
        points="outliers",
        title=f"Distribution of {column}"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Value:</b> %{y:,.2f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def create_correlation_chart(df):

    numeric_columns = get_useful_numeric_columns(df)

    if len(numeric_columns) < 2:
        return None

    numeric_df = pd.DataFrame()

    for column in numeric_columns:
        numeric_df[column] = pd.to_numeric(
            get_series(df, column),
            errors="coerce"
        )

    correlation = numeric_df.corr()

    fig = px.imshow(
        correlation,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Matrix",
        color_continuous_scale="Blues"
    )

    fig.update_layout(height=550)

    return fig


# ============================================================
# LOCATION MAP
# ============================================================

def create_location_map(df, latitude_column, longitude_column):

    chart_df = pd.DataFrame()

    chart_df["Latitude"] = pd.to_numeric(
        get_series(df, latitude_column),
        errors="coerce"
    )

    chart_df["Longitude"] = pd.to_numeric(
        get_series(df, longitude_column),
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:
        return None

    fig = px.scatter_map(
        chart_df,
        lat="Latitude",
        lon="Longitude",
        zoom=2,
        height=500,
        title="Geographic Distribution"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Latitude:</b> %{lat:.5f}"
            "<br><b>Longitude:</b> %{lon:.5f}"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        map_style="carto-darkmatter",
        margin=dict(l=0, r=0, t=60, b=0)
    )

    return fig


# ============================================================
# TOP / BOTTOM ANALYSIS
# ============================================================

def show_top_bottom_analysis(df, category_column, value_column):

    category = (
        get_series(df, category_column)
        .fillna("Missing")
        .astype(str)
    )

    value = pd.to_numeric(
        get_series(df, value_column),
        errors="coerce"
    )

    analysis_df = pd.DataFrame(
        {"Category": category, "Value": value}
    ).dropna()

    if analysis_df.empty:
        return

    grouped = (
        analysis_df
        .groupby("Category")["Value"]
        .sum()
        .sort_values(ascending=False)
    )

    top_df = grouped.head(5).reset_index()
    bottom_df = grouped.tail(5).sort_values().reset_index()

    top_df.columns = [category_column, value_column]
    bottom_df.columns = [category_column, value_column]

    left, right = st.columns(2)

    with left:
        st.markdown(f"#### 🏆 Top {category_column}")
        st.dataframe(top_df, use_container_width=True, hide_index=True)

    with right:
        st.markdown(f"#### 📉 Bottom {category_column}")
        st.dataframe(bottom_df, use_container_width=True, hide_index=True)


# ============================================================
# AUTOMATIC BI DASHBOARD
# ============================================================

def show_auto_dashboard(df):

    st.markdown(
        '<div class="dashboard-title">🏢 Intelligent BI Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="dashboard-subtitle">'
        'Interactive analytics generated from your dataset'
        '</div>',
        unsafe_allow_html=True
    )

    # ---------------- FILTERS ----------------

    filtered_df = apply_global_filters(df)

    if filtered_df.empty:
        st.warning("No records match the selected filters.")
        return

    # ---------------- SELECTED POINT ----------------

    show_selected_point()

    st.divider()

    # ---------------- KPIs ----------------

    show_kpi_cards(filtered_df)

    st.divider()

    # ---------------- DETECTION ----------------

    numeric_columns = get_useful_numeric_columns(filtered_df)
    categorical_columns = get_useful_categorical_columns(filtered_df)
    date_columns = detect_date_columns(filtered_df)
    latitude_column, longitude_column = detect_location_columns(filtered_df)
    metrics = find_business_metrics(filtered_df)

    # ================= TREND =================

    if date_columns and metrics:

        st.markdown("### 📈 Performance Trend")

        fig = create_line_chart(filtered_df, date_columns[0], metrics[0])

        display_chart(
            fig,
            "dashboard_main_line",
            chart_type="line",
            source_column=date_columns[0],
            allow_click_filter=True
        )

        st.caption("💡 Click any point to see its exact date and value.")

    # ================= BAR + PIE =================

    if categorical_columns:

        st.markdown("### 📊 Category Analysis")

        category_column = categorical_columns[0]
        value_column = metrics[0] if metrics else None

        left, right = st.columns(2)

        with left:

            fig = create_bar_chart(filtered_df, category_column, value_column)

            display_chart(
                fig,
                "dashboard_bar",
                chart_type="bar",
                source_column=category_column,
                allow_click_filter=True
            )

            st.caption("🖱️ Click a bar to inspect the value.")

        with right:

            fig = create_pie_chart(filtered_df, category_column, value_column)

            display_chart(
                fig,
                "dashboard_pie",
                chart_type="pie",
                source_column=category_column,
                allow_click_filter=True
            )

            st.caption("🖱️ Click a slice to inspect the value.")

    # ================= TOP / BOTTOM =================

    if categorical_columns and metrics:

        st.divider()

        show_top_bottom_analysis(
            filtered_df,
            categorical_columns[0],
            metrics[0]
        )

    # ================= SCATTER + HISTOGRAM =================

    if len(numeric_columns) >= 2:

        st.divider()

        st.markdown("### 🔵 Numeric Analysis")

        left, right = st.columns(2)

        with left:

            color_column = (
                categorical_columns[0] if categorical_columns else None
            )

            fig = create_scatter_chart(
                filtered_df,
                numeric_columns[0],
                numeric_columns[1],
                color_column
            )

            display_chart(
                fig,
                "dashboard_scatter",
                chart_type="scatter",
                source_column=None,
                allow_click_filter=True
            )

            st.caption("🖱️ Click a point to inspect X/Y values.")

        with right:

            fig = create_histogram(filtered_df, numeric_columns[0])
            display_chart(fig, "dashboard_histogram")

    elif numeric_columns:

        st.divider()

        st.markdown("### 📊 Numeric Distribution")

        fig = create_histogram(filtered_df, numeric_columns[0])
        display_chart(fig, "dashboard_histogram")

    # ================= BOX =================

    if numeric_columns:

        st.divider()

        st.markdown("### 📦 Distribution & Outliers")

        category_column = (
            categorical_columns[0] if categorical_columns else None
        )

        fig = create_box_chart(
            filtered_df,
            numeric_columns[0],
            category_column
        )

        display_chart(fig, "dashboard_box")

    # ================= CORRELATION =================

    if len(numeric_columns) >= 2:

        st.divider()

        st.markdown("### 🔥 Relationship Analysis")

        fig = create_correlation_chart(filtered_df)
        display_chart(fig, "dashboard_correlation")

    # ================= MAP =================

    if latitude_column and longitude_column:

        st.divider()

        st.markdown("### 📍 Geographic Analysis")

        fig = create_location_map(
            filtered_df,
            latitude_column,
            longitude_column
        )

        display_chart(fig, "dashboard_map")

    # ================= DATA PREVIEW =================

    st.divider()

    with st.expander("👀 View Dashboard Data"):
        st.dataframe(filtered_df, use_container_width=True, height=400)


# ============================================================
# MANUAL CHART BUILDER
# ============================================================

def show_manual_chart_builder(df):

    st.markdown("## 🎛️ Manual Chart Builder")

    numeric_columns = get_numeric_columns(df)
    categorical_columns = get_categorical_columns(df)
    date_columns = detect_date_columns(df)
    latitude_column, longitude_column = detect_location_columns(df)

    chart_type = st.selectbox(
        "Chart Type",
        [
            "Line Chart",
            "Bar Chart",
            "Pie / Donut Chart",
            "Scatter Plot",
            "Histogram",
            "Box Plot",
            "Correlation Heatmap",
            "Location Map"
        ],
        key="manual_chart_type"
    )

    # ================= LINE =================

    if chart_type == "Line Chart":

        if not date_columns or not numeric_columns:
            st.warning("Line charts require a date and numeric column.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox(
                "Date / X Axis", date_columns, key="manual_line_x"
            )

        with col2:
            y_column = st.selectbox(
                "Value / Y Axis", numeric_columns, key="manual_line_y"
            )

        if st.button(
            "📈 Generate Line Chart",
            use_container_width=True,
            key="manual_generate_line"
        ):
            fig = create_line_chart(df, x_column, y_column)

            display_chart(
                fig,
                "manual_line_chart",
                chart_type="line",
                source_column=x_column,
                allow_click_filter=True
            )

    # ================= BAR =================

    elif chart_type == "Bar Chart":

        if not categorical_columns:
            st.warning("A categorical column is required.")
            return

        category = st.selectbox(
            "Category", categorical_columns, key="manual_bar_category"
        )

        value = st.selectbox(
            "Value",
            ["Record Count"] + numeric_columns,
            key="manual_bar_value"
        )

        if st.button(
            "📊 Generate Bar Chart",
            use_container_width=True,
            key="manual_generate_bar"
        ):
            fig = create_bar_chart(
                df,
                category,
                None if value == "Record Count" else value
            )

            display_chart(
                fig,
                "manual_bar_chart",
                chart_type="bar",
                source_column=category,
                allow_click_filter=True
            )

    # ================= PIE =================

    elif chart_type == "Pie / Donut Chart":

        if not categorical_columns:
            st.warning("A categorical column is required.")
            return

        category = st.selectbox(
            "Category", categorical_columns, key="manual_pie_category"
        )

        value = st.selectbox(
            "Value",
            ["Record Count"] + numeric_columns,
            key="manual_pie_value"
        )

        if st.button(
            "🥧 Generate Pie Chart",
            use_container_width=True,
            key="manual_generate_pie"
        ):
            fig = create_pie_chart(
                df,
                category,
                None if value == "Record Count" else value
            )

            display_chart(
                fig,
                "manual_pie_chart",
                chart_type="pie",
                source_column=category,
                allow_click_filter=True
            )

    # ================= SCATTER =================

    elif chart_type == "Scatter Plot":

        if len(numeric_columns) < 2:
            st.warning("Two numeric columns are required.")
            return

        col1, col2 = st.columns(2)

        with col1:
            x_column = st.selectbox(
                "X Axis", numeric_columns, key="manual_scatter_x"
            )

        with col2:
            y_column = st.selectbox(
                "Y Axis",
                numeric_columns,
                index=min(1, len(numeric_columns) - 1),
                key="manual_scatter_y"
            )

        color_column = st.selectbox(
            "Color By",
            ["None"] + categorical_columns,
            key="manual_scatter_color"
        )

        if st.button(
            "🔵 Generate Scatter Plot",
            use_container_width=True,
            key="manual_generate_scatter"
        ):
            fig = create_scatter_chart(
                df,
                x_column,
                y_column,
                None if color_column == "None" else color_column
            )

            display_chart(
                fig,
                "manual_scatter_chart",
                chart_type="scatter",
                source_column=None,
                allow_click_filter=True
            )

    # ================= HISTOGRAM =================

    elif chart_type == "Histogram":

        if not numeric_columns:
            st.warning("A numeric column is required.")
            return

        column = st.selectbox(
            "Numerical Column",
            numeric_columns,
            key="manual_histogram_column"
        )

        if st.button(
            "📊 Generate Histogram",
            use_container_width=True,
            key="manual_generate_histogram"
        ):
            fig = create_histogram(df, column)
            display_chart(fig, "manual_histogram_chart")

    # ================= BOX =================

    elif chart_type == "Box Plot":

        if not numeric_columns:
            st.warning("A numeric column is required.")
            return

        column = st.selectbox(
            "Numerical Column", numeric_columns, key="manual_box_column"
        )

        group = st.selectbox(
            "Group By",
            ["None"] + categorical_columns,
            key="manual_box_group"
        )

        if st.button(
            "📦 Generate Box Plot",
            use_container_width=True,
            key="manual_generate_box"
        ):
            fig = create_box_chart(
                df,
                column,
                None if group == "None" else group
            )

            display_chart(fig, "manual_box_chart")

    # ================= CORRELATION =================

    elif chart_type == "Correlation Heatmap":

        if len(numeric_columns) < 2:
            st.warning("At least two numeric columns are required.")
            return

        fig = create_correlation_chart(df)
        display_chart(fig, "manual_correlation_chart")

    # ================= MAP =================

    elif chart_type == "Location Map":

        if latitude_column is None or longitude_column is None:
            st.warning("Latitude and longitude columns were not detected.")
            return

        if st.button(
            "📍 Generate Location Map",
            use_container_width=True,
            key="manual_generate_map"
        ):
            fig = create_location_map(df, latitude_column, longitude_column)
            display_chart(fig, "manual_location_chart")


# ============================================================
# MAIN FUNCTION
# ============================================================

def show_visualizations():

    st.title("📊 Dashboard & Visualizations")

    st.caption(
        "Transform your uploaded dataset into "
        "an interactive business intelligence dashboard."
    )

    # ---------------- GET DATASET ----------------

    df = st.session_state.get("df")

    if df is None:
        st.warning("📂 Please upload a dataset first.")
        return

    if not isinstance(df, pd.DataFrame):
        st.error("❌ Invalid dataset.")
        return

    if df.empty:
        st.warning("⚠️ The dataset is empty.")
        return

    # ---------------- DUPLICATE COLUMN CHECK ----------------

    column_names = [clean_column_name(column) for column in df.columns]

    duplicate_count = int(pd.Series(column_names).duplicated().sum())

    if duplicate_count > 0:
        st.warning(
            f"⚠️ {duplicate_count} duplicate column name(s) detected. "
            "The dashboard will safely use the first occurrence."
        )

    # ---------------- TABS ----------------

    dashboard_tab, manual_tab = st.tabs(
        ["🏢 BI Dashboard", "🎛️ Manual Chart Builder"]
    )

    with dashboard_tab:
        show_auto_dashboard(df)

    with manual_tab:
        show_manual_chart_builder(df)
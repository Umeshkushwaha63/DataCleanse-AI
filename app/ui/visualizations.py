import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# BASIC COLUMN HELPERS
# ============================================================

def get_unique_columns(df):

    """
    Return column names without duplicates.

    Pandas allows duplicate column names, but charts and
    analysis become difficult to handle when that happens.
    """

    seen = set()
    columns = []

    for column in df.columns:

        column_name = str(column)

        if column_name not in seen:

            columns.append(column)
            seen.add(column_name)

    return columns


def get_numeric_columns(df):

    columns = []

    for column in get_unique_columns(df):

        series = df[column]

        # If duplicate column names exist, skip them
        if isinstance(series, pd.DataFrame):
            continue

        if pd.api.types.is_numeric_dtype(series):

            columns.append(column)

    return columns


def get_categorical_columns(df):

    columns = []

    for column in get_unique_columns(df):

        series = df[column]

        if isinstance(series, pd.DataFrame):
            continue

        if (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_categorical_dtype(series)
            or pd.api.types.is_bool_dtype(series)
        ):

            columns.append(column)

    return columns


# ============================================================
# DATE DETECTION
# ============================================================

def detect_date_columns(df):

    date_columns = []

    for column in get_unique_columns(df):

        series = df[column]

        # Ignore duplicate-column DataFrames
        if isinstance(series, pd.DataFrame):

            continue

        # Already datetime
        if pd.api.types.is_datetime64_any_dtype(series):

            date_columns.append(column)

            continue

        column_name = str(
            column
        ).lower().strip()

        date_keywords = [
            "date",
            "time",
            "month",
            "year",
            "day"
        ]

        looks_like_date = any(
            keyword in column_name
            for keyword in date_keywords
        )

        if not looks_like_date:

            continue

        try:

            converted = pd.to_datetime(
                series,
                errors="coerce"
            )

            if len(series) == 0:

                continue

            valid_ratio = (
                converted.notna().mean()
            )

            if valid_ratio >= 0.70:

                date_columns.append(
                    column
                )

        except Exception:

            continue

    return date_columns


# ============================================================
# LOCATION DETECTION
# ============================================================

def detect_location_columns(df):

    latitude_column = None
    longitude_column = None

    for column in get_unique_columns(df):

        column_name = (
            str(column)
            .lower()
            .strip()
        )

        if column_name in [
            "latitude",
            "lat",
            "latitude_deg"
        ]:

            latitude_column = column

        elif column_name in [
            "longitude",
            "long",
            "lng",
            "longitude_deg"
        ]:

            longitude_column = column

    return (
        latitude_column,
        longitude_column
    )


# ============================================================
# SAFE SERIES FUNCTION
# ============================================================

def get_series(df, column):

    """
    Safely return one column as a Pandas Series.

    This prevents problems caused by duplicate column names.
    """

    if column not in df.columns:

        return None

    series = df[column]

    if isinstance(
        series,
        pd.DataFrame
    ):

        # If duplicate columns exist, use first one
        series = series.iloc[:, 0]

    return series


# ============================================================
# CHART RECOMMENDATIONS
# ============================================================

def recommend_charts(df):

    numeric_columns = (
        get_numeric_columns(df)
    )

    categorical_columns = (
        get_categorical_columns(df)
    )

    date_columns = (
        detect_date_columns(df)
    )

    latitude_column, longitude_column = (
        detect_location_columns(df)
    )

    recommendations = []

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    if (
        latitude_column is not None
        and longitude_column is not None
    ):

        recommendations.append(
            {
                "type": "Map",
                "reason": (
                    "Latitude and longitude "
                    "columns were detected."
                ),
                "columns": [
                    latitude_column,
                    longitude_column
                ]
            }
        )

    # --------------------------------------------------------
    # LINE CHART
    # --------------------------------------------------------

    if (
        date_columns
        and numeric_columns
    ):

        recommendations.append(
            {
                "type": "Line Chart",
                "reason": (
                    "A date/time column and "
                    "numeric column were detected."
                ),
                "columns": [
                    date_columns[0],
                    numeric_columns[0]
                ]
            }
        )

    # --------------------------------------------------------
    # BAR CHART
    # --------------------------------------------------------

    if (
        categorical_columns
        and numeric_columns
    ):

        recommendations.append(
            {
                "type": "Bar Chart",
                "reason": (
                    "A categorical column and "
                    "numeric column were detected."
                ),
                "columns": [
                    categorical_columns[0],
                    numeric_columns[0]
                ]
            }
        )

    # --------------------------------------------------------
    # SCATTER
    # --------------------------------------------------------

    if len(numeric_columns) >= 2:

        recommendations.append(
            {
                "type": "Scatter Plot",
                "reason": (
                    "Multiple numeric columns "
                    "were detected."
                ),
                "columns": [
                    numeric_columns[0],
                    numeric_columns[1]
                ]
            }
        )

    # --------------------------------------------------------
    # BOX PLOT
    # --------------------------------------------------------

    if numeric_columns:

        recommendations.append(
            {
                "type": "Box Plot",
                "reason": (
                    "A numeric column can be "
                    "used to inspect spread "
                    "and outliers."
                ),
                "columns": [
                    numeric_columns[0]
                ]
            }
        )

    # --------------------------------------------------------
    # HISTOGRAM
    # --------------------------------------------------------

    if numeric_columns:

        recommendations.append(
            {
                "type": "Histogram",
                "reason": (
                    "A numeric column can be "
                    "used to inspect distribution."
                ),
                "columns": [
                    numeric_columns[0]
                ]
            }
        )

    return recommendations


# ============================================================
# LINE CHART
# ============================================================

def show_line_chart(
    df,
    date_column,
    value_column
):

    date_series = get_series(
        df,
        date_column
    )

    value_series = get_series(
        df,
        value_column
    )

    if (
        date_series is None
        or value_series is None
    ):

        st.warning(
            "The selected columns could not be used."
        )

        return

    chart_df = pd.DataFrame(
        {
            "date": date_series,
            "value": value_series
        }
    )

    chart_df["date"] = pd.to_datetime(
        chart_df["date"],
        errors="coerce"
    )

    chart_df["value"] = pd.to_numeric(
        chart_df["value"],
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:

        st.warning(
            "Not enough valid data for a line chart."
        )

        return

    chart_df = chart_df.sort_values(
        "date"
    )

    fig, ax = plt.subplots()

    ax.plot(
        chart_df["date"],
        chart_df["value"]
    )

    ax.set_xlabel(
        date_column
    )

    ax.set_ylabel(
        value_column
    )

    ax.set_title(
        f"{value_column} over time"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# BAR CHART
# ============================================================

def show_bar_chart(
    df,
    category_column,
    value_column
):

    category_series = get_series(
        df,
        category_column
    )

    value_series = get_series(
        df,
        value_column
    )

    if (
        category_series is None
        or value_series is None
    ):

        st.warning(
            "The selected columns could not be used."
        )

        return

    chart_df = pd.DataFrame(
        {
            "category": category_series,
            "value": value_series
        }
    )

    chart_df["value"] = pd.to_numeric(
        chart_df["value"],
        errors="coerce"
    )

    chart_df = chart_df.dropna(
        subset=["value"]
    )

    if chart_df.empty:

        st.warning(
            "Not enough valid data for a bar chart."
        )

        return

    grouped = (
        chart_df
        .groupby(
            "category",
            dropna=False
        )["value"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(15)
    )

    fig, ax = plt.subplots()

    ax.bar(
        grouped.index.astype(str),
        grouped.values
    )

    ax.set_xlabel(
        category_column
    )

    ax.set_ylabel(
        value_column
    )

    ax.set_title(
        f"{value_column} by {category_column}"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# SCATTER PLOT
# ============================================================

def show_scatter_plot(
    df,
    x_column,
    y_column
):

    x_series = get_series(
        df,
        x_column
    )

    y_series = get_series(
        df,
        y_column
    )

    if (
        x_series is None
        or y_series is None
    ):

        st.warning(
            "The selected columns could not be used."
        )

        return

    chart_df = pd.DataFrame(
        {
            "x": x_series,
            "y": y_series
        }
    )

    chart_df["x"] = pd.to_numeric(
        chart_df["x"],
        errors="coerce"
    )

    chart_df["y"] = pd.to_numeric(
        chart_df["y"],
        errors="coerce"
    )

    chart_df = chart_df.dropna()

    if chart_df.empty:

        st.warning(
            "Not enough valid data for a scatter plot."
        )

        return

    fig, ax = plt.subplots()

    ax.scatter(
        chart_df["x"],
        chart_df["y"]
    )

    ax.set_xlabel(
        x_column
    )

    ax.set_ylabel(
        y_column
    )

    ax.set_title(
        f"{y_column} vs {x_column}"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# BOX PLOT
# ============================================================

def show_box_plot(
    df,
    column
):

    series = get_series(
        df,
        column
    )

    if series is None:

        st.warning(
            "The selected column could not be used."
        )

        return

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if values.empty:

        st.warning(
            "No numerical values are available."
        )

        return

    fig, ax = plt.subplots()

    ax.boxplot(
        values
    )

    ax.set_ylabel(
        column
    )

    ax.set_title(
        f"Box Plot - {column}"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# HISTOGRAM
# ============================================================

def show_histogram(
    df,
    column
):

    series = get_series(
        df,
        column
    )

    if series is None:

        st.warning(
            "The selected column could not be used."
        )

        return

    values = pd.to_numeric(
        series,
        errors="coerce"
    ).dropna()

    if values.empty:

        st.warning(
            "No numerical values are available."
        )

        return

    fig, ax = plt.subplots()

    ax.hist(
        values,
        bins=30
    )

    ax.set_xlabel(
        column
    )

    ax.set_ylabel(
        "Frequency"
    )

    ax.set_title(
        f"Distribution of {column}"
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# LOCATION MAP
# ============================================================

def show_location_map(
    df,
    latitude_column,
    longitude_column
):

    latitude_series = get_series(
        df,
        latitude_column
    )

    longitude_series = get_series(
        df,
        longitude_column
    )

    if (
        latitude_series is None
        or longitude_series is None
    ):

        st.warning(
            "Location columns could not be used."
        )

        return

    map_df = pd.DataFrame(
        {
            "latitude": pd.to_numeric(
                latitude_series,
                errors="coerce"
            ),
            "longitude": pd.to_numeric(
                longitude_series,
                errors="coerce"
            )
        }
    )

    map_df = map_df.dropna()

    map_df = map_df[
        (
            map_df["latitude"] >= -90
        )
        &
        (
            map_df["latitude"] <= 90
        )
        &
        (
            map_df["longitude"] >= -180
        )
        &
        (
            map_df["longitude"] <= 180
        )
    ]

    if map_df.empty:

        st.warning(
            "No valid geographic coordinates were found."
        )

        return

    st.map(
        map_df,
        use_container_width=True
    )


# ============================================================
# CORRELATION HEATMAP
# ============================================================

def show_correlation_heatmap(df):

    numeric_columns = (
        get_numeric_columns(df)
    )

    if len(numeric_columns) < 2:

        st.info(
            "At least two numeric columns "
            "are required for correlation analysis."
        )

        return

    numeric_df = df[
        numeric_columns
    ].copy()

    correlation = (
        numeric_df.corr()
    )

    fig, ax = plt.subplots()

    image = ax.imshow(
        correlation,
        aspect="auto"
    )

    ax.set_xticks(
        range(
            len(correlation.columns)
        )
    )

    ax.set_yticks(
        range(
            len(correlation.columns)
        )
    )

    ax.set_xticklabels(
        correlation.columns,
        rotation=45,
        ha="right"
    )

    ax.set_yticklabels(
        correlation.columns
    )

    ax.set_title(
        "Correlation Heatmap"
    )

    fig.colorbar(
        image,
        ax=ax
    )

    plt.tight_layout()

    st.pyplot(
        fig,
        clear_figure=True
    )


# ============================================================
# AUTO DASHBOARD
# ============================================================

def show_auto_dashboard(df):

    st.subheader(
        "🤖 Auto Visualization Dashboard"
    )

    st.caption(
        "Charts are selected automatically "
        "based on your dataset."
    )

    recommendations = recommend_charts(
        df
    )

    if not recommendations:

        st.warning(
            "No suitable visualizations were detected."
        )

        return

    for recommendation in recommendations:

        chart_type = recommendation[
            "type"
        ]

        reason = recommendation[
            "reason"
        ]

        columns = recommendation[
            "columns"
        ]

        st.markdown(
            f"### {chart_type}"
        )

        st.caption(
            reason
        )

        if chart_type == "Line Chart":

            show_line_chart(
                df,
                columns[0],
                columns[1]
            )

        elif chart_type == "Bar Chart":

            show_bar_chart(
                df,
                columns[0],
                columns[1]
            )

        elif chart_type == "Scatter Plot":

            show_scatter_plot(
                df,
                columns[0],
                columns[1]
            )

        elif chart_type == "Box Plot":

            show_box_plot(
                df,
                columns[0]
            )

        elif chart_type == "Histogram":

            show_histogram(
                df,
                columns[0]
            )

        elif chart_type == "Map":

            show_location_map(
                df,
                columns[0],
                columns[1]
            )

        st.divider()

    st.subheader(
        "🔗 Correlation Overview"
    )

    show_correlation_heatmap(
        df
    )


# ============================================================
# MANUAL CHART BUILDER
# ============================================================

def show_manual_chart_builder(df):

    st.subheader(
        "🎛️ Manual Chart Builder"
    )

    numeric_columns = (
        get_numeric_columns(df)
    )

    categorical_columns = (
        get_categorical_columns(df)
    )

    date_columns = (
        detect_date_columns(df)
    )

    latitude_column, longitude_column = (
        detect_location_columns(df)
    )

    chart_type = st.selectbox(
        "Chart Type",
        [
            "Line Chart",
            "Bar Chart",
            "Scatter Plot",
            "Box Plot",
            "Histogram",
            "Map"
        ],
        key="manual_chart_type"
    )

    # --------------------------------------------------------
    # LINE
    # --------------------------------------------------------

    if chart_type == "Line Chart":

        if not date_columns:

            st.warning(
                "No date/time column detected."
            )

            return

        if not numeric_columns:

            st.warning(
                "No numeric column detected."
            )

            return

        x_column = st.selectbox(
            "Date / Time Column",
            date_columns,
            key="manual_line_x"
        )

        y_column = st.selectbox(
            "Value Column",
            numeric_columns,
            key="manual_line_y"
        )

        if st.button(
            "📈 Generate Line Chart",
            use_container_width=True,
            key="generate_line_chart"
        ):

            show_line_chart(
                df,
                x_column,
                y_column
            )

    # --------------------------------------------------------
    # BAR
    # --------------------------------------------------------

    elif chart_type == "Bar Chart":

        if not categorical_columns:

            st.warning(
                "No categorical column detected."
            )

            return

        if not numeric_columns:

            st.warning(
                "No numeric column detected."
            )

            return

        x_column = st.selectbox(
            "Category Column",
            categorical_columns,
            key="manual_bar_x"
        )

        y_column = st.selectbox(
            "Value Column",
            numeric_columns,
            key="manual_bar_y"
        )

        if st.button(
            "📊 Generate Bar Chart",
            use_container_width=True,
            key="generate_bar_chart"
        ):

            show_bar_chart(
                df,
                x_column,
                y_column
            )

    # --------------------------------------------------------
    # SCATTER
    # --------------------------------------------------------

    elif chart_type == "Scatter Plot":

        if len(numeric_columns) < 2:

            st.warning(
                "At least two numeric columns "
                "are required."
            )

            return

        x_column = st.selectbox(
            "X Axis",
            numeric_columns,
            key="manual_scatter_x"
        )

        y_column = st.selectbox(
            "Y Axis",
            numeric_columns,
            key="manual_scatter_y"
        )

        if st.button(
            "🔵 Generate Scatter Plot",
            use_container_width=True,
            key="generate_scatter_chart"
        ):

            show_scatter_plot(
                df,
                x_column,
                y_column
            )

    # --------------------------------------------------------
    # BOX
    # --------------------------------------------------------

    elif chart_type == "Box Plot":

        if not numeric_columns:

            st.warning(
                "No numeric columns available."
            )

            return

        column = st.selectbox(
            "Numerical Column",
            numeric_columns,
            key="manual_box_column"
        )

        if st.button(
            "📦 Generate Box Plot",
            use_container_width=True,
            key="generate_box_chart"
        ):

            show_box_plot(
                df,
                column
            )

    # --------------------------------------------------------
    # HISTOGRAM
    # --------------------------------------------------------

    elif chart_type == "Histogram":

        if not numeric_columns:

            st.warning(
                "No numeric columns available."
            )

            return

        column = st.selectbox(
            "Numerical Column",
            numeric_columns,
            key="manual_histogram_column"
        )

        if st.button(
            "📊 Generate Histogram",
            use_container_width=True,
            key="generate_histogram"
        ):

            show_histogram(
                df,
                column
            )

    # --------------------------------------------------------
    # MAP
    # --------------------------------------------------------

    elif chart_type == "Map":

        if (
            latitude_column is None
            or longitude_column is None
        ):

            st.warning(
                "Latitude and longitude columns "
                "were not detected."
            )

            return

        st.success(
            f"Using {latitude_column} + "
            f"{longitude_column}"
        )

        if st.button(
            "🌍 Generate Map",
            use_container_width=True,
            key="generate_map"
        ):

            show_location_map(
                df,
                latitude_column,
                longitude_column
            )


# ============================================================
# MAIN VISUALIZATION PAGE
# ============================================================

def show_visualizations():

    st.title(
        "📈 Visualizations & Insights"
    )

    st.caption(
        "DataCleanse AI automatically recommends "
        "visualizations based on your dataset."
    )

    # --------------------------------------------------------
    # GET DATASET
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # DUPLICATE COLUMN WARNING
    # --------------------------------------------------------

    column_names = [
        str(column)
        for column in df.columns
    ]

    duplicate_names = (
        pd.Series(column_names)
        .duplicated()
    )

    duplicate_count = int(
        duplicate_names.sum()
    )

    if duplicate_count > 0:

        st.warning(
            f"⚠️ Your dataset contains "
            f"{duplicate_count} duplicate column name(s). "
            f"The visualization engine will safely use "
            f"the first occurrence."
        )

    # --------------------------------------------------------
    # OVERVIEW
    # --------------------------------------------------------

    numeric_columns = (
        get_numeric_columns(df)
    )

    categorical_columns = (
        get_categorical_columns(df)
    )

    date_columns = (
        detect_date_columns(df)
    )

    latitude_column, longitude_column = (
        detect_location_columns(df)
    )

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
            "Numeric Columns",
            len(numeric_columns)
        )

    with col4:

        st.metric(
            "Categorical Columns",
            len(categorical_columns)
        )

    # --------------------------------------------------------
    # COLUMN DETECTION
    # --------------------------------------------------------

    st.divider()

    st.subheader(
        "🔍 Column Detection"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            "🔢 **Numeric**"
        )

        if numeric_columns:

            for column in numeric_columns:

                st.write(
                    f"• {column}"
                )

        else:

            st.caption(
                "None detected"
            )

    with col2:

        st.write(
            "🏷️ **Categorical**"
        )

        if categorical_columns:

            for column in categorical_columns:

                st.write(
                    f"• {column}"
                )

        else:

            st.caption(
                "None detected"
            )

    with col3:

        st.write(
            "📅 **Date / Time**"
        )

        if date_columns:

            for column in date_columns:

                st.write(
                    f"• {column}"
                )

        else:

            st.caption(
                "None detected"
            )

        if (
            latitude_column
            and longitude_column
        ):

            st.success(
                "🌍 Location detected"
            )

    # --------------------------------------------------------
    # TABS
    # --------------------------------------------------------

    st.divider()

    auto_tab, manual_tab = st.tabs(
        [
            "🤖 Auto Dashboard",
            "🎛️ Manual Chart Builder"
        ]
    )

    with auto_tab:

        show_auto_dashboard(
            df
        )

    with manual_tab:

        show_manual_chart_builder(
            df
        )
import pandas as pd
import numpy as np


def scan_dataset(df):

    results = {
        "missing_values": [],
        "duplicates": 0,
        "empty_columns": [],
        "constant_columns": [],
        "mixed_types": [],
        "category_inconsistencies": [],
        "date_issues": [],
        "outliers": [],
        "whitespace_issues": [],
    }

    # ---------------------------------------------
    # 1. Missing values
    # ---------------------------------------------

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        if missing_count > 0:

            percentage = round(
                (missing_count / len(df)) * 100,
                2
            )

            results["missing_values"].append({
                "column": column,
                "count": missing_count,
                "percentage": percentage
            })

    # ---------------------------------------------
    # 2. Duplicate rows
    # ---------------------------------------------

    results["duplicates"] = int(
        df.duplicated().sum()
    )

    # ---------------------------------------------
    # 3. Empty columns
    # ---------------------------------------------

    for column in df.columns:

        if df[column].isna().all():

            results["empty_columns"].append(column)

    # ---------------------------------------------
    # 4. Constant columns
    # ---------------------------------------------

    for column in df.columns:

        unique_count = df[column].nunique(
            dropna=False
        )

        if unique_count <= 1:

            results["constant_columns"].append(
                column
            )

    # ---------------------------------------------
    # 5. Mixed data types
    # ---------------------------------------------

    for column in df.columns:

        values = df[column].dropna()

        if values.empty:
            continue

        type_count = values.map(type).nunique()

        if type_count > 1:

            results["mixed_types"].append(column)

    # ---------------------------------------------
    # 6. Category inconsistencies
    # ---------------------------------------------

    text_columns = df.select_dtypes(
        include=["object", "string"]
    ).columns

    for column in text_columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
            .str.strip()
        )

        if values.empty:
            continue

        groups = {}

        for value in values.unique():

            key = value.lower()

            groups.setdefault(
                key,
                []
            ).append(value)

        for key, variants in groups.items():

            if len(variants) > 1:

                results[
                    "category_inconsistencies"
                ].append({
                    "column": column,
                    "values": variants
                })

    # ---------------------------------------------
    # 7. Date issues
    # ---------------------------------------------

    for column in text_columns:

        values = df[column].dropna()

        if values.empty:
            continue

        sample = (
            values
            .astype(str)
            .head(100)
        )

        converted = pd.to_datetime(
            sample,
            errors="coerce"
        )

        valid_ratio = converted.notna().mean()

        if 0.7 < valid_ratio < 1:

            results["date_issues"].append(
                column
            )

    # ---------------------------------------------
    # 8. Outliers
    # ---------------------------------------------

    numeric_columns = df.select_dtypes(
        include=np.number
    ).columns

    for column in numeric_columns:

        series = df[column].dropna()

        if len(series) < 4:
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        if iqr == 0:
            continue

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outlier_count = int(
            (
                (series < lower)
                |
                (series > upper)
            ).sum()
        )

        if outlier_count > 0:

            results["outliers"].append({
                "column": column,
                "count": outlier_count
            })

    # ---------------------------------------------
    # 9. Whitespace issues
    # ---------------------------------------------

    for column in text_columns:

        values = (
            df[column]
            .dropna()
            .astype(str)
        )

        whitespace_count = int(
            (
                values != values.str.strip()
            ).sum()
        )

        if whitespace_count > 0:

            results["whitespace_issues"].append({
                "column": column,
                "count": whitespace_count
            })

    return results


def calculate_quality_score(
    results,
    total_columns
):

    issue_count = 0

    issue_count += len(
        results["missing_values"]
    )

    if results["duplicates"] > 0:

        issue_count += 1

    issue_count += len(
        results["empty_columns"]
    )

    issue_count += len(
        results["constant_columns"]
    )

    issue_count += len(
        results["mixed_types"]
    )

    issue_count += len(
        results["category_inconsistencies"]
    )

    issue_count += len(
        results["date_issues"]
    )

    issue_count += len(
        results["outliers"]
    )

    issue_count += len(
        results["whitespace_issues"]
    )

    if total_columns == 0:

        return 100

    # Every detected issue category
    # reduces the score by 5 points.

    penalty = min(
        issue_count * 5,
        100
    )

    score = max(
        0,
        100 - penalty
    )

    return score
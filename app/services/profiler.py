import pandas as pd


def profile_dataset(df: pd.DataFrame) -> dict:
    """
    Generate a structured profile of the uploaded dataset.
    """

    profile = {
        "Rows": int(df.shape[0]),
        "Columns": int(df.shape[1]),
        "Missing Values": int(df.isna().sum().sum()),
        "Duplicate Rows": int(df.duplicated().sum()),
        "Column Details": {},
    }

    for column in df.columns:

        series = df[column]

        profile["Column Details"][column] = {
            "dtype": str(series.dtype),
            "missing": int(series.isna().sum()),
            "missing_percentage": round(
                (series.isna().sum() / len(df)) * 100,
                2,
            ) if len(df) else 0,
            "unique_values": int(series.nunique()),
            "unique_percentage": round(
                (series.nunique() / len(df)) * 100,
                2,
            ) if len(df) else 0,
        }

    return profile
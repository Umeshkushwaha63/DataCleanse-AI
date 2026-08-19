import pandas as pd


def fill_missing(df, column, method, custom_value=None):

    if method == "Mean":
        df[column] = df[column].fillna(df[column].mean())

    elif method == "Median":
        df[column] = df[column].fillna(df[column].median())

    elif method == "Mode":
        df[column] = df[column].fillna(df[column].mode()[0])

    elif method == "Forward Fill":
        df[column] = df[column].ffill()

    elif method == "Backward Fill":
        df[column] = df[column].bfill()

    elif method == "Custom Value":
        df[column] = df[column].fillna(custom_value)

    return df


def remove_duplicates(df):
    return df.drop_duplicates()


def remove_empty_columns(df):
    return df.dropna(axis=1, how="all")
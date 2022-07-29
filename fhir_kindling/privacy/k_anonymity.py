from typing import List
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
from pandas.api.types import is_numeric_dtype, is_string_dtype, is_categorical_dtype


def is_k_anonymized(
        df: pd.DataFrame,
        k: int = 3,
        id_cols: List[str] = None,
        excluded_cols: List[str] = None,
) -> bool:
    """

    Checks if a dataframe satisfies k-anonymity for the given k. If id_cols is given only these columns are checked
    :param df: pandas dataframe to check
    :param k: k value to check for
    :param id_cols: optional list of columns to check for k-anonymity
    :param excluded_cols: optional list of columns to exclude from the k-anonymity check
    :return: bool value indicating whether the dataframe satisfies k-anonymity
    """

    for index, row in df.iterrows():
        query = _make_k_anon_query_for_row(row, df, excluded_cols=excluded_cols, id_cols=id_cols)
        rows = df.query(query)
        if rows.shape[0] < k:
            return False
    return True


def anonymize(df: pd.DataFrame, k: int = 3, id_cols: List[str] = None) -> pd.DataFrame:
    """
    Attempts to generalize the given dataframe to make it k-anonymized

    :param df: dataframe to check
    :param k: k value to check for
    :param id_cols: optional parameter specifying a subset of columns in the dataframe to generalize
    :return: anonymized dataframe
    """
    anon_df = df.copy()
    # If id cols are given anonymize those otherwise use all columns
    for col in id_cols if id_cols else df.columns:
        if is_datetime(df[col]):
            print("Datetime column detected")
            anon_df[col] = generalize_datetime_column(df[col])

        elif is_numeric_dtype(df[col]):
            print("Numeric column detected")
            anon_df[col] = generalize_numeric_column(df[col])

        elif is_string_dtype(df[col]) or is_categorical_dtype(df[col]):
            print("String column detected")
            # TODO categorical/string variable handling
            anon_df[col] = df[col]

        else:
            print("Unknown column type:", df[col].dtype)
            anon_df[col] = anon_df[col]

    if is_k_anonymized(anon_df, k=k):
        return anon_df

    else:
        print("More generalization required")


def _make_k_anon_query_for_row(row: pd.Series, df: pd.DataFrame, excluded_cols: List[str] = None,
                               id_cols: List[str] = None) -> str:
    """
    Creates a query string for a given row of a dataframe to check if there are enough rows in the dataframe to satisfy
    k-anonymity
    :param row: the row of a dataframe to check
    :param df: underlying dataframe
    :param excluded_cols: columns in the dataframe to exclude from the k-anonymity check
    :param id_cols:
    :return: query string to run against the dataframe
    """
    if id_cols:
        cols = id_cols
    else:
        if excluded_cols:
            cols = [col for col in df.columns if col not in excluded_cols]
        else:
            cols = df.columns
    query_cols = []
    for col in cols:
        if isinstance(row[col], int) or isinstance(row[col], float):
            query_cols.append(f"{col} == {row[col]}")
        else:
            query_cols.append(f"{col} == '{row[col]}'")
    query = ' & '.join(query_cols)

    return query


def generalize_numeric_column(num_col: pd.Series):
    return num_col


def generalize_datetime_column(date_col: pd.Series, level: int = 2):
    col = pd.to_datetime(date_col)

    if level == 2:
        generalized_col = col.apply(lambda x: x.strftime('m-%Y'))
        return pd.to_datetime(generalized_col)

    elif level == 3:
        generalized_col = col.apply(lambda x: x.strftime('%Y'))
        return pd.to_datetime(generalized_col)

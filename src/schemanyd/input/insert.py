from typing import Any, Dict, Union
from io import BytesIO

import polars as pl
import pandas as pd


# - - - - - Wrapper Functions - Convert various data types to CSV BytesIO (file-like) - - - - -

def csv_from_dicts(data_dicts: list[dict[str, Any]]) -> BytesIO:
    """
    Convert a list of dictionaries to CSV bytes.

    Parameters
    ----------
    data_dicts: list[dict[str, Any]]
        Iterable of dictionaries that should be converted into CSV format.

    Returns
    -------
    BytesIO
        An in-memory binary file-like object (positioned at start) containing the UTF-8
        encoded CSV representation of the provided dictionaries.
    """
    df = pl.DataFrame(data_dicts)
    buffer = BytesIO(df.write_csv().encode('utf-8'))
    buffer.seek(0)
    return buffer


def csv_from_polars(df: pl.DataFrame) -> BytesIO:
    """
    Convert a Polars DataFrame to CSV bytes.

    Parameters
    ----------
    df: pl.DataFrame
        DataFrame to serialize to CSV.

    Returns
    -------
    BytesIO
        An in-memory binary file-like object (positioned at start) containing the UTF-8
        encoded CSV representation of the DataFrame.
    """
    buffer = BytesIO(df.write_csv().encode('utf-8'))
    buffer.seek(0)
    return buffer


def csv_from_pandas(df: 'pd.DataFrame') -> BytesIO:
    """
    Convert a Pandas DataFrame to CSV bytes.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to serialize to CSV. Index is ignored.

    Returns
    -------
    BytesIO
        An in-memory binary file-like object (positioned at start) containing the UTF-8
        encoded CSV representation of the DataFrame.
    """
    buffer = BytesIO(df.to_csv(index=False).encode('utf-8'))
    buffer.seek(0)
    return buffer


def csv_from_csv_file(file_path: str) -> BytesIO:
    """
    Read a CSV file from disk and return its bytes.

    Parameters
    ----------
    file_path: str
        Absolute or relative path to the CSV file.

    Returns
    -------
    BytesIO
        An in-memory binary file-like object (positioned at start) containing the raw
        file contents as bytes.
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    buffer = BytesIO(data)
    buffer.seek(0)
    return buffer


def csv_from_excel_file(file_path: str, sheet_name: Union[str, int, None] = None) -> BytesIO:
    """
    Convert an Excel sheet to CSV bytes.

    Parameters
    ----------
    file_path: str
        Absolute or relative path to the Excel file (.xlsx or .xls).
    sheet_name: Union[str, int, None], optional
        Sheet identifier to read. Defaults to the first sheet when omitted.

    Returns
    -------
    BytesIO
        An in-memory binary file-like object (positioned at start) containing the UTF-8
        encoded CSV representation of the selected sheet.
    """
    if sheet_name is None:
        df = pl.read_excel(file_path)
    else:
        df = pl.read_excel(file_path, sheet_name=sheet_name)

    buffer = BytesIO(df.write_csv().encode('utf-8'))
    buffer.seek(0)
    return buffer

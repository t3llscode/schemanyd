from typing import Any, Dict, Union
from io import BytesIO

import polars as pl
import pandas as pd


# - - - - - Core Insertion Function - CSV bytes → Temporary Table → into Final Tables - - - - -

def insert(csv_file: bytes, column_mapping: Dict[str, str]) -> None:
    """
    Insert data from CSV bytes into database using Schemanyd Autotrace Logic.
    
    Parameters
    ------------------------------------------------------------------------------------------------------------------------
    csv_file: bytes
        CSV data as bytes (in-memory, no disk file required). Use `csv_from_...()` functions for other supported formats.
    column_mapping: Dict[str, str]
        A mapping of CSV column names to database table column names.


    Example
    ------------------------------------------------------------------------------------------------------------------------
    #### `csv_file`
    ```
    'name','citizenship','destination','country'
    'Tell','Germany','Züricher See','Switzerland'
    ```

    #### `column_mapping`
    ```
    {
        'name': 'traveler.name',                 # "Tell"
        'citizenship': 'traveler/country.name',  # "Germany"
        'destination': 'destination.name',       # "Züricher See"
        'country': 'destination/country.name'    # "Switzerland"
    }
    ```

    Result
    ------------------------------------------------------------------------------------------------------------------------
    ```
    traveler                      destination                            country             
    | id | name | country_id |    | id | name         | country_id |     | id | name        |
    |----|------|------------|    |----|--------------|------------|     |----|-------------|
    | 10 | Tell | 1          |    | 20 | Züricher See | 2          |     | 1  | Germany     |
                                                                         | 2  | Switzerland |
    ```

    `column_mapping` Syntax
    ------------------------------------------------------------------------------------------------------------------------
    If there are multiple links to the same table, use `/` to distinguish them. <br>
    `. = Schemanyd.seperator_rf(default)` - seperator between relation and field <br>
    `/ = Schemanyd.seperator_rr(default)` - seperator between parent relation and relation (parent needs the foreign key)
    """
    pass

    # 1. Reading CSV from bytes (no disk I/O)

    # 2. Creating a temporary table in the database

    # 3. Bulk loading CSV data into temp table

    # 4. Mapping and inserting from temp table to final table

        # 4.1. Schemanyd Logic Stuff

    # 5. Cleaning up temporary table


# - - - - - Wrapper Functions - Convert various data types to CSV bytes - - - - -

def csv_bytes_from_dicts(data_dicts: list[dict[str, Any]]) -> bytes:
    """
    Convert a list of dictionaries to CSV bytes.

    Parameters
    ----------
    data_dicts: list[dict[str, Any]]
        Iterable of dictionaries that should be converted into CSV format.

    Returns
    -------
    bytes
        UTF-8 encoded CSV representation of the provided dictionaries.
    """
    df = pl.DataFrame(data_dicts)
    return df.write_csv().encode('utf-8')


def csv_bytes_from_polars(df: pl.DataFrame) -> bytes:
    """
    Convert a Polars DataFrame to CSV bytes.

    Parameters
    ----------
    df: pl.DataFrame
        DataFrame to serialize to CSV.

    Returns
    -------
    bytes
        UTF-8 encoded CSV representation of the DataFrame.
    """
    return df.write_csv().encode('utf-8')


def csv_bytes_from_pandas(df: 'pd.DataFrame') -> bytes:
    """
    Convert a Pandas DataFrame to CSV bytes.

    Parameters
    ----------
    df: pd.DataFrame
        DataFrame to serialize to CSV. Index is ignored.

    Returns
    -------
    bytes
        UTF-8 encoded CSV representation of the DataFrame.
    """
    return df.to_csv(index=False).encode('utf-8')


def csv_bytes_from_csv_file(file_path: str) -> bytes:
    """
    Read a CSV file from disk and return its bytes.

    Parameters
    ----------
    file_path: str
        Absolute or relative path to the CSV file.

    Returns
    -------
    bytes
        Raw file contents as bytes.
    """
    with open(file_path, 'rb') as f:
        return f.read()


def csv_bytes_from_excel_file(file_path: str, sheet_name: Union[str, int, None] = None) -> bytes:
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
    bytes
        UTF-8 encoded CSV representation of the selected sheet.
    """
    if sheet_name is None:
        df = pl.read_excel(file_path)
    else:
        df = pl.read_excel(file_path, sheet_name=sheet_name)

    return df.write_csv().encode('utf-8')

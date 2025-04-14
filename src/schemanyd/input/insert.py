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

    # 1. | Reading CSV from bytes (no disk I/O)

    # 2. | 1st Check Wave

        # 2.1. | Check if every mentioned column in the csv even exists (maybe check for similiar names / typos)

        # 2.2. | Check if every mentioned database field even exists in the schema
        
            # 2.2.1. | Check if the data types match (maybe also check for similiar names / typos)

        # 2.3. | Check if fields which are mentioned without any long syntax ('.../...') have multiple foreign keys pointing to them

            # 2.3.1. | Check which foreign key is closer / choose it and give a warning / return in how it was joined, which one was taken, throw an error if they are equally close

        # 2.4. | For every table, check if all fields which are notnull are given

            # 2.4.1. | If not, check if the existing are unique enough to get the IDs of existing entries

            # 2.4.2. | If it would be possible, check if all entries already exist, or if I would need to add new (then this can't be done, but a dataset with the found values can be returned)

        # 2.5. | Check with a Graph Path-Tracing, if the join is possible, provide detailed feedback which exact point might cause issues

    # 3. | Renaming and dropping columns based on mapping

    # 4. | Creating a temporary table in the database

    # 5. | Bulk loading CSV data into temp table

    # 6. | Schemanyd Logic

        # 6.1. | Check which tables don't require any foreign keys and can immediately be inserted

        # 6.2. | Insert those and join the keys to the temporary table, continue with 6.1 again (maybe add an option for inserting as long as it can, even in cases where a join is not fully possible)

    # n-2. | Check if the insert was successful (not sure which logic to use for this yet)

    # n-1. | Cleaning up temporary table

    # n. | Return how the procedure went


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

# Preinstalled
from typing import Dict, Any, Union
from io import BytesIO
from pathlib import Path

# Pip
import polars as pl
import pandas as pd

# Local
from schemanyd.utility.database import Database
from schemanyd.input.insert import (
    csv_from_dicts,
    csv_from_polars,
    csv_from_pandas,
    csv_from_csv_file,
    csv_from_excel_file
)

class Schemanyd:

    def __init__(self, database_obj: Database, seperator_rf = ".", seperator_rr = "/"):
        """
        database_obj - Schemanyd Database Object

        seperator_rf - seperator between relation and field
        seperator_rr - seperator between parent relation and relation (relationship)
        """

        # [POTENTIAL ADD] Think about if it is useful to support multiple database connections within a single Schemanyd object
        self.db = database_obj

        self.seperator_rf = seperator_rf
        self.seperator_rr = seperator_rr

    # - - - - - Core Insertion Function - CSV bytes → Temporary Table → into Final Tables - - - - -

    @staticmethod
    def to_BytesIO(data: Any) -> BytesIO:
        """
        Transform your data into a BytesIO stream for use with insert().
        
        Supported data types:
        - list[dict]: List of dictionaries (each dict is a row)
        - polars.DataFrame: Polars DataFrame
        - pandas.DataFrame: Pandas DataFrame  
        - str (file path): CSV file path or Excel file path (.xlsx/.xls)
        - BytesIO: Already a BytesIO object (returns as-is after seeking to start)
        
        Parameters
        ----------
        data : Any
            Data to convert to CSV BytesIO format
            
        Returns
        -------
        BytesIO
            In-memory binary file-like object containing CSV data, positioned at start
            
        Raises
        ------
        TypeError
            If data type is not supported
        ValueError
            If file path doesn't exist or has unsupported extension
        """
        
        # Already a BytesIO - just ensure it's at the start
        if isinstance(data, BytesIO):
            data.seek(0)
            return data
            
        # List of dictionaries
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            return csv_from_dicts(data)
            
        # Polars DataFrame
        elif hasattr(data, '__class__') and data.__class__.__name__ == 'DataFrame' and hasattr(data, 'write_csv'):
            return csv_from_polars(data)
            
        # Pandas DataFrame
        elif hasattr(data, '__class__') and data.__class__.__name__ == 'DataFrame' and hasattr(data, 'to_csv'):
            return csv_from_pandas(data)
            
        # File path (string)
        elif isinstance(data, str):
            file_path = Path(data)
            if not file_path.exists():
                raise ValueError(f"File not found: {data}")
                
            suffix = file_path.suffix.lower()
            if suffix == '.csv':
                return csv_from_csv_file(data)
            elif suffix in ['.xlsx', '.xls']:
                return csv_from_excel_file(data)
            else:
                raise ValueError(f"Unsupported file extension: {suffix}. Supported: .csv, .xlsx, .xls")
                
        else:
            raise TypeError(f"Unsupported data type: {type(data)}. "
                          f"Supported types: list[dict], polars.DataFrame, pandas.DataFrame, "
                          f"str (file path), BytesIO")

    def insert(self, csv_file: BytesIO, column_mapping: Dict[str, str], try_convert: bool = False) -> None:
        """
        Insert data from a CSV BytesIO into the database using Schemanyd Autotrace Logic.
        
        Parameters
        ------------------------------------------------------------------------------------------------------------------------
        csv_file: BytesIO
            In-memory binary file-like object containing CSV data. The stream should contain UTF-8 encoded CSV bytes.
        column_mapping: Dict[str, str]
            A mapping of CSV column names to database table column names.
        try_convert: bool
            Whether to attempt automatic type conversion for the CSV data.

        Example
        ------------------------------------------------------------------------------------------------------------------------
        #### `csv_file` (contents of the BytesIO)
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

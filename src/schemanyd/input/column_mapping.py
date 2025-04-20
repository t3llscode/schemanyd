from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from ..schemanyd import Schemanyd

class ColumnMapping:

    def __init__(self, schemanyd_obj: "Schemanyd", column_mapping: Dict[str, str]):
        self.schemanyd_obj = schemanyd_obj
        self.column_mapping = column_mapping


    def check(self):
        print("ColumnMapping.check() is not implemented yet, be aware.")
        pass

        # 2.2. | Check if every mentioned database field even exists in the schema

        # 2.2.1. | Check if the data types match (maybe also check for similiar names / typos)

        # 2.3. | Check if fields which are mentioned without any long syntax ('.../...') have multiple foreign keys pointing to them

        # 2.3.1. | Check which foreign key is closer / choose it and give a warning / return in how it was joined, which one was taken, throw an error if they are equally close

        # 2.4. | For every table, check if all fields which are notnull are given

        # 2.4.1. | If not, check if the existing are unique enough to get the IDs of existing entries

        # 2.4.2. | If it would be possible, check if all entries already exist, or if I would need to add new (then this can't be done, but a dataset with the found values can be returned)

        # 2.5. | Check with a Graph Path-Tracing, if the join is possible, provide detailed feedback which exact point might cause issues

from schemanyd.utility.database import Database

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

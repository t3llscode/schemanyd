from schemanyd.utility.database import Database

class Schemanyd:

    def __init__(self, database_url, seperator_rf = ".", seperator_rr = "/"):
        """
        database_url - URL with Credentials for Database Connection - Example: 'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}' - Passed to sqlalchemy

        seperator_rf - seperator between relation and field
        seperator_rr - seperator between parent relation and relation (relationship)
        """

        # [POTENTIAL ADD] Think about if it is useful to support multiple database connections within a single Schemanyd object
        self.database_url = database_url
        self.db = Database(database_url)

        self.seperator_rf = seperator_rf
        self.seperator_rr = seperator_rr

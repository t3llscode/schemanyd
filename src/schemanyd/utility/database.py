from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


# IMPROVEMENTS
# - Database URL Check / Error Handling

# POTENTIAL IMPROVEMENTS
# - Database URL Building Utility Function feeded by Docker secrets


class Database:

    def __init__(self, database_url):
        """
        Initialize the Database instance (synchronous portion).

        Usage
        -----
        Recommended (factory, handles async initialization for you):
        ```python
        database = await Database.create("postgresql+asyncpg://user:password@host:5432/db")
        ```

        Manual (create then initialize asynchronously):
        ```python
        database = Database("postgresql+asyncpg://user:password@host:5432/db")
        await database.async_init()
        ```

        Parameters
        -----
        database_url : str
            Full SQLAlchemy database URL.
            Example: "postgresql+asyncpg://user:password@host:5432/db"

        """

        # [ADD] Database URL Check / Error Handling
        self.database_url = database_url
        self.engine = create_async_engine(self.database_url)
        
        # Initialize these as None - they'll be set in async_init
        self.schema = None
        self.graph = None

        # Create async session maker
        self.create_async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )


    @classmethod
    async def create(cls, database_url):
        """
        Factory method to create and initialize Database instance asynchronously
        """
        instance = cls(database_url)
        await instance.async_init()
        return instance


    async def async_init(self):
        """
        Async initialization method - call this after creating the instance
        """
        # Load the database schema
        self.schema = await self.get_schema()
        self.graph = await self.build_graph()

    # - - - STATIC METHODS - - -

    @staticmethod
    def build_database_url(db_protocol, db_user, db_password, db_host, db_port, db_name):
        """
        Build a database URL from the given components.

        Parameters
        ----------
        db_protocol : str
            The database protocol (e.g. "postgresql+asyncpg").
        db_user : str
            The database user.
        db_password : str
            The password for the database user.
        db_host : str
            The host of the database.
        db_port : int
            The port of the database.
        db_name : str
            The name of the database.

        Returns
        -------
        str
            The constructed database URL.
        """

        return f"{db_protocol}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    # - - - INSTANCE METHODS - - -

    async def get_db(self):
        """
        async function to get async DB session
        """
        async with self.create_async_session() as session:
            try:
                yield session
            finally:
                await session.close()


    async def get_schema(self):
        """
        async function for loading schema
        """
        schema = MetaData()
        print(type(schema))
        async with self.engine.connect() as connection:
            await connection.run_sync(schema.reflect)
            return schema


    async def build_graph(self) -> dict:
        """
        async function to build a simple dependency graph
        """
        # Use self.schema if already loaded, otherwise get it fresh
        schema = self.schema if self.schema is not None else await self.get_schema()  # should be covered by init
        graph = {}

        for table in schema.tables.values():
            print(table, flush=True)
            graph[table] = [fk.column.table.name for fk in table.foreign_keys]

        return graph


    async def connection_established(self):
        """
        async function to check database connection
        """
        try:
            async with self.engine.connect() as connection:
                await connection.execute(text("SELECT 1"))
                return True
        except Exception:
            return False

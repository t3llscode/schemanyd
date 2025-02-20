from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

class Database:

    def __init__(self, database_url):
        """
        Initialize the database connection and object
        """

        # [POTENTIAL ADD] - - - Maybe add database_url building later - - -
        # DB_PROTOCOL = "postgresql+asyncpg"    # protocol + driver for URL
        # DB_USER = "user"                      # username
        # DB_PASSWORD = "db_password"           # password of the user
        # DB_HOST = "docker-db-1"               # IP address or container name
        # DB_PORT = "5432"                      # Postgres default port
        # DB_NAME = "db"                        # name of the database
        #
        # self.database_url = f"{DB_PROTOCOL}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

        # [ADD] Database URL Check / Error Handling
        self.database_url = database_url
        self.engine = create_async_engine(self.database_url)

        # Load the database schema
        self.schema = MetaData()

        # Create async session maker
        self.create_async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

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
        async with self.engine.connect() as connection:
            await connection.run_sync(self.schema.reflect)
            print(f"Available Tables: {list(self.schema.tables.keys())}", flush=True)
            return self.schema

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

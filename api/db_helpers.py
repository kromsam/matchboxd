"""Helper functions for the database."""

import logging
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

# Import the root logger
logger = logging.getLogger(__name__)


Base = declarative_base()


class DatabaseHandler():
    """Class for setting up and handling database."""

    def __init__(self, database):
        print("Creating DB engine...")
        self.engine = create_engine(database, echo=True)
        print("DB engine created.")
        # Connect to the database and print success message
        with self.engine.connect() as connection:
            print("Connection successful!")
            result = connection.execute(text("SELECT 1"))
            print("Query result:", result.fetchone())
        print("Creating declarative base...")
        Base.metadata.create_all(bind=self.engine)
        print("Declarative base created.")
        print("Creating session")
        self.session = sessionmaker(bind=self.engine)
        print("Session created.")

    def create_session(self):
        """Create new database session."""
        return self.session()

    def remove_database(self):
        """Completely remove all content from database."""
        # Create a metadata object
        metadata = MetaData()

        # Reflect the existing database schema
        metadata.reflect(bind=self.engine)

        # Drop all tables
        metadata.drop_all(bind=self.engine)

    def create_all(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)


def clear_tables(session, table_to_clear):
    """Empty specific table from database."""
    # Delete all rows from the table
    session.execute(table_to_clear.delete())

    # Commit the changes
    session.commit()

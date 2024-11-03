"""Helper functions for the database."""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker

from .global_constants import DATABASE


Base = declarative_base()


class DatabaseHandler:
    """Class for setting up and handling database."""

    def __init__(self):
        self.engine = create_engine(DATABASE, echo=True)
        Base.metadata.create_all(bind=self.engine)
        self.session = sessionmaker(bind=self.engine)

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


def clear_tables(session, table_to_clear):
    """Empty specific table from database."""
    # Delete all rows from the table
    session.execute(table_to_clear.delete())

    # Commit the changes
    session.commit()

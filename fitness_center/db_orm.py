"""Db init."""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

# DB_STRING = 'sqlite:///fc_db.sqlite'
DB_STRING_TEMPLATE = 'postgresql+psycopg2://{0}:{1}@{2}:5432'
DB_STRING = DB_STRING_TEMPLATE.format(os.environ.get('POSTGRES_USER'),
                                      os.environ.get('POSTGRES_PASSWORD'),
                                      os.environ.get('DB_HOST', 'localhost'))
Base = declarative_base()


class Db:
    """Db ORM class."""

    def __init__(self):
        """Init."""
        self.engine = create_engine(DB_STRING)
        self.session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self._init_db()

    def _init_db(self):
        """Initialize db orm metadata."""
        Base.query = self.session.query_property()
        Base.metadata.create_all(bind=self.engine)

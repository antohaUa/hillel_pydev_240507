"""Module provides common db operations."""
import sqlite3

SQLITE_DB_PATH = 'fc_db.sqlite'


class SqliteDb:
    """Sqlite3 db operations."""

    def __init__(self, db_path=SQLITE_DB_PATH):
        """Init."""
        con = sqlite3.connect(db_path)
        con.row_factory = self.dict_factory
        self.con = con
        self.cur = con.cursor()

    @staticmethod
    def dict_factory(cursor, row):
        """Convert rows into dict."""
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def exec_query(self, query, single=True, commit=False):
        """Execute DB query."""
        self.cur.execute(query)
        if commit:
            self.con.commit()
        return self.cur.fetchone() if single else self.cur.fetchall()

    def close(self):
        """Close db."""
        self.con.close()

    def __del__(self):
        """Teardown."""
        self.close()

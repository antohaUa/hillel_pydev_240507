"""Module provides common db operations."""
import sqlite3

SQLITE_DB_PATH = 'fc_db.sqlite'


def exec_db_query(**kwargs):
    """Execute certain DB query."""
    db = SqliteDb()
    if select_data := kwargs.get('select_data'):
        return db.select(select_data=select_data, join_data=kwargs.get('join_data'), single=kwargs.get('single', True),
                         where_data=kwargs.get('where_data'), join_type=kwargs.get('join_type', 'join'))
    elif insert_data := kwargs.get('insert_data'):
        db.insert(insert_data=insert_data)
    elif update_data := kwargs.get('update_data'):
        db.update(update_data=update_data, where_data=kwargs.get('where_data'))
    elif delete_data := kwargs.get('delete_data'):
        db.delete(delete_data=delete_data, where_data=kwargs.get('where_data'))


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
        try:
            self.cur.execute(query)
            if commit:
                self.con.commit()
            return self.cur.fetchone() if single else self.cur.fetchall()
        except Exception:
            return {} if single else []

    def select(self, select_data, join_data=None, where_data=None, single=True, join_type='join'):
        """Create and execute select query according provided select, join and where dicts."""
        fields_str = ', '.join([f'{itm} as "{itm}"' for itm in list(select_data.values())[0]])
        select_str = f'select {fields_str} from {list(select_data.keys())[0]}'
        if join_data is not None:
            join_str = ' '.join([f'{join_type} {k} on {v}' for k, v in join_data.items()])
            select_str += f' {join_str}'
        if where_data is not None:
            select_str += f""" where {' and '.join([f'{key}="{val}"' for key, val in where_data.items()])}"""
        return self.exec_query(query=select_str, single=single)

    def insert(self, insert_data):
        """Create and execute insert query according provided insert data."""
        insert_fields = ', '.join(list(insert_data.values())[0].keys())
        values_str = ', '.join([f'"{itm}"' for itm in list(insert_data.values())[0].values()])
        insert_str = f'insert into {list(insert_data.keys())[0]} ({insert_fields}) values ({values_str})'
        return self.exec_query(query=insert_str, commit=True)

    def update(self, update_data, where_data=None):
        """Create and execute update query according provided update data."""
        update_str = f'update {list(update_data.keys())[0]} set '
        set_pairs = ', '.join([f'{column}="{value}"' for column, value in list(update_data.values())[0].items()])
        update_str += set_pairs
        if where_data is not None:
            update_str += f""" where {' and '.join([f'{key}="{val}"' for key, val in where_data.items()])}"""
        return self.exec_query(query=update_str, commit=True)

    def delete(self, delete_data, where_data=None):
        """Create and execute delete query according provided delete data."""
        delete_str = f'delete from {delete_data}'
        if where_data is not None:
            delete_str += f""" where {' and '.join([f'{key}="{val}"' for key, val in where_data.items()])}"""
        return self.exec_query(query=delete_str, commit=True)

    def close(self):
        """Close db."""
        self.con.close()

    def __del__(self):
        """Teardown."""
        self.close()

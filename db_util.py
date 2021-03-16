import sqlite3
from contextlib import contextmanager


def _open_connection():
    with sqlite3.connect('volvo.db') as conn:
        cursor = conn.cursor()

        yield cursor

        cursor.commit()


def create_table():
    with _open_connection() as conn:
        conn.execute('''CREATE TABLE stocks (date text, trans text, symbol text, qty real, price real)''')


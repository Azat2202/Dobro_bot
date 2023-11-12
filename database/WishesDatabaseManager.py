import sqlite3

from database.DatabaseManager import DatabaseManager


class WishesDatabaseManager(DatabaseManager):
    __db_name = '../resources/pid.db'

    def __init__(self):
        super().__init__(self.__db_name)

    def get_truth(self) -> str:
        return self.cursor.execute("SELECT value FROM truth ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

    def get_dare(self) -> str:
        return self.cursor.execute("SELECT value FROM dare ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

    def get_wish(self) -> str:
        return self.cursor.execute("SELECT value FROM wish ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

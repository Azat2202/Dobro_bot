import sqlite3


class WishesDatabaseManager:
    __db_name = '../resources/pid.db'

    def __init__(self):
        import os.path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, self.__db_name)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return

    def get_truth(self) -> str:
        return self.cursor.execute("SELECT value FROM truth ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

    def get_dare(self) -> str:
        return self.cursor.execute("SELECT value FROM dare ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

    def get_wish(self) -> str:
        return self.cursor.execute("SELECT value FROM wish ORDER BY RANDOM() LIMIT 1;").fetchone()[0]

    def close(self):
        self.connection.commit()
        self.connection.close()

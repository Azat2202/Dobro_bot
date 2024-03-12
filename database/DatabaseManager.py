import sqlite3


class DatabaseManager:

    def __init__(self, db_name):
        import os.path

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return

    def close(self):
        self.connection.commit()
        self.connection.close()

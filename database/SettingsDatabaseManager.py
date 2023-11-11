import sqlite3


class SettingsDatabaseManager:
    __db_name = '../resources/chat_settings.db'

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

    def add_chat(self, chat_id):
        self.cursor.execute("""
        INSERT OR IGNORE INTO chats(chat_id, send_poll) VALUES (?, 0)""", (chat_id, ))
        self.connection.commit()

    def get_poll_parameter(self, chat_id: int) -> bool:
        return self.cursor.execute("""
        SELECT send_poll FROM chats WHERE chat_id = ?""", (chat_id, )).fetchone()[0] == 1

    def change_poll_parameter(self, chat_id) -> bool:
        self.cursor.execute("""
        UPDATE chats 
        SET send_poll=?
        WHERE chat_id = ?""", (0 if self.get_poll_parameter(chat_id) else 1, chat_id))
        self.connection.commit()
        return self.get_poll_parameter(chat_id)

    def get_mailing_chats(self) -> list:
        return self.cursor.execute("""
        SELECT chat_id FROM chats WHERE send_poll = 1""").fetchall()

    def close(self):
        self.connection.commit()
        self.connection.close()

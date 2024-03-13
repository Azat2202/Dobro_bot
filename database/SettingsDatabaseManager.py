import sqlite3

from database.DatabaseManager import DatabaseManager


class SettingsDatabaseManager(DatabaseManager):
    __db_name = "../resources/chat_settings.db"

    def __init__(self):
        super().__init__(self.__db_name)

    def add_chat(self, chat_id):
        self.cursor.execute(
            """
        INSERT OR IGNORE INTO chats(chat_id, send_poll) VALUES (?, 0)""",
            (chat_id,),
        )
        self.connection.commit()

    def get_poll_parameter(self, chat_id: int) -> bool:
        result = self.cursor.execute(
            """
        SELECT send_poll FROM chats WHERE chat_id = ?""",
            (chat_id,),
        ).fetchone()
        if result:
            return result[0] == 1
        else:
            self.add_chat(chat_id)
            return (
                self.cursor.execute(
                    """
        SELECT send_poll FROM chats WHERE chat_id = ?""",
                    (chat_id,),
                ).fetchone()[0]
                == 1
            )

    def change_poll_parameter(self, chat_id) -> bool:
        self.cursor.execute(
            """
        UPDATE chats 
        SET send_poll=?
        WHERE chat_id = ?""",
            (0 if self.get_poll_parameter(chat_id) else 1, chat_id),
        )
        self.connection.commit()
        return self.get_poll_parameter(chat_id)

    def get_updatelog_parameter(self, chat_id: int) -> bool:
        result = self.cursor.execute(
            """
        SELECT send_updatelog FROM chats WHERE chat_id = ?""",
            (chat_id,),
        ).fetchone()
        if result:
            return result[0] == 1
        else:
            self.add_chat(chat_id)
            return (
                self.cursor.execute(
                    "SELECT send_updatelog FROM chats WHERE chat_id = ?",
                    (chat_id,),
                ).fetchone()[0]
                == 1
            )

    def change_updatelog_parameter(self, chat_id) -> bool:
        self.cursor.execute(
            """
        UPDATE chats 
        SET send_updatelog=?
        WHERE chat_id = ?""",
            (0 if self.get_updatelog_parameter(chat_id) else 1, chat_id),
        )
        self.connection.commit()
        return self.get_updatelog_parameter(chat_id)

    def get_chats_with_polls(self) -> list:
        return self.cursor.execute(
            """
        SELECT chat_id FROM chats WHERE send_poll = 1"""
        ).fetchall()

    def get_chats_with_updatelogs(self) -> list:
        return self.cursor.execute(
            """
        SELECT chat_id FROM chats WHERE send_updatelog = 1"""
        ).fetchall()

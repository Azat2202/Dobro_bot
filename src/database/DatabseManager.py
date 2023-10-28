import sqlite3
from datetime import datetime

from aiogram.utils import emoji

from src.database.exceptions import *


class DatabaseManager:
    __db_name = '../resources/wedding_users.db'

    def __init__(self):
        import os.path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, self.__db_name)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return

    def is_married(self, user1, user2):
        is_first_married = self.cursor.execute('SELECT 1 '
                                               'FROM marriages '
                                               'WHERE (user1 = (?) OR user2 = (?)) '
                                               'AND betrothed = 1',
                                               (user1, user1)).fetchone()
        is_second_married = self.cursor.execute('SELECT 1 '
                                                'FROM marriages '
                                                'WHERE user1 = (?) OR user2 = (?) AND betrothed = 1',
                                                (user2, user2)).fetchone()
        return is_first_married or is_second_married

    def inc_message(self, user_id, chat_id, first_name, last_name):
        self.__add_new_user(user_id, first_name, last_name)
        self.cursor.execute("UPDATE messages "
                            "SET message_count = message_count + 1 "
                            "WHERE user_id = (?) AND chat_id = (?)",
                                (user_id, chat_id))
        self.connection.commit()

    def inc_karma(self, user_id, chat_id):
        self.cursor.execute("UPDATE messages "
                            "SET karma = karma + 1 "
                            "WHERE user_id = (?) AND chat_id = (?)",
                            (user_id, chat_id))
        self.connection.commit()

    def dec_karma(self, user_id, chat_id):
        self.cursor.execute("UPDATE messages "
                            "SET karma = karma - 1 "
                            "WHERE user_id = (?) AND chat_id = (?)",
                            (user_id, chat_id))
        self.connection.commit()

    def get_messages(self, chat_id):
        return self.cursor.execute("SELECT users.name, users.surname, messages.message_count"
                                   "FROM messages"
                                   "JOIN users"
                                   "ON messages.user_id = users.id"
                                   "WHERE chat_id = (?)"
                                   "ORDER BY message_count DESC;"
                                   , (chat_id,)).fetchall()

    def karma_repr(self, chat_id):
        return self.cursor.execute("SELECT users.name, users.surname, messages.karma"
                                   "FROM messages"
                                   "JOIN users"
                                   "ON messages.user_id = users.id"
                                   "WHERE chat_id = (?)"
                                   "ORDER BY karma DESC;"
                                   , (chat_id,)).fetchall()


    def registrate_new_marriage(self, user1_id, user1_name, user1_surname, user2_id, user2_name, user2_surname, chat_id, message_id):
        # Delete previous proposals
        self.cursor.execute("DELETE FROM marriages "
                            "WHERE (user1 = (?) OR user2 = (?)) AND chat_id = (?) AND betrothed = 0",
                            (user1_id, user2_id))
        self.cursor.execute(f""
        f"INSERT INTO marriages (user1, user2, date, chat_id, message_id, betrothed, agreed)"
        f"VALUES (?, ?, ?, ?, ?, 0, 0)",
                            (user1_id,
                             user2_id,
                             datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                             chat_id,
                             message_id))
        self.__add_new_user(user1_id, user1_name, user1_surname)
        self.__add_new_user(user2_id, user2_name, user2_surname)
        self.connection.commit()

    def marriage_agree(self, user_id, chat_id, message_id):
        data = self.cursor.execute("SELECT * "
                                   "FROM marriages "
                                   "WHERE chat_id = (?) and message_id = (?)",
                                   (chat_id, message_id)).fetchone()
        marriage_time = datetime.strptime(data[2], "%y-%m-%d %H:%M:%S")
        time_delta = datetime.now() - marriage_time

        if user_id != data[1]:
            raise WrongUserException
        if time_delta.seconds > 600:
            raise TimeLimitException

        self.cursor.execute("UPDATE marriages "
                            "SET betrothed = 1"
                            "WHERE chat_id = (?) "
                            "AND message_id = (?) "
                            "AND witness_1 IS NOT NULL "
                            "AND witness_2 IS NOT NULL",
                            (chat_id, message_id))
        self.cursor.execute("UPDATE marriages "
                            "SET agreed = 1"
                            "WHERE chat_id = (?) AND message_id = (?)",
                            (chat_id, message_id))
        self.connection.commit()
        # marriage status, user1, user2, first witness, second witness
        return data[3] and data[4] and data[8] == 1, data[0], data[1], data[3], data[4]

    def marriage_disagree(self, user_id, chat_id, message_id):
        data = self.cursor.execute("SELECT * "
                                   "FROM marriages "
                                   "WHERE chat_id = (?) AND message_id = (?)",
                                   (chat_id, message_id)).fetchone()
        if user_id != data[1]:
            raise WrongUserException
        self.cursor.execute("DELETE FROM marriages "
                            "WHERE chat_id = (?) AND message_id = (?)",
                            (chat_id, message_id))
        self.connection.commit()
        return data[0], self.__get_name(data[0]), data[1], self.__get_name(data[1])

    def marriage_witness(self, user_id, chat_id, message_id):
        data = self.cursor.execute("SELECT * FROM marriages "
                                   "WHERE chat_id = (?) and message_id = (?)",
                                   (chat_id, message_id)).fetchone()
        marriage_time = datetime.strptime(data[2], "%y-%m-%d %H:%M:%S")
        time_delta = datetime.now() - marriage_time
        if user_id in (data[0], data[1], data[3], data[4]):
            raise WrongUserException
        if time_delta.seconds > 600:
            raise TimeLimitException

        if not data[3]:
            self.cursor.execute(f"UPDATE marriages SET witness1 = (?) WHERE chat_id = (?) and message_id = (?)",
                                (user_id, chat_id, message_id))
            self.connection.commit()
            return data[8], False, data[0], self.__get_name(data[0]), data[1], self.__get_name(data[1])
        elif not data[4]:
            self.cursor.execute(f"UPDATE marriages SET witness2 = (?) WHERE chat_id = (?) and "
                                f"message_id = (?)",
                                (user_id, chat_id, message_id))
            self.connection.commit()
            if data[8]:
                self.cursor.execute(f"UPDATE marriages SET betrothed = 1 WHERE chat_id = (?) and "
                                    f"message_id = (?)",
                                    (chat_id, message_id))
            return data[8], True, data[0], self.__get_name(data[0]), data[1], self.__get_name(data[1])

    def marriages_repr(self, chat_id):
        return self.cursor.execute("""
        SELECT user_1.id, user_1.name, user_1.surname, user_2.id, user_2.name, user_2.surname, marriages.date
        FROM marriages
        JOIN users AS user_1
              ON marriages.user1 = user_1.id
        JOIN users AS user_2
              ON marriages.user2 = user_2.id
        WHERE betrothed = 1
          AND chat_id = (?)
        ORDER BY date;""", (chat_id, )).fetchall()


    def request_divorce(self, user_id, chat_id):
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and (user1 = (?) or user2 = (?))",
                                   (chat_id, user_id, user_id)).fetchone()
        if not data:
            raise WrongUserException

    def del_marriage(self, call, chat_id, user_id):
        self.cursor.execute("DELETE FROM marriages WHERE chat_id = (?) AND (user1 = (?) OR user2 = (?))",
                            (chat_id, user_id, user_id))

    def __get_name(self, user_id):
        data = self.cursor.execute("SELECT * FROM users WHERE id = (?)", (user_id,)).fetchone()
        if data:
            return f"{data[1]}{' ' + data[2] if data[2] else ''}"
        else:
            return ''

    def __add_new_user(self, user_id, name, surname):
        self.cursor.execute(f"INSERT OR IGNORE INTO users VALUES (?, ?, ?)", (user_id, name, surname))
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()

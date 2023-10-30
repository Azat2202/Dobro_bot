import sqlite3
from datetime import datetime

from database.exceptions import *


class DatabaseManager:
    __db_name = '../resources/wedding_users.db'

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

    def is_married(self, user1: int, user2: int, chat_id: int):
        is_first_married = self.cursor.execute('SELECT 1 '
                                               'FROM marriages '
                                               'WHERE (user1 = (?) OR user2 = (?)) '
                                               'AND betrothed = 1 AND chat_id = (?)',
                                               (user1, user1, chat_id)).fetchone()
        is_second_married = self.cursor.execute('SELECT 1 '
                                                'FROM marriages '
                                                'WHERE (user1 = (?) OR user2 = (?)) '
                                                'AND betrothed = 1 AND chat_id = (?)',
                                                (user2, user2, chat_id)).fetchone()
        return is_first_married or is_second_married

    def inc_message(self, user_id: int, chat_id: int, first_name: str, last_name: str):
        self.__add_new_user(chat_id, user_id, first_name, last_name)
        self.cursor.execute("UPDATE messages "
                            "SET message_count = message_count + 1 "
                            "WHERE user_id = (?) AND chat_id = (?)", (user_id, chat_id))
        self.__add_new_user(chat_id, user_id, first_name, last_name)
        self.connection.commit()

    def inc_karma(self, user_id: int, chat_id: int):
        self.cursor.execute("UPDATE messages "
                            "SET karma = karma + 1 "
                            "WHERE user_id = (?) AND chat_id = (?)",
                            (user_id, chat_id))
        self.connection.commit()

    def dec_karma(self, user_id: int, chat_id: int):
        self.cursor.execute("UPDATE messages "
                            "SET karma = karma - 1 "
                            "WHERE user_id = (?) AND chat_id = (?)",
                            (user_id, chat_id))
        self.connection.commit()

    def get_messages(self, chat_id: int):
        return self.cursor.execute("SELECT users.name, users.surname, messages.message_count "
                                   "FROM messages "
                                   "JOIN users "
                                   "ON messages.user_id = users.id AND messages.chat_id = users.chat_id "
                                   "WHERE messages.chat_id = (?) "
                                   "ORDER BY message_count DESC; ",
                                   (chat_id,)).fetchall()

    def get_users(self, chat_id):
        return self.cursor.execute("""
        SELECT id, name, surname FROM users WHERE chat_id = (?)""", (chat_id,)).fetchall()

    def karma_repr(self, chat_id: int):
        return self.cursor.execute("SELECT users.name, users.surname, messages.karma "
                                   "FROM messages "
                                   "JOIN users "
                                   "ON messages.user_id = users.id AND messages.chat_id = users.chat_id "
                                   "WHERE messages.chat_id = (?) "
                                   "ORDER BY karma DESC; ",
                                   (chat_id,)).fetchall()

    def registrate_new_marriage(self, user1_id: int, user1_name: str, user1_surname: str, user2_id: int,
                                user2_name: str, user2_surname: str, chat_id: int, message_id: int):
        # Delete previous proposals
        self.cursor.execute("DELETE FROM marriages "
                            "WHERE (user1 = (?) OR user2 = (?)) AND chat_id = (?) AND betrothed = 0",
                            (user1_id, user2_id, chat_id))
        self.cursor.execute(f"INSERT INTO marriages (user1, user2, date, chat_id, message_id, betrothed, agreed) \
        VALUES (?, ?, ?, ?, ?, 0, 0)",
                            (user1_id,
                             user2_id,
                             datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                             chat_id,
                             message_id))
        self.__add_new_user(chat_id, user1_id, user1_name, user1_surname)
        self.__add_new_user(chat_id, user2_id, user2_name, user2_surname)
        self.connection.commit()

    def marriage_agree(self, user_id: int, chat_id: int, message_id: int):
        data = self.cursor.execute("SELECT * "
                                         "FROM marriages "
                                         "WHERE chat_id = (?) and message_id = (?)",
                                         (chat_id,
                                          message_id)).fetchone()
        user1, user2, date, witness1, witness2, chat_id, message_id, betrothed, agreed = data
        marriage_time = datetime.strptime(date, "%y-%m-%d %H:%M:%S")
        time_delta = datetime.now() - marriage_time

        if user_id != user2:
            raise WrongUserException
        if time_delta.seconds > 600:
            raise TimeLimitException

        self.cursor.execute("UPDATE marriages "
                            "SET betrothed = 1 "
                            "WHERE chat_id = (?) "
                            "AND message_id = (?) "
                            "AND witness1 IS NOT NULL "
                            "AND witness2 IS NOT NULL",
                            (chat_id, message_id))
        self.cursor.execute("UPDATE marriages "
                            "SET agreed = 1 "
                            "WHERE chat_id = (?) AND message_id = (?)",
                            (chat_id, message_id))
        self.connection.commit()
        # marriage status, user1, user2, first witness, second witness
        return witness1 and witness2, user1, user2, witness1, witness2, self.__get_name(user1), self.__get_name(user2)

    def marriage_disagree(self, user_id: int, chat_id: int, message_id: int):
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

    def marriage_witness(self, user_id: int, chat_id: int, message_id: int):
        data = self.cursor.execute("SELECT * FROM marriages "
                                   "WHERE chat_id = (?) and message_id = (?)",
                                   (chat_id, message_id)).fetchone()
        user1, user2, date, witness1, witness2, chat, msg, betrothed, agreed = data
        marriage_time = datetime.strptime(date, "%y-%m-%d %H:%M:%S")
        time_delta = datetime.now() - marriage_time
        if user_id in (user1, user2, witness1, witness2):
            raise WrongUserException
        if time_delta.seconds > 600:
            raise TimeLimitException
        if not witness1:
            self.cursor.execute(f"UPDATE marriages SET witness1 = (?) WHERE chat_id = (?) and message_id = (?)",
                                (user_id, chat_id, message_id))
            self.connection.commit()
            return (agreed and bool(witness1)), agreed, bool(witness1), user1, self.__get_name(user1), user2, self.__get_name(user2)
        elif not witness2:
            self.cursor.execute(f"UPDATE marriages SET witness2 = (?) WHERE chat_id = (?) and "
                                f"message_id = (?)",
                                (user_id, chat_id, message_id))
            self.connection.commit()
            if agreed:
                self.cursor.execute(f"UPDATE marriages SET betrothed = 1 WHERE chat_id = (?) and "
                                    f"message_id = (?)",
                                    (chat_id, message_id))
                self.connection.commit()
            return (agreed and bool(witness1)), agreed, bool(witness1), user1, self.__get_name(user1), user2, self.__get_name(user2)

    def marriages_repr(self, chat_id: int):
        return self.cursor.execute("""
        SELECT user_1.id, user_1.name, user_2.id, user_2.name, witness_1.name, witness_2.name, marriages.date
        FROM marriages
        JOIN users AS user_1
              ON marriages.user1 = user_1.id AND marriages.chat_id = user_1.chat_id
        JOIN users AS user_2
              ON marriages.user2 = user_2.id AND marriages.chat_id = user_2.chat_id
        JOIN users AS witness_1
              ON marriages.witness1 = witness_1.id AND marriages.chat_id = witness_1.chat_id
        JOIN users AS witness_2
              ON marriages.witness2 = witness_2.id AND marriages.chat_id = witness_2.chat_id
        WHERE betrothed = 1
          AND marriages.chat_id = (?)
        ORDER BY date;""", (chat_id,)).fetchall()

    def request_divorce(self, user_id: int, chat_id: int):
        data = self.cursor.execute("SELECT * FROM marriages "
                                   "WHERE chat_id = (?) and (user1 = (?) or user2 = (?))"
                                   "and betrothed = 1",
                                   (chat_id, user_id, user_id)).fetchone()
        if not data:
            raise WrongUserException

    def del_marriage(self, chat_id: int, user_id: int):
        self.cursor.execute("DELETE FROM marriages WHERE chat_id = (?) AND (user1 = (?) OR user2 = (?))",
                            (chat_id, user_id, user_id))
        self.connection.commit()

    def __get_name(self, user_id: int):
        data = self.cursor.execute("SELECT * FROM users WHERE id = (?)", (user_id,)).fetchone()
        if data:
            return f"{data[1]}{' ' + data[2] if data[2] else ''}"
        else:
            return ''

    def __add_new_user(self, chat_id: int, user_id: int, name: str, surname: str):
        name = name.replace("[", "{").replace("]", "}")
        self.cursor.execute(f"INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (user_id, name, surname, chat_id))
        self.connection.commit()

    def close(self):
        self.connection.commit()
        self.connection.close()

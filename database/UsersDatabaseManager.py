import sqlite3
from datetime import datetime

from aiogram.utils.markdown import quote_html

from database.DatabaseManager import DatabaseManager
from database.exceptions import *


class UsersDatabaseManager(DatabaseManager):
    __db_name = '../resources/wedding_users.db'

    def __init__(self):
        super().__init__(self.__db_name)

    def get_last_poll(self, chat_id: int):
        return self.cursor.execute("""
        SELECT message_id
        FROM created_polls
        WHERE chat_id= ? 
        ORDER BY CAST(SUBSTR(date, 7, 2) AS INTEGER) DESC, CAST(SUBSTR(date, 4, 2) AS INTEGER) DESC , CAST(SUBSTR(date, 1, 2) AS INTEGER) DESC;""",
                                   (chat_id, )).fetchone()

    def add_poll(self, chat_id: int, poll_id: int, date: str, message_id: int):
        self.cursor.execute("""
        INSERT INTO created_polls(chat_id, poll_id, "date", "message_id")
        VALUES (?, ?, ?, ?)""", (chat_id, poll_id, date, message_id))

    def add_poll_answer(self, user_id: int, poll_id: int, option_id: int):
        self.cursor.execute("""
        INSERT INTO poll_answers(user_id, poll_id, option_id)
        VALUES  (?, ?, ?)""", (user_id, poll_id, option_id))
        self.connection.commit()

    def remove_poll_anser(self, user_id: int, poll_id: int):
        self.cursor.execute("""
        DELETE FROM poll_answers
        WHERE user_id = ? AND poll_id = ?""", (user_id, poll_id))
        self.connection.commit()


    def get_user_mood(self, user_id: int, chat_id: int):
        return self.cursor.execute("""
        SELECT user_mood.date, user_mood.mood, avg_mood.mood
        FROM (
            SELECT date, (3 - option_id) as "mood"
            FROM poll_answers
                   JOIN created_polls
                        ON poll_answers.poll_id = created_polls.poll_id
            WHERE chat_id = :chat_id
            AND user_id = :user_id
        ) AS user_mood
        JOIN (
            SELECT date, (3 - AVG(option_id)) as "mood"
            FROM poll_answers
            JOIN created_polls
                ON poll_answers.poll_id = created_polls.poll_id
            WHERE chat_id = :chat_id
            GROUP BY date
        ) AS avg_mood
        ON user_mood.date = avg_mood.date
        ORDER BY CAST(SUBSTR(user_mood.date, 7, 2) AS INTEGER) DESC , CAST(SUBSTR(user_mood.date, 4, 2) AS INTEGER) DESC , CAST(SUBSTR(user_mood.date, 1, 2) AS INTEGER) DESC ;""",
                                   {'user_id': user_id, 'chat_id': chat_id}).fetchmany(31)[::-1]

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

    def get_partner(self, user_id: int, chat_id: int):
        data = self.cursor.execute("""
                            SELECT user1, user2
                            FROM marriages
                            WHERE (marriages.user1=? or marriages.user2=?) and chat_id = ?
                            AND betrothed = 1;""",
                                   (user_id, user_id, chat_id)).fetchone()
        if not data:
            return None
        if data[0] == user_id:
            return data[1]
        return data[0]

    def is_adopted(self, child: int, chat_id: int):
        return self.cursor.execute('SELECT 1 '
                                   'FROM children '
                                   'WHERE child = (?) AND chat_id = (?)',
                                   (child, chat_id)).fetchone()

    def is_ancestor(self, parent: int, child: int, chat_id: int):
        data = self.cursor.execute("""
                        WITH RECURSIVE parent_of_parent AS (
                        SELECT children.parent, m_l.user2, m_r.user1
                        FROM children
                        LEFT JOIN marriages as m_l
                        ON children.parent = m_l.user1 AND m_l.chat_id = :chat_id
                        LEFT JOIN marriages as m_r
                        ON children.parent = m_r.user2 AND m_r.chat_id = :chat_id
                        WHERE children.child = :user_id AND children.chat_id = :chat_id
                        
                        UNION SELECT children.parent, m_l.user2, m_r.user1
                        FROM children
                        LEFT JOIN marriages as m_l
                        ON children.parent = m_l.user1 AND m_l.chat_id = :chat_id
                        LEFT JOIN marriages as m_r
                        ON children.parent = m_r.user2 AND m_r.chat_id = :chat_id
                        JOIN parent_of_parent ON (children.child = parent_of_parent.parent
                                            OR children.child = parent_of_parent.user1
                                            OR children.child = parent_of_parent.user2)
                                            AND children.chat_id = :chat_id
                        )
                        SELECT *
                        FROM parent_of_parent;
                """, {'user_id': parent, 'chat_id': chat_id}).fetchall()
        return any(child in line for line in data)

    def is_parent(self, parent_id: int, child_id: int, chat_id: int):
        return self.cursor.execute("""
        SELECT 1
        FROM children
        LEFT JOIN marriages as m_l
        ON (children.parent = m_l.user1 OR children.parent = m_l.user2)
        AND m_l.chat_id = :chat_id
        WHERE children.child = :child_id 
        AND children.chat_id = :chat_id
        AND (m_l.user2 = :parent_id OR m_l.user1 = :parent_id)""",
                                   {'parent_id': parent_id, 'child_id': child_id, 'chat_id': chat_id}).fetchone()

    def get_parent(self, child_id: int, chat_id: int):
        data =  self.cursor.execute("""
        SELECT parent
        FROM children
        WHERE child = ? AND chat_id = ?""", (child_id, chat_id)).fetchone()
        if not data:
            return None
        return data[0]

    def add_child(self, parent: int, child: int, chat_id: int):
        self.cursor.execute("INSERT INTO children (parent, child, chat_id) "
                            "VALUES (?, ?, ?)", (parent, child, chat_id))
        self.connection.commit()

    def remove_child(self, parent_id: int, child_id: int, chat_id: int):
        self.cursor.execute("""
        DELETE 
        FROM children
        WHERE parent = ? AND child = ? and chat_id = ?""", (parent_id, child_id, chat_id))
        self.connection.commit()

    def move_child(self, parent_id: int, new_parent_id: int, chat_id: int):
        self.cursor.execute("""
        UPDATE children
        SET parent=?
        WHERE parent=? AND chat_id=?""", (new_parent_id, parent_id, chat_id))
        self.connection.commit()

    def get_children(self, parent_id: int, chat_id: int):
        return self.cursor.execute("""
        SELECT child
        FROM children
        WHERE parent = ? AND chat_id = ?""", (parent_id, chat_id)).fetchall()

    def get_edges(self, chat_id: int):
        return self.cursor.execute("""
                            SELECT parent.id, parent.name, child.id, child.name
                            FROM children
                            JOIN users AS parent
                            ON children.chat_id = parent.chat_id AND children.parent = parent.id
                            JOIN users AS child
                                ON children.chat_id = child.chat_id AND children.child = child.id
                            WHERE children.chat_id = :chat_id;""",
                                   {'chat_id': chat_id}).fetchall()

    def inc_message(self, user_id: int, chat_id: int, first_name: str, last_name: str):
        self.add_new_user(chat_id, user_id, first_name, last_name)
        count = self.cursor.execute("UPDATE messages "
                                    "SET message_count = message_count + 1 "
                                    "WHERE user_id = (?) AND chat_id = (?) "
                                    "RETURNING message_count ", (user_id, chat_id)).fetchone()[0]
        self.add_new_user(chat_id, user_id, first_name, last_name)
        self.connection.commit()
        return count

    def inc_karma(self, user_id: int, chat_id: int):
        karma = self.cursor.execute("UPDATE messages "
                                    "SET karma = karma + 1 "
                                    "WHERE user_id = (?) AND chat_id = (?) "
                                    "RETURNING karma;",
                                    (user_id, chat_id)).fetchone()[0]
        self.connection.commit()
        return karma

    def dec_karma(self, user_id: int, chat_id: int):
        karma = self.cursor.execute("UPDATE messages "
                                    "SET karma = karma - 1 "
                                    "WHERE user_id = (?) AND chat_id = (?) "
                                    "RETURNING karma",
                                    (user_id, chat_id)).fetchone()[0]
        self.connection.commit()
        return karma

    def add_sex(self, user1: int, user2: int, chat_id: int):
        self.cursor.execute("INSERT INTO sex (chat_id, user1, user2)"
                            "VALUES (?, ?, ?);",
                            (chat_id, user1, user2))
        self.connection.commit()

    def sex_count(self, chat_id: int, user1: int):
        every = self.cursor.execute("SELECT COUNT(*) "
                                    "FROM sex "
                                    "WHERE (user1 = ? OR user2 = ?) AND chat_id = ?;",
                                    (user1, user1, chat_id)).fetchone()[0]
        return every

    def get_sex_history(self, chat_id: int, user1: int):
        return self.cursor.execute("""
                            SELECT partner.id, partner.name, COUNT(user2)
                            FROM (
                                SELECT id,user1, user2, chat_id
                                FROM sex
                                WHERE user1 = ? AND chat_id = ?
                                UNION SELECT id, user2, user1, chat_id
                                FROM sex
                                WHERE user2 = ? AND chat_id = ?
                            ) as t
                            JOIN users as partner
                            ON user2=partner.id AND t.chat_id = partner.chat_id
                            GROUP BY user2;""",
                                   (user1, chat_id, user1, chat_id)).fetchall()

    def get_top_spammers(self, chat_id: int, limit_by:int):
        return self.cursor.execute("SELECT users.name, users.surname, messages.message_count "
                                   "FROM messages "
                                   "JOIN users "
                                   "ON messages.user_id = users.id AND messages.chat_id = users.chat_id "
                                   "WHERE messages.chat_id = (?) "
                                   "ORDER BY message_count DESC "
                                   "LIMIT (?); ",
                                   (chat_id, limit_by)).fetchall()

    def get_users(self, chat_id):
        return self.cursor.execute("""
        SELECT id, name, surname FROM users WHERE chat_id = (?)""", (chat_id,)).fetchall()

    def get_user(self, chat_id, user_id):
        return self.cursor.execute("""
               SELECT name, surname, message_count, karma
               FROM users
               JOIN messages 
               ON users.id = messages.user_id AND users.chat_id=messages.chat_id 
               WHERE users.chat_id = (?) AND users.id=(?)""",
                                   (chat_id, user_id)).fetchone()

    def update_user(self, chat_id: int, user_id: int, first_name: str, last_name:str):
        return self.cursor.execute("""
        UPDATE users
        SET name = (?), surname = (?)
        WHERE id = (?) AND chat_id = (?)""",
                                   (first_name, last_name, user_id, chat_id)).execute()

    def top_karma(self, chat_id: int, limit_by: int):
        return self.cursor.execute("SELECT users.name, users.surname, messages.karma "
                                   "FROM messages "
                                   "JOIN users "
                                   "ON messages.user_id = users.id AND messages.chat_id = users.chat_id "
                                   "WHERE messages.chat_id = (?) "
                                   "ORDER BY karma DESC "
                                   "LIMIT (?); ",
                                   (chat_id, limit_by)).fetchall()

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
        self.add_new_user(chat_id, user1_id, user1_name, user1_surname)
        self.add_new_user(chat_id, user2_id, user2_name, user2_surname)
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
            return (agreed and bool(witness1)), agreed, bool(witness1), user1, self.__get_name(
                user1), user2, self.__get_name(user2)
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
            return (agreed and bool(witness1)), agreed, bool(witness1), user1, self.__get_name(
                user1), user2, self.__get_name(user2)

    def get_my_marriage(self, user_id: int, chat_id: int):
        return self.cursor.execute("""
        SELECT user_1.id, user_1.name, user_2.id, user_2.name, witness_1.name, witness_2.name, marriages.date, marriages.message_id
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
          AND (marriages.user1 = ? OR marriages.user2 = ?)
        ORDER BY date;""", (chat_id, user_id, user_id)).fetchone()

    def get_marriages(self, chat_id: int):
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
        return data

    def divorce(self, user_id: int, chat_id: int):
        self.cursor.execute("DELETE FROM marriages WHERE chat_id = (?) AND (user1 = (?) OR user2 = (?))",
                            (chat_id, user_id, user_id))
        self.connection.commit()

    def __get_name(self, user_id: int):
        data = self.cursor.execute("SELECT * FROM users WHERE id = (?)", (user_id,)).fetchone()
        if data:
            return f"{data[1]}{' ' + data[2] if data[2] else ''}"
        else:
            return ''

    def add_new_user(self, chat_id: int, user_id: int, name: str, surname: str):
        name = quote_html(name)
        self.cursor.execute(f"INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)", (user_id, name, surname, chat_id))
        if self.cursor.rowcount > 0:
            self.cursor.execute(f"INSERT OR IGNORE INTO messages VALUES (?, ?, ?, ?)", (user_id, chat_id, 0, 0))
        self.connection.commit()

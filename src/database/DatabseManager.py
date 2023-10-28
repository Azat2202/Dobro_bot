import sqlite3

from aiogram.utils import emoji


class WeddingDb:
    __db_name = '../resources/wedding_users.db'

    def __init__(self):
        import os.path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, self.__db_name)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def is_married(self, user1, user2):
        is_first_married = self.cursor.execute('SELECT 1 FROM marriages WHERE (user1 = (?) OR user2 = (?)) AND '
                                               'betrothed = 1',
                                               (user1, user1)).fetchone()
        is_second_married = self.cursor.execute('SELECT 1 FROM marriages WHERE user1 = (?) OR user2 = (?) AND '
                                                'betrothed = 1',
                                                (user2, user2)).fetchone()
        return is_first_married or is_second_married

    def inc_message(self, user_id, chat_id, first_name, last_name):
        self.__add_new_user(user_id, first_name, last_name)
        data = self.cursor.execute("SELECT * FROM messages WHERE user_id = (?) AND chat_id = (?)",
                                   (user_id, chat_id)).fetchone()
        if data:
            self.cursor.execute("UPDATE messages SET message_count = (?) WHERE user_id = (?) AND chat_id = (?)",
                                (int(data[2]) + 1, user_id, chat_id))
        else:
            self.cursor.execute("INSERT OR IGNORE INTO messages VALUES (?, ?, 1, 0)", (user_id, chat_id))
        self.connection.commit()

    def inc_karma(self, user_id, chat_id):
        data = self.cursor.execute("SELECT * FROM messages WHERE user_id = (?) AND chat_id = (?)",
                                   (user_id, chat_id)).fetchone()
        self.cursor.execute("UPDATE messages SET karma = (?) WHERE user_id = (?) AND chat_id = (?)",
                            (int(data[3]) + 1, user_id, chat_id))

    def dec_karma(self, user_id, chat_id):
        data = self.cursor.execute("SELECT * FROM messages WHERE user_id = (?) AND chat_id = (?)",
                                   (user_id, chat_id)).fetchone()
        self.cursor.execute("UPDATE messages SET karma = (?) WHERE user_id = (?) AND chat_id = (?)",
                            (int(data[3]) - 1, user_id, chat_id))

    async def message_repr(self, msg: types.Message):
        data = self.cursor.execute("SELECT * FROM messages WHERE chat_id = (?)", (msg.chat.id,)).fetchall()
        data.sort(key=lambda s: s[2], reverse=True)
        out = 'Топ пользователей по написанным сообщениям: \n'
        num = 1
        for user in data:
            count = int(user[2])
            if count > 50_000:
                rank = 'главный спамер'
            elif count > 10_000:
                rank = 'активный спамер'
            elif count > 5_000:
                rank = 'небольшой спамер'
            elif count > 1000:
                rank = 'рядовой участник'
            elif count > 250:
                rank = 'тихоня'
            else:
                rank = 'новичок'
            out += f'{num}. {rank} {self.__get_name(user[0])} - {count} сообщений\n'
            num += 1
        await bot.send_message(msg.chat.id, out)
        await bot.delete_message(msg.chat.id, msg.message_id)

    async def karma_repr(self, msg: types.Message):
        out = 'Топ кармы: \n'
        data = self.cursor.execute("SELECT * FROM messages WHERE chat_id = (?)", (msg.chat.id,)).fetchall()
        data.sort(key=lambda s: s[3], reverse=True)
        num = 1
        for user in data:
            karma = int(user[3])
            print(karma)
            if karma < -1000:
                rank = 'токс'
            elif karma < -50:
                rank = 'злой'
            elif karma < -10:
                rank = 'злюка'
            elif karma < 0:
                rank = 'недоброжелательный'
            elif karma < 10:
                rank = 'добрый'
            elif karma < 25:
                rank = 'добряш'
            elif karma < 50:
                rank = 'очень добрый'
            else:
                rank = 'главный добряш'

            out += f'{num}. {rank} {self.__get_name(user[0])} - {karma}\n'
            num += 1
        await bot.send_message(msg.chat.id, out)
        await bot.delete_message(msg.chat.id, msg.message_id)

    async def registrate_new_marriage(self, msg: types.Message):
        sent_msg = await msg.reply(
            emoji.emojize(f'[{get_name(msg.reply_to_message)}](tg://user?id={msg.reply_to_message.from_user.id}), вы '
                          f'согласны заключить брак с [{get_name(msg)}](tg://user?id={msg.from_user.id})?\n '
                          f'Для заключения брака так же необходимы два свидетеля\n'
                          f'Согласие: :cross_mark:\n'
                          f'Первый свидетель: :cross_mark:\n'
                          f'Второй свидетель: :cross_mark:'), reply_markup=form_inline_kb(), parse_mode='Markdown')
        data = self.cursor.execute(f"SELECT * FROM marriages WHERE (user1 = (?) OR user2 = (?)) AND chat_id = (?) AND "
                                   f"betrothed = 0", (msg.from_user.id, msg.chat.id, msg.chat.id)).fetchall()
        if data:
            self.cursor.execute("DELTE FROM marriages WHERE (user1 = (?) OR user2 = (?)) AND chat_id = (?) AND "
                                "betrothed = 0", (msg.from_user.id, msg.chat.id))
        self.cursor.execute(f'''INSERT INTO marriages (user1, user2, date, chat_id, message_id, betrothed, agreed) VALUES 
                                (?, ?, ?, ?, ?, ?, ?)''', (msg.from_user.id, msg.reply_to_message.from_user.id,
                                                           datetime.datetime.now().strftime("%y-%m-%d %H:%M:%S"),
                                                           msg.chat.id, sent_msg.message_id, 0, 0))
        self.__add_new_user(msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name)
        self.__add_new_user(msg.reply_to_message.from_user.id, msg.reply_to_message.from_user.first_name,
                            msg.reply_to_message.from_user.last_name)
        self.connection.commit()

    async def marriage_agree(self, call: types.CallbackQuery):
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and message_id = (?)",
                                   (call.message.chat.id, call.message.message_id)).fetchone()
        if call.from_user.id != data[1]:
            await call.answer('Вы не можете дать согласие')
            return
        self.cursor.execute("UPDATE marriages SET agreed = 1 WHERE chat_id = (?) and message_id = (?)",
                            (call.message.chat.id, call.message.message_id))
        self.connection.commit()
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and message_id = (?)",
                                   (call.message.chat.id, call.message.message_id)).fetchone()
        mrg_time = datetime.datetime.strptime(data[2], "%y-%m-%d %H:%M:%S")
        time_delta = datetime.datetime.now() - mrg_time
        if time_delta.seconds > 600:
            await call.answer(emoji.emojize("Прошло слишком много времени, брак заключить нельзя! :alarm_clock:"))
            await call.message.edit_reply_markup()
            await call.message.edit_text(
                f"{self.__get_name(data[0])} и {self.__get_name(data[1])} не успели за 10 минут(")
            return
        if data[3] and data[4] and data[8] == 1:
            await call.answer("Поздравляем, вы вступили в брак!")
            self.cursor.execute("UPDATE marriages SET betrothed = 1 WHERE chat_id = (?) and message_id = (?)",
                                (call.message.chat.id, call.message.message_id))
            await call.message.edit_reply_markup()
            await call.message.edit_text(f"{self.__get_name(data[0])} и {self.__get_name(data[1])} вступили в брак!")
        else:
            await call.answer("Поздравляем! Вы согласились на вступление в брак, осталось найти свидетелей")
            await call.message.edit_text(emoji.emojize(
                f'Для заключения брака так же необходимы два свидетеля\n'
                f'Согласие: :check_mark_button:\n'
                f'Первый свидетель: {":check_mark_button:" if data[3] else ":cross_mark:"}\n'
                f'Второй свидетель: {":check_mark_button:" if data[4] else ":cross_mark:"})'),
                reply_markup=form_inline_kb(agreement=False), parse_mode='Markdown')

    async def marriage_disagree(self, call):
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and message_id = (?)",
                                   (call.message.chat.id, call.message.message_id)).fetchone()
        if call.from_user.id != data[1]:
            await call.answer('Вы не можете отказаться от свадьбы!')
            return
        self.cursor.execute("DELETE FROM marriages WHERE chat_id = (?) and message_id = (?)",
                            (call.message.chat.id, call.message.message_id))
        await call.message.edit_reply_markup()
        await call.message.edit_text(
            f"[{self.__get_name(data[1])}](tg://user?id={data[0]}) отказал в браке [{self.__get_name(data[0])}](tg://user?id={data[0]})",
            parse_mode='Markdown')
        self.connection.commit()

    async def marriage_witness(self, call: types.CallbackQuery):
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and message_id = (?)",
                                   (call.message.chat.id, call.message.message_id)).fetchone()
        if call.from_user.id in (data[0], data[1], data[3], data[4]):
            await call.answer('Вы уже учавствуете в свадьбе')
            return
        mrg_time = datetime.datetime.strptime(data[2], "%y-%m-%d %H:%M:%S")
        time_delta = datetime.datetime.now() - mrg_time
        if time_delta.seconds > 600:
            await call.answer("Прошло слишком много времени, свидетелем стать нельзя!")
            await call.message.edit_text(
                emoji.emojize(
                    f"[{self.__get_name(data[0])}](tg://user?id={data[0]}) и [{self.__get_name(data[1])}](tg://user?id={data[1]}) не нашли свидетелей:alarm_clock::"),
                parse_mode='Markdown')
            return
        if not data[3]:  # Первый свидетель
            self.cursor.execute(f"UPDATE marriages SET witness1 = (?) WHERE chat_id = (?) and message_id = (?)",
                                (call.from_user.id, call.message.chat.id, call.message.message_id))
            await call.answer("Теперь вы свидетель!")
            if data[8]:
                await call.message.edit_text(emoji.emojize(
                    f'[{self.__get_name(data[1])}](tg://user?id={data[1]}), вы согласны заключить брак с [{self.__get_name(data[0])}](tg://user?id={data[0]})?\n'
                    f'Для заключения брака так же необходимы два свидетеля\n'
                    f'Согласие: {":check_mark_button:" if data[8] == 1 else ":cross_mark:"}\n'
                    f'Первый свидетель: :check_mark_button:\n'
                    f'Второй свидетель: :cross_mark:'),
                    reply_markup=form_inline_kb(agreement=False if data[8] == 1 else True),
                    parse_mode='Markdown')
            else:
                await call.message.edit_text(emoji.emojize(f'Для заключения брака так же необходимы два свидетеля\n'
                                                           f'Согласие: {":check_mark_button:" if data[8] == 1 else ":cross_mark:"}\n'
                                                           f'Первый свидетель: :check_mark_button:\n'
                                                           f'Второй свидетель: :cross_mark:'),
                                             reply_markup=form_inline_kb(agreement=False if data[8] == 1 else True))
            self.__add_new_user(call.from_user.id, call.from_user.first_name, call.from_user.last_name)
        elif not data[4]:
            self.cursor.execute(f"UPDATE marriages SET witness2 = (?) WHERE chat_id = (?) and "
                                f"message_id = (?)",
                                (call.from_user.id, call.message.chat.id, call.message.message_id))
            await call.answer("Теперь вы свидетель!")
            if data[8] == 1:
                self.cursor.execute(f"UPDATE marriages SET betrothed = (?) WHERE chat_id = (?) and "
                                    f"message_id = (?)",
                                    (1, call.message.chat.id, call.message.message_id))
                await call.message.edit_text(
                    f"Поздравляем молодоженов! [{self.__get_name(data[0])}](tg://user?id={data[0]}) и [{self.__get_name(data[1])}](tg://user?id={data[1]}) теперь в браке!",
                    parse_mode='Markdown')
            else:
                await call.message.edit_text(emoji.emojize(f'Для заключения брака осталось согласие\n'
                                                           f'Согласие: :cross_mark:\n'
                                                           f'Первый свидетель: :check_mark_button:\n'
                                                           f'Второй свидетель: :check_mark_button:'),
                                             reply_markup=form_inline_kb(witness=False))
            self.__add_new_user(call.from_user.id, call.from_user.first_name, call.from_user.last_name)
        self.connection.commit()

    async def marriages_repr(self, msg: types.Message):
        data = self.cursor.execute("SELECT * FROM marriages WHERE betrothed = 1 ORDER BY date").fetchall()
        out = 'Статистика по бракам:\n'
        num = 0
        for line in data:
            if line[5] == msg.chat.id:
                num += 1
                time_obj = datetime.datetime.now() - datetime.datetime.strptime(line[2], "%y-%m-%d %H:%M:%S")
                out += f'{num}. [{self.__get_name(line[0])}](tg://user?id={line[0]}) и [{self.__get_name(line[1])}](tg://user?id={line[1]}) - {beautiful_time_repr(time_obj)}\n'
                out += f'   Свидетели: {self.__get_name(line[3])} и {self.__get_name(line[4])}\n'
        out += f'\nВсего {num} браков'
        if num == 0:
            out = 'В этой группе еще нет ни одного брака!'
        await msg.reply(out, parse_mode='Markdown')

    async def divorce(self, msg: types.Message):
        data = self.cursor.execute("SELECT * FROM marriages WHERE chat_id = (?) and (user1 = (?) or user2 = (?))",
                                   (msg.chat.id, msg.from_user.id, msg.from_user.id)).fetchone()
        if not data:
            await msg.reply('Вы не состоите в браке!')
            return
        inline_divorce_agreement = InlineKeyboardButton('Да', callback_data=f'divorce {data[5]} {msg.from_user.id}')
        inline_divorce_refusal = InlineKeyboardButton('Отмена', callback_data=f'not_divorce {msg.from_user.id}')
        inline_divorce_kb = InlineKeyboardMarkup().add(inline_divorce_agreement, inline_divorce_refusal)
        await msg.reply('Вы уверены что собираетесь развестись?', reply_markup=inline_divorce_kb)

    async def del_marriage(self, call, chat_id, user_id):
        if call.from_user.id != user_id:
            await call.answer('Вы не можете подтвердить развод')
            return
        self.cursor.execute("DELETE FROM marriages WHERE chat_id = (?) AND (user1 = (?) OR user2 = (?))",
                            (chat_id, user_id, user_id))
        await call.message.edit_text("Вы развелись")

    async def edit_divorce(self, call: types.CallbackQuery, user_id):
        if user_id != call.from_user.id:
            await call.answer('Вы не можете отменить развод!')
            return
        await call.message.edit_text("Развод отменен")
        await call.answer()

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

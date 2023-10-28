import emoji
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import filters
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from get_users import users
from emoji import emojize
from random import randint, choice
from time import sleep, time
from wishes import get_wishes
import datetime
import requests
from bs4 import BeautifulSoup
import sqlite3
import os

API_TOKEN = os.getenv("API_TOKEN")
API_URL = "https://api-inference.huggingface.co/models/apanc/russian-inappropriate-messages"
db_name = 'wedding_users.db'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
wait_seconds = 1800
wait_seconds_for_horo = 30000
wait_seconds_for_mention = 1000
last_time_banned = datetime.datetime.now() - datetime.timedelta(seconds=wait_seconds)
last_time_horo = datetime.datetime.now() - datetime.timedelta(days=1)
last_time_mentioned = datetime.datetime.now() - datetime.timedelta(seconds=wait_seconds_for_mention)
massive = [1 for i in users]


# TODO:
# 1) Отметки в свадьбе
# 2) Шведские браки


class WeddingDb:
    def __init__(self, database):
        import os.path
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(BASE_DIR, db_name)
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def is_married(self, user1, user2):
        is_first_married = self.cursor.execute('SELECT 1 FROM marriages WHERE (user1 = (?) OR user2 = (?)) AND '
                                               'betrothed = 1',
                                               (user1, user1)).fetchone()
        is_second_married = self.cursor.execute('SELECT 1 FROM marriages WHERE user1 = (?) OR user2 = (?) AND '
                                                'betrothed = 1',
                                                (user2, user2)).fetchone()
        if is_first_married or is_second_married:
            return True
        else:
            return False

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


def create_tables():
    db_worker = WeddingDb(db_name)
    db_worker.cursor.execute("CREATE TABLE IF NOT EXISTS messages (user_id INT NOT NULL, chat_id INT NOT NULL, "
                             "message_count INT, karma INT);")
    db_worker.close()


def get_name(msg: types.Message):
    return f'{msg.from_user.first_name}{" " + msg.from_user.last_name if msg.from_user.last_name else ""}'


def form_repr(num) -> str:
    global massive
    pistol = emojize(":water_pistol:")
    out = ''
    if num == -1:
        for person in users:
            out += f'{pistol}{person.name}{"" if person.surname is None else " " + str(person.surname)},\n'
    else:
        for per_num, person in enumerate(users):
            if massive[per_num] == 1:
                out += f'{pistol}{person.name}{"" if person.surname is None else " " + str(person.surname)},\n'
            else:
                out += f'— {person.name}{"" if person.surname is None else " " + str(person.surname)},\n'
    return out


def beautiful_time_repr(time_: datetime.timedelta) -> str:
    if time_.days > 365:
        return f'{time_.days // 365} лет и {time_.days % 365} дней'
    if time_.days > 0:
        return f'{time_.days} дней'
    if time_.seconds > 3601:
        return f'{time_.seconds // 3601} часов'
    if time_.seconds > 60:
        return f'{time_.seconds // 60} минут'
    return f'{time_.seconds} секунд'


inline_wedding_agreement = InlineKeyboardButton('Согласен', callback_data='agreement')
inline_wedding_refusal = InlineKeyboardButton('Не согласен', callback_data='refusal')
inline_wedding_witness = InlineKeyboardButton('Я свидетель', callback_data='witness')


def form_inline_kb(agreement: bool = True, witness: bool = True) -> types.InlineKeyboardMarkup:
    inline_wedding_kb = InlineKeyboardMarkup()
    if agreement:
        inline_wedding_kb.add(inline_wedding_agreement, inline_wedding_refusal)
    if witness:
        inline_wedding_kb.add(inline_wedding_witness)
    return inline_wedding_kb


@dp.callback_query_handler(lambda c: c.data[:7] == 'divorce')
async def agreed(call: types.CallbackQuery):
    db_worker = WeddingDb(db_name)
    data = call.data.split()
    await db_worker.del_marriage(call, int(data[1]), int(data[2]))
    db_worker.close()


@dp.callback_query_handler(lambda c: c.data[:11] == 'not_divorce')
async def agreed(call: types.CallbackQuery):
    data = call.data.split()
    db_worker = WeddingDb(db_name)
    await db_worker.edit_divorce(call, int(data[1]))
    db_worker.close()


@dp.callback_query_handler(lambda c: c.data == 'agreement')
async def agreed(call: types.CallbackQuery):
    db_worker = WeddingDb(db_name)
    await db_worker.marriage_agree(call)
    db_worker.close()


@dp.callback_query_handler(lambda c: c.data == 'refusal')
async def refused(call: types.CallbackQuery):
    db_worker = WeddingDb(db_name)
    await db_worker.marriage_disagree(call)
    db_worker.close()


@dp.callback_query_handler(lambda c: c.data == 'witness')
async def refused(call: types.CallbackQuery):
    db_worker = WeddingDb(db_name)
    await db_worker.marriage_witness(call)
    db_worker.close()


@dp.message_handler(filters.Text(equals='!Помощь', ignore_case=True))
@dp.message_handler(commands='help')
async def help_(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply('Список всех доступных команд:\n'
                        '/marry или !Брак - Заключить брак с человеком из чата\n'
                        '/divorce или !Развод - Развестись\n'
                        '/marriages или !Браки - Показать текущие браки\n'
                        '/anek или !Анекдот - Отправить случайный анекдот\n'
                        'Важный вопрос ... - Задать важный вопрос\n'
                        'Вопрос ... - Задать вопрос да/нет\n'
                        'Совместимость ... - Узнать свою совместимость с человеком\n'
                        '/horo или !Гороскоп - Получить индивидуальный гороскоп\n'
                        '/horo_for_all - Отправить гороскоп для всех\n'
                        '/mark_all или !Сбор - Отметить всех участников\n'
                        'добряш или плюс или Спасибо - Повысить карму \n'
                        'минус или токс - Понизить карму\n'
                        '/top_spamers или !Спамеры - Топ участников по сообщениям\n'
                        '/top_karma или !Карма - Топ учатников по карме')


@dp.message_handler(commands=['horo_for_all'])
async def solo_horo(message: types.Message):
    global last_time_horo
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    now_time = datetime.datetime.now()
    delta = now_time - last_time_horo
    out = ''
    if delta.seconds > wait_seconds_for_horo or delta.days > 0:
        last_time_horo = now_time
        for person in users:
            today_horo = get_wishes(users)
            out += f'[{person.name}](tg://user?id={person.user_id}){choice(today_horo)}\n'
        await bot.send_message(message.chat.id, out, parse_mode='Markdown', reply_to_message_id=message.message_id)
    else:
        await bot.send_message(message.chat.id,
                               f'До использования команды заново осталось {(wait_seconds_for_horo - delta.seconds) // 3600} часов')
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(filters.Text(equals='!Сбор', ignore_case=True))
@dp.message_handler(commands=['mark_all'])
async def mark_all(message: types.Message):
    global last_time_mentioned
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    now_time = datetime.datetime.now()
    delta = now_time - last_time_mentioned
    out = ''
    if delta.seconds > wait_seconds_for_mention or delta.days > 0:
        last_time_mentioned = now_time
        out += f'{message.from_user.first_name} ОРГАНИЗОВАЛ ВСЕОБЩИЙ СБОР\n'
        for person in users:
            out += f'[{person.name}](tg://user?id={person.user_id})  '
        await bot.send_message(message.chat.id, out, parse_mode='Markdown')
    else:
        await bot.send_message(message.chat.id,
                               f'До использования команды заново осталось {(wait_seconds_for_mention - delta.seconds) // 3600} часов')
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(filters.Text(equals='!Гороскоп', ignore_case=True))
@dp.message_handler(commands=['horo'])
async def all_horo(message: types.Message):
    today_horo = get_wishes(users)
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    out = f'{message.from_user.first_name}{"" if message.from_user.last_name is None else " " + str(message.from_user.last_name)}{choice(today_horo)}'
    await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id)


# @dp.message_handler(filters.Text(equals='!Бан', ignore_case=True))
# @dp.message_handler(commands=['ban'])
# async def kill_sbd(message: types.Message):
#     global last_time_banned, massive
#     db_worker = WeddingDb(db_name)
#     db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
#     db_worker.close()
#     now_time = datetime.datetime.now()
#     delta = now_time - last_time_banned
#     if delta.seconds > wait_seconds or delta.days > 0:
#         massive = [1 for i in users]
#         last_time_banned = now_time
#         last_message = await message.reply(form_repr(-1))
#         num_to_ban = randint(0, len(users) - 1)
#         while sum(massive) != 1:
#             sleep(sum(massive) / 100)
#             num1 = randint(0, len(users) - 1)
#             while num1 == num_to_ban or massive[num1] == 0:
#                 num1 = randint(0, len(users) - 1)
#             num2 = randint(0, len(users) - 1)
#             while num2 == num_to_ban or massive[num2] == 0:
#                 num2 = randint(0, len(users) - 1)
#             massive[num1] = 0
#             massive[num2] = 0
#             await bot.edit_message_text(form_repr(num_to_ban), message.chat.id, last_message.message_id)
#         sleep(2)
#         await bot.delete_message(message.chat.id, message.message_id)
#         await bot.edit_message_text(
#             f'{users[num_to_ban].name} {"" if users[num_to_ban].surname is None else " " + str(users[num_to_ban].surname) + " "}забанен на 5 минут{emojize(":smiling_face_with_horns:")}',
#             message.chat.id, last_message.message_id)
#         await bot.restrict_chat_member(message.chat.id, users[num_to_ban].user_id, can_send_messages=False,
#                                        until_date=int((time() + 3600)))
#     else:
#         await bot.delete_message(message.chat.id, message.message_id)
#         await bot.send_message(message.chat.id,
#                                f'До использования команды заново осталось {wait_seconds - delta.seconds} секунд')


@dp.message_handler(filters.Text(startswith='Совместимость', ignore_case=True))
async def connection(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(f'Ты и {message.text[14::]} вместе с шансом {randint(0, 100)}%')


@dp.message_handler(filters.Text(startswith='Вопрос', ignore_case=True))
async def yn(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(choice(['Да', "Нет"]))


# @dp.message_handler(commands='truth')
# @dp.message_handler(filters.Text(startswith='!Правда', ignore_case=True))
# async def yn(message: types.Message):
#     db_worker = WeddingDb(db_name)
#     db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
#     db_worker.close()
#     await message.reply(get_true())


# @dp.message_handler(filters.Text(startswith='!Действие', ignore_case=True))
# @dp.message_handler(commands='dare')
# async def yn(message: types.Message):
#     db_worker = WeddingDb(db_name)
#     db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
#     db_worker.close()
#     await message.reply(get_action())


@dp.message_handler(filters.Text(startswith='Важный вопрос', ignore_case=True))
async def yn(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(choice(['Да', "Нет", "Это не важно", "Успокойся", "Не спрашивай такое", "Да, хотя зря",
                                "Никогда", "100%", "1 из 100", "Спроси еще раз"]))


# @dp.message_handler(filters.Text(equals='!Секс', ignore_case=True))
# @dp.message_handler(commands='sex')
# async def yn(message: types.Message):
#     db_worker = WeddingDb(db_name)
#     db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
#     db_worker.close()
#     await message.reply(
#         f'У тебя будет {choice(["жесткий", "медленный", "быстрый", "приятный", "неприятный", "необычный", "романтичный"])} секс с {choice(users).name}')


@dp.message_handler(filters.Text(equals='!Анекдот', ignore_case=True))
@dp.message_handler(commands='anek')
async def anek(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    anek_url = 'https://baneks.ru/random'
    response = requests.get(anek_url)
    soup = BeautifulSoup(response.text, 'lxml')
    joke = soup.find('article')
    await message.reply(joke.text)


@dp.message_handler(filters.Text(equals='!Брак', ignore_case=True))
@dp.message_handler(commands=['marry'])
async def new_marriage(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    if message.reply_to_message:
        db_worker = WeddingDb(db_name)
        if db_worker.is_married(message.from_user.id, message.reply_to_message.from_user.id):
            await message.reply('Вы уже состоите в браке!')
            db_worker.close()
            return
        if message.reply_to_message.from_user.id == message.from_user.id:
            await message.reply('Вы не можете заключить брак самим с собой!')
            db_worker.close()
            return
        await db_worker.registrate_new_marriage(message)
        db_worker.close()
    else:
        await message.reply('Чтобы заключить брак вам необходимо ответить командой на сообщение')


@dp.message_handler(filters.Text(equals='!Браки', ignore_case=True))
@dp.message_handler(commands='marriages')
async def marriages_repr(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await db_worker.marriages_repr(message)
    db_worker.close()


@dp.message_handler(filters.Text(equals='!Развод', ignore_case=True))
@dp.message_handler(commands='divorce')
async def divorce(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await db_worker.divorce(message)
    db_worker.close()


@dp.message_handler(commands='top_spamers')
@dp.message_handler(filters.Text(equals='!Спамеры', ignore_case=True))
async def spamers_repr(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await db_worker.message_repr(message)
    db_worker.close()


@dp.message_handler(commands='top_karma')
@dp.message_handler(filters.Text(equals='!Карма', ignore_case=True))
async def spamers_repr(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await db_worker.karma_repr(message)
    db_worker.close()


@dp.message_handler(filters.Text(equals='добряш', ignore_case=True))
@dp.message_handler(filters.Text(equals='плюс', ignore_case=True))
@dp.message_handler(filters.Text(equals='спасибо', ignore_case=True))
async def plus_karma(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    if message.reply_to_message:
        if(message.reply_to_message.from_user.id == message.from_user.id):
            await message.reply('Нельзя изменять карму себе')
        else:
            db_worker.inc_karma(message.reply_to_message.from_user.id, message.chat.id)
            await message.reply('Карма увеличена!')
    else:
        await message.reply('Увеличить карму можно ответом на сообщение')
    db_worker.close()


@dp.message_handler(filters.Text(equals='минус', ignore_case=True))
@dp.message_handler(filters.Text(equals='токс', ignore_case=True))
async def plus_karma(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    if message.reply_to_message:
        if(message.reply_to_message.from_user.id == message.from_user.id):
            await message.reply('Нельзя изменять карму себе')
        else:
            db_worker.dec_karma(message.reply_to_message.from_user.id, message.chat.id)
            await message.reply('Карма уменьшена! ')
    else:
        await message.reply('Уменьшить карму можно ответом на сообщение')
    db_worker.close()

@dp.message_handler()
async def common_message(message: types.Message):
    db_worker = WeddingDb(db_name)
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    # print(output)
    #if(output[0][1]['score'] > 0.65):
    #   await message.reply('Это сообщение очень токсичное, ваша карма уменьшена')
    #  db_worker.dec_karma(message.reply_to_message.from_user.id, message.chat.id)
    #elif(output[0][1]['score'] > 0.3):
    #    await message.reply("Это сообщение выглядит достаточно токсичным, пожалуйста будьте добрее")
    db_worker.close()
    


if __name__ == '__main__':
    create_tables()
    executor.start_polling(dp, skip_updates=True)

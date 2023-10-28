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

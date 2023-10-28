import datetime
from random import choice, randint

from aiogram import types
from aiogram.dispatcher import filters

from src.configuration import *
from src.database.DatabseManager import DatabaseManager
from src.get_users import users
from src.main import bot, dp

last_time_horo = datetime.datetime.now() - datetime.timedelta(days=1)
@dp.message_handler(commands=['horo_for_all'])
async def solo_horo(message: types.Message):
    global last_time_horo
    db_worker = DatabaseManager()
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

@dp.message_handler(filters.Text(equals='!Гороскоп', ignore_case=True))
@dp.message_handler(commands=['horo'])
async def all_horo(message: types.Message):
    today_horo = get_wishes(users)
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    out = f'{message.from_user.first_name}{"" if message.from_user.last_name is None else " " + str(message.from_user.last_name)}{choice(today_horo)}'
    await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id)



def get_wishes(users):
    a = [f', у тебя будет {choice(["добрый", "хороший", "плохой", "ахуенный", "пиздатый", "хуевый", "ебаный"])} день',
         f', тебя любит {choice(users).name}',
         f', сегодня ты ляжешь спать раньше {randint(1, 7)}',
         f', ты {choice(["сдашь", "не сдашь"])} кр по {choice(["матану", "дму", "линалу"])}',
         f', ты {choice(["сдашь", "не сдашь"])} лабу по {choice(["информатике", "проге", "опд", "япам", "вебу", "бд"])}',
         f', сегодня {choice(users).name} {choice(["не назовет", "назовет"])} тебя добрым',
         f', {choice(users).name} тебе купит покушать',
         f', тебе {choice(["", "не "])}купит одноразку {choice(users).name}',
         f', ты завтра {choice(["", "не "])}пойдешь ко второй паре',
         f', ты выпьешь пива с {choice(users).name}'
         ]
    return a

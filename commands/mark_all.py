import datetime

from aiogram import types
from aiogram.dispatcher import filters

from configuration import *
from database.DatabseManager import DatabaseManager
from get_users import users
from loader import dp, bot


@dp.message_handler(filters.Text(equals='!Сбор', ignore_case=True))
@dp.message_handler(commands=['mark_all'])
async def mark_all(message: types.Message):
    global last_time_mentioned
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
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

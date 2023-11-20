import datetime

from aiogram import types
from aiogram.dispatcher import filters

from configuration import *
from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp, bot

last_time_mentioned = datetime.datetime.min


@dp.message_handler(filters.Text(equals='!Сбор', ignore_case=True))
@dp.message_handler(commands=['mark_all'])
async def mark_all(message: types.Message):
    global last_time_mentioned
    with WeddingDatabaseManager() as db_worker:
        users = db_worker.get_users(message.chat.id)
    now_time = datetime.datetime.now()
    delta = now_time - last_time_mentioned
    out = ''
    if delta.seconds > wait_seconds_for_mention or delta.days > 0:
        last_time_mentioned = now_time
        out += f'{message.from_user.first_name} ОРГАНИЗОВАЛ ВСЕОБЩИЙ СБОР\n'
        for user_id, name, surname in users:
            out += f'[{name}](tg://user?id={user_id})\n'
        await bot.send_message(message.chat.id, out, parse_mode='Markdown')
    else:
        await bot.send_message(message.chat.id,
                               f'До использования команды заново осталось {(wait_seconds_for_mention - delta.seconds) // 3600 + 1} часа')
    await bot.delete_message(message.chat.id, message.message_id)

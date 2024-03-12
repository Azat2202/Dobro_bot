from aiogram import types
from aiogram.dispatcher import filters

import utility
from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp, bot
from utility import format_name, spam_degrees, karma_degrees


@dp.message_handler(commands='top_spammers')
async def spammers_repr(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        data = db_worker.get_top_spammers(message.chat.id, 10)
    out = 'Топ-10 пользователей по написанным сообщениям: \n'
    for i, user in enumerate(data):
        count = int(user[2])
        out += f'{i + 1}. <b>{format_name(user[0], user[1])}</b> - {count} сообщений\n'
    await bot.send_message(message.chat.id, out)


@dp.message_handler(commands='top_karma')
async def karma_repr(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        data = db_worker.top_karma(message.chat.id, 10)
    out = 'Топ-10 кармы в чате: \n'
    for i, user in enumerate(data):
        karma = int(user[2])
        out += f'{i + 1}. <b>{format_name(user[0], user[1])}</b> - {karma}\n'
    await bot.send_message(message.chat.id, out)


@dp.message_handler(commands='my_stats')
async def spammers_repr(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        name, surname, message_count, karma_count = db_worker.get_user(message.chat.id, message.from_user.id)
    out = f"""
🌟Ваша статистика:🌟
💼Имя: {name }💼
📩Вы написали: {message_count} сообщений 📩
Вы - {utility.get_spammer_rank(message_count)}
😇У вас {karma_count} кармы 😇
Уровень кармы: {utility.get_karma_rank(karma_count)}
"""
    await bot.send_message(message.chat.id, out)

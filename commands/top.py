from aiogram import types
from aiogram.dispatcher import filters

from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp, bot
from utility import format_name, rank_degrees, karma_degrees


@dp.message_handler(commands='top_spamers')
@dp.message_handler(filters.Text(equals='!Спамеры', ignore_case=True))
async def spamers_repr(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        data = db_worker.get_messages(message.chat.id)
    out = 'Топ пользователей по написанным сообщениям: \n'
    num = 1
    for user in data:
        count = int(user[2])
        rank = ""
        for c, r in rank_degrees.items():
            if count > c:
                rank = r
                break
        out += f'{num}. {rank} <b>{format_name(user[0], user[1])}</b> - {count} сообщений\n'
        num += 1
    await bot.send_message(message.chat.id, out)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(commands='top_karma')
@dp.message_handler(filters.Text(equals='!Карма', ignore_case=True))
async def karma_repr(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        data = db_worker.karma_repr(message.chat.id)
    out = 'Топ кармы: \n'
    num = 1
    for user in data:
        karma = int(user[2])
        rank = ""
        for c, r in karma_degrees.items():
            if karma < c:
                rank = r
                break
        out += f'{num}. {rank} <b>{format_name(user[0], user[1])}</b> - {karma}\n'
        num += 1
    await bot.send_message(message.chat.id, out)
    await bot.delete_message(message.chat.id, message.message_id)

from aiogram import types
from aiogram.dispatcher import filters

from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp, bot
from utility import format_name


@dp.message_handler(commands='top_spamers')
@dp.message_handler(filters.Text(equals='!Спамеры', ignore_case=True))
async def spamers_repr(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        data = db_worker.get_messages(message.chat.id)
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
            rank = 'обычный участник'
        elif count > 250:
            rank = 'тихоня'
        else:
            rank = 'новичок'
        out += f'{num}. {rank} <b>{format_name(user[0], user[1])}</b> - {count} сообщений\n'
        num += 1
    await bot.send_message(message.chat.id, out)
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(commands='top_karma')
@dp.message_handler(filters.Text(equals='!Карма', ignore_case=True))
async def spamers_repr(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        data = db_worker.karma_repr(message.chat.id)
    out = 'Топ кармы: \n'
    num = 1
    for user in data:
        karma = int(user[2])
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

        out += f'{num}. {rank} <b>{format_name(user[0], user[1])}</b> - {karma}\n'
        num += 1
    await bot.send_message(message.chat.id, out)
    await bot.delete_message(message.chat.id, message.message_id)

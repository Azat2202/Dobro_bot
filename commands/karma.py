from aiogram import types
from aiogram.dispatcher import filters

from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp


@dp.message_handler(filters.Text(equals='добряш', ignore_case=True))
@dp.message_handler(filters.Text(equals='плюс', ignore_case=True))
@dp.message_handler(filters.Text(equals='спасибо', ignore_case=True))
async def plus_karma(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('Нельзя изменять карму себе')
            else:
                db_worker.inc_karma(message.reply_to_message.from_user.id, message.chat.id)
                if db_worker.is_parent(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                    db_worker.inc_karma(message.reply_to_message.from_user.id, message.chat.id)
                    await message.reply('Карма увеличена в двойном размере!')
                else:
                    await message.reply('Карма увеличена!')
        else:
            await message.reply('Увеличить карму можно ответом на сообщение')


@dp.message_handler(filters.Text(equals='минус', ignore_case=True))
@dp.message_handler(filters.Text(equals='токс', ignore_case=True))
async def minus_karma(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('Нельзя изменять карму себе')
            else:
                db_worker.dec_karma(message.reply_to_message.from_user.id, message.chat.id)
                if db_worker.is_parent(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                    db_worker.dec_karma(message.reply_to_message.from_user.id, message.chat.id)
                    await message.reply('Карма уменьшена в двойном размере!')
                else:
                    await message.reply('Карма уменьшена!')
        else:
            await message.reply('Уменьшить карму можно ответом на сообщение')

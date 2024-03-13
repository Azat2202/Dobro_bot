from aiogram import types
from aiogram.dispatcher import filters

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp
from utility import karma_degrees


@dp.message_handler(filters.Text(startswith="добряш", ignore_case=True))
@dp.message_handler(filters.Text(startswith="умник", ignore_case=True))
@dp.message_handler(filters.Text(startswith="умница", ignore_case=True))
@dp.message_handler(filters.Text(startswith="молодец", ignore_case=True))
@dp.message_handler(filters.Text(startswith="плюс", ignore_case=True))
@dp.message_handler(filters.Text(startswith="спасибо", ignore_case=True))
async def plus_karma(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Увеличить карму можно ответом на сообщение")
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        await message.reply("Нельзя изменять карму себе")
        return
    with UsersDatabaseManager() as db_worker:
        karma = db_worker.inc_karma(
            message.reply_to_message.from_user.id, message.chat.id
        )
        if db_worker.is_parent(
            message.from_user.id, message.reply_to_message.from_user.id, message.chat.id
        ):
            karma = db_worker.inc_karma(
                message.reply_to_message.from_user.id, message.chat.id
            )
            await message.reply(f"Карма увеличена в двойном размере! ({karma})")
        else:
            await message.reply(f"Карма увеличена! ({karma})")
    if karma in karma_degrees.keys():
        await message.reply(
            "🎉🎉Поздравляем!🎉🎉\n"
            f"Теперь вы <b>{karma_degrees.get(karma)}!</b>\n"
            f"Ваше количество кармы: {karma}"
        )


@dp.message_handler(filters.Text(equals="минус", ignore_case=True))
@dp.message_handler(filters.Text(equals="токс", ignore_case=True))
async def minus_karma(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Уменьшить карму можно ответом на сообщение")
        return
    if message.reply_to_message.from_user.id == message.from_user.id:
        await message.reply("Нельзя изменять карму себе")
        return
    with UsersDatabaseManager() as db_worker:
        karma = db_worker.dec_karma(
            message.reply_to_message.from_user.id, message.chat.id
        )
        if db_worker.is_parent(
            message.from_user.id, message.reply_to_message.from_user.id, message.chat.id
        ):
            karma = db_worker.dec_karma(
                message.reply_to_message.from_user.id, message.chat.id
            )
            await message.reply(f"Карма уменьшена в двойном размере! ({karma})")
        else:
            await message.reply(f"Карма уменьшена! ({karma})")
    if karma in karma_degrees.keys():
        await message.reply(
            "🤬🤬Вы потеряли карму!🤬🤬\n"
            f"Теперь вы <b>{karma_degrees.get(karma)}!</b>\n"
            f"Ваше количество кармы: {karma}"
        )

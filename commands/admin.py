import aiogram
from aiogram import types

from database.SettingsDatabaseManager import SettingsDatabaseManager
from loader import dp, ADMIN_USERS, bot


@dp.message_handler(commands="send_update_log")
async def settings_poll_creation(message: types.Message):
    if not message.from_user.id in ADMIN_USERS:
        await message.reply("Вы не админ чата!")
        return
    with SettingsDatabaseManager() as db_worker:
        for chat_id in db_worker.get_chats_with_updatelogs():
            try:
                bot.send_message(chat_id, message.text)
            except aiogram.exceptions.BadRequest:
                pass

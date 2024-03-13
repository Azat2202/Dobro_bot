import aiogram
from aiogram import types

from database.SettingsDatabaseManager import SettingsDatabaseManager
from loader import dp, ADMIN_USERS, bot


@dp.message_handler(commands="send_update_log")
async def settings_poll_creation(message: types.Message):
    if not message.from_user.id in ADMIN_USERS:
        await message.reply("Вы не админ бота!")
        return
    with SettingsDatabaseManager() as db_worker:
        for data in db_worker.get_chats_with_updatelogs():
            try:
                await bot.send_message(data[0],
                                       message.text[len("/send_update_log"):])
            except aiogram.exceptions.BadRequest:
                pass

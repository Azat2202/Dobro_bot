from aiogram import types

from loader import dp, bot
from database.SettingsDatabaseManager import SettingsDatabaseManager


@dp.message_handler(commands="settings_poll_creation")
async def settings_poll_creation(message: types.Message):
    if not (
        await bot.get_chat_member(message.chat.id, message.from_user.id)
    ).is_chat_admin():
        await message.reply("Вы не админ чата!")
        return
    with SettingsDatabaseManager() as db_worker:
        if db_worker.change_poll_parameter(message.chat.id):
            await message.reply(
                "Теперь бот будет отправлять опросы каждый день в 19:00"
            )
        else:
            await message.reply("Бот больше не будет отправлять опросы настроения!")

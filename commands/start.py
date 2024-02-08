from aiogram import types

from loader import dp
from database.SettingsDatabaseManager import SettingsDatabaseManager


@dp.message_handler(commands="start")
async def start(message: types.Message):
    with SettingsDatabaseManager() as db_worker:
        db_worker.add_chat(message.chat.id)
    await message.reply(
        "Привет, я доброБот, самый добрый бот. Ознакомься со списком команд по команде /help!"
    )

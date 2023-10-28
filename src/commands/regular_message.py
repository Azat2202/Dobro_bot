from aiogram import types

from src.database.DatabseManager import DatabaseManager
from src.main import dp


@dp.message_handler()
async def common_message(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
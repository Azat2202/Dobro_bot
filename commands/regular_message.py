from aiogram import types

from database.DatabseManager import DatabaseManager
from loader import dp


@dp.message_handler()
async def common_message(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)

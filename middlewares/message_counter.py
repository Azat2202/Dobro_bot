from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from database.WeddingDatabseManager import WeddingDatabaseManager


class MessageCounter(BaseMiddleware):
    def __init__(self):
        super(MessageCounter, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        with WeddingDatabaseManager() as db_worker:
            db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                                  message.from_user.last_name)

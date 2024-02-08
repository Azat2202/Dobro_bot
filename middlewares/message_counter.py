from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from database.UsersDatabaseManager import UsersDatabaseManager
from utility import rank_degrees


class MessageCounter(BaseMiddleware):
    def __init__(self):
        super(MessageCounter, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        with UsersDatabaseManager() as db_worker:
            count = db_worker.inc_message(
                message.from_user.id,
                message.chat.id,
                message.from_user.first_name,
                message.from_user.last_name,
            )
            if count in rank_degrees.keys():
                await message.reply(
                    "🎉🎉Поздравляем!🎉🎉\n"
                    f"Теперь вы <b>{rank_degrees.get(count)}!</b>\n"
                    f"Ваше количество сообщений: {count}"
                )

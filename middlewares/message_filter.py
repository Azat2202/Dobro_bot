from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.markdown import quote_html


class MessageFilter(BaseMiddleware):
    def __init__(self):
        super(MessageFilter, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        message.from_user.first_name = quote_html(message.from_user.first_name)
        if message.from_user.last_name:
            message.from_user.last_name = quote_html(message.from_user.last_name)

from aiogram import types
from aiogram.utils import exceptions

from loader import dp


@dp.errors_handler(exception=exceptions.RetryAfter)
async def exception_handler(update: types.Update, exception: exceptions.RetryAfter):
    return True

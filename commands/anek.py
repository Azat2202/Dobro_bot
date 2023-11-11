import requests
from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

from database.WeddingDatabseManager import DatabaseManager
from loader import dp


@dp.message_handler(commands='anek')
async def anek(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        anek_url = 'https://baneks.ru/random'
        response = requests.get(anek_url)
        soup = BeautifulSoup(response.text, 'lxml')
        joke = soup.find('article')
        await message.reply(joke.text)

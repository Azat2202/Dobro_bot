import requests
from aiogram import types
from aiogram.dispatcher import filters
from bs4 import BeautifulSoup

from src.database.DatabseManager import DatabaseManager
from src.main import dp


@dp.message_handler(filters.Text(equals='!Анекдот', ignore_case=True))
@dp.message_handler(commands='anek')
async def anek(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    anek_url = 'https://baneks.ru/random'
    response = requests.get(anek_url)
    soup = BeautifulSoup(response.text, 'lxml')
    joke = soup.find('article')
    await message.reply(joke.text)

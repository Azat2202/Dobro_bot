import requests
from aiogram import types
from bs4 import BeautifulSoup

from loader import dp


@dp.message_handler(commands='anek')
async def anek(message: types.Message):
    anek_url = 'https://baneks.ru/random'
    response = requests.get(anek_url)
    soup = BeautifulSoup(response.text, 'lxml')
    joke = soup.find('article')
    await message.reply(joke.text)

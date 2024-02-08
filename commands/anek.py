import requests
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup

from loader import dp, bot


@dp.message_handler(commands="anek")
async def anek(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(
        InlineKeyboardButton("🔄", callback_data=f"anek_update {message.from_user.id}"),
        InlineKeyboardButton(
            "✅", callback_data=f"remove_markup {message.from_user.id}"
        ),
    )
    anek_url = "https://baneks.ru/random"
    response = requests.get(anek_url)
    soup = BeautifulSoup(response.text, "lxml")
    joke = soup.find("article")
    if by_command:
        await message.reply(joke.text, reply_markup=inline_kb)
    else:
        await bot.edit_message_text(
            joke.text,
            message.chat.id,
            message.message_id,
            reply_markup=message.reply_markup,
        )


@dp.callback_query_handler(lambda c: c.data[:11] == "anek_update")
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await anek(call.message, False)
        await call.answer()

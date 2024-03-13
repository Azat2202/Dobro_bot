import datetime

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from commands.truth_or_dare import get_wish, get_next_day_horo
from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp, bot

last_time_horo = datetime.datetime.now() - datetime.timedelta(days=1)


@dp.message_handler(commands=["wish"])
async def wish(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(
        InlineKeyboardButton("🔄", callback_data=f"wish_update {message.from_user.id}"),
        InlineKeyboardButton(
            "✅", callback_data=f"remove_markup {message.from_user.id}"
        ),
    )
    with UsersDatabaseManager() as db_worker:
        today_horo = get_wish(db_worker.get_users(message.chat.id))
    if by_command:
        out = f"{message.from_user.first_name}{today_horo}"
        await bot.send_message(
            message.chat.id,
            out,
            reply_to_message_id=message.message_id,
            reply_markup=inline_kb,
        )
    else:
        out = f"{message.reply_to_message.from_user.first_name}{today_horo}"
        await bot.edit_message_text(
            out, message.chat.id, message.message_id, reply_markup=message.reply_markup
        )


@dp.callback_query_handler(lambda c: c.data.startswith("wish_update"))
async def wish_callback_handler(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await wish(call.message, False)
        await call.answer()


@dp.message_handler(commands=["horo"])
async def horo(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(
        InlineKeyboardButton("🔄", callback_data=f"horo_update {message.from_user.id}"),
        InlineKeyboardButton(
            "✅", callback_data=f"remove_markup {message.from_user.id}"
        ),
    )
    today_horo = get_next_day_horo()
    if by_command:
        out = f"{message.from_user.first_name}, {today_horo}"
        await bot.send_message(
            message.chat.id,
            out,
            reply_to_message_id=message.message_id,
            reply_markup=inline_kb,
        )
    else:
        out = f"{message.reply_to_message.from_user.first_name}, {today_horo}"
        await bot.edit_message_text(
            out, message.chat.id, message.message_id, reply_markup=message.reply_markup
        )


@dp.callback_query_handler(lambda c: c.data.startswith("horo_update"))
async def horo_callback_handler(call: types.CallbackQuery):

    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await horo(call.message, False)
        await call.answer()

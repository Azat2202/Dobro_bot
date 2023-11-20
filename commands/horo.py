import datetime
from random import choice, randint

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from commands.truth_or_dare import get_wish, get_next_day_horo
from configuration import *
from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp, bot

last_time_horo = datetime.datetime.now() - datetime.timedelta(days=1)


@dp.message_handler(commands=['horo_for_all'])
async def all_horo(message: types.Message):
    global last_time_horo
    with WeddingDatabaseManager() as db_worker:
        users = db_worker.get_users(message.chat.id)
    now_time = datetime.datetime.now()
    delta = now_time - last_time_horo
    out = ''
    if delta.seconds > wait_seconds_for_horo or delta.days > 0:
        last_time_horo = now_time
        for user_id, name, surname in users:
            today_horo = get_wish(users)
            out += f'<b>{name}</b>{today_horo}\n'
        await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id)
    else:
        await bot.send_message(message.chat.id,
                               f'До использования команды заново осталось {(wait_seconds_for_horo - delta.seconds) // 3600} часов')
    await bot.delete_message(message.chat.id, message.message_id)


@dp.message_handler(commands=['horo'])
async def solo_horo(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('🔄', callback_data=f'horo_update {message.from_user.id}'))
    with WeddingDatabaseManager() as db_worker:
        today_horo = get_wish(db_worker.get_users(message.chat.id))
    if by_command:
        out = f'{message.from_user.first_name}{today_horo}'
        await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id,
                               reply_markup=inline_kb)
    else:
        out = f'{message.reply_to_message.from_user.first_name}{today_horo}'
        await bot.edit_message_text(out, message.chat.id, message.message_id, reply_markup=message.reply_markup)


@dp.callback_query_handler(lambda c: c.data[:11] == 'horo_update')
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await solo_horo(call.message, False)
        await call.answer()


@dp.message_handler(filters.Text(equals='!Пожелание', ignore_case=True))
@dp.message_handler(commands=['wish'])
async def solo_wish(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(InlineKeyboardButton('🔄', callback_data=f'solo_wish_update {message.from_user.id}'))
    today_horo = get_next_day_horo()
    if by_command:
        out = f'{message.from_user.first_name}, {today_horo}'
        await bot.send_message(message.chat.id, out, reply_to_message_id=message.message_id, reply_markup=inline_kb)
    else:
        out = f'{message.reply_to_message.from_user.first_name}, {today_horo}'
        await bot.edit_message_text(out, message.chat.id, message.message_id, reply_markup=message.reply_markup)


@dp.callback_query_handler(lambda c: c.data[:16] == 'solo_wish_update')
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await solo_wish(call.message, False)
        await call.answer()

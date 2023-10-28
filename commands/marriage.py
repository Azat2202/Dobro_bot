from datetime import datetime

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import emoji

from commands.inlineKeyboards import form_inline_kb
from database.DatabseManager import DatabaseManager
from database.exceptions import *
from loader import dp
from utility import format_name, beautiful_time_repr


@dp.message_handler(filters.Text(equals='!Брак', ignore_case=True))
@dp.message_handler(commands=['marry'])
async def new_marriage(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        if message.reply_to_message:
            if db_worker.is_married(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Вы уже состоите в браке!')
                return
            elif message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('Вы не можете заключить брак самим с собой!')
                return
            sent_msg = await message.reply(
                emoji.emojize(f'[{format_name(message.from_user.first_name, message.from_user.last_name)}](tg://user?id={message.reply_to_message.from_user.id}), вы '
                              f'согласны заключить брак с [{format_name(message.from_user.first_name, message.from_user.last_name)}](tg://user?id={message.from_user.id})?\n '
                              f'Для заключения брака так же необходимы два свидетеля\n'
                              f'Согласие: :cross_mark:\n'
                              f'Первый свидетель: :cross_mark:\n'
                              f'Второй свидетель: :cross_mark:'), reply_markup=form_inline_kb(), parse_mode='Markdown')
            db_worker.registrate_new_marriage(message.from_user.id,
                                                    message.from_user.first_name,
                                                    message.from_user.last_name,
                                                    message.reply_to_message.from_user.id,
                                                    message.reply_to_message.from_user.first_name,
                                                    message.reply_to_message.from_user.last_name,
                                                    message.chat.id,
                                                    sent_msg.message_id)
        else:
            await message.reply('Чтобы заключить брак вам необходимо ответить командой на сообщение')


@dp.message_handler(filters.Text(equals='!Браки', ignore_case=True))
@dp.message_handler(commands='marriages')
async def marriages_repr(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        data = db_worker.marriages_repr(message.chat.id)
        out = 'Статистика по бракам:\n'
        num = 0
        for line in data:
            user1, user1_name, user1_surname, user2, user2_name, user2_surname,marriage_date = line
            num += 1
            time_obj = datetime.now() - datetime.strptime(marriage_date, "%y-%m-%d %H:%M:%S")
            out += f'{num}. [{format_name(user1_name, user1_surname)}](tg://user?id={user1}) и [{format_name(user2_name, user2_surname)}](tg://user?id={user2}) - {beautiful_time_repr(time_obj)}\n'
            # out += f'   Свидетели: {self.__get_name(line[3])} и {self.__get_name(line[4])}\n'
        out += f'\nВсего {num} браков'
        if num == 0:
            out = 'В этой группе еще нет ни одного брака!'
        await message.reply(out, parse_mode='Markdown')


@dp.message_handler(filters.Text(equals='!Развод', ignore_case=True))
@dp.message_handler(commands='divorce')
async def divorce(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        try:
            db_worker.request_divorce(message.from_user.id, message.chat.id)
            inline_divorce_agreement = InlineKeyboardButton('Да', callback_data=f'divorce {message.chat.id} {message.from_user.id}')
            inline_divorce_refusal = InlineKeyboardButton('Отмена', callback_data=f'not_divorce {message.from_user.id}')
            inline_divorce_kb = InlineKeyboardMarkup().add(inline_divorce_agreement, inline_divorce_refusal)
            await message.reply('Вы уверены что собираетесь развестись?', reply_markup=inline_divorce_kb)
        except WrongUserException:
            await message.reply("Вы еще не состоите в браке!")



@dp.callback_query_handler(lambda c: c.data[:7] == 'divorce')
async def agreed(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        chat_id, user_id = call.data.split()
        if call.from_user.id != user_id:
            await call.answer('Вы не можете подтвердить развод')
            return
        db_worker.del_marriage(chat_id, user_id)
        await call.message.edit_text("Вы развелись")


@dp.callback_query_handler(lambda c: c.data[:11] == 'not_divorce')
async def agreed(call: types.CallbackQuery):
    chat_id, user_id = call.data.split()
    if user_id != call.from_user.id:
        await call.answer('Вы не можете отменить развод!')
        return
    await call.message.edit_text("Развод отменен")
    await call.answer()


@dp.callback_query_handler(lambda c: c.data == 'agreement')
async def agreed(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        try:
            status, user_1, user_2, witness_1, witness_2 = db_worker.marriage_agree(call.from_user.id,
                                                                                    call.message.chat.id,
                                                                                    call.message.message_id)
            if status:
                await call.answer("Поздравляем, вы вступили в брак!")
                await call.message.edit_reply_markup()
                await call.message.edit_text(f"{user_1} и {user_2} вступили в брак!")
            else:
                await call.answer("Поздравляем! Вы согласились на вступление в брак, осталось найти свидетелей")
                await call.message.edit_text(emoji.emojize(
                    f'Для заключения брака так же необходимы два свидетеля\n'
                    f'Согласие: :check_mark_button:\n'
                    f'Первый свидетель: {":check_mark_button:" if witness_1 else ":cross_mark:"}\n'
                    f'Второй свидетель: {":check_mark_button:" if witness_2 else ":cross_mark:"})'),
                    reply_markup=form_inline_kb(agreement=False), parse_mode='Markdown')
        except WrongUserException:
            await call.answer('Вы не можете дать согласие')
        except TimeLimitException:
            await call.answer(emoji.emojize("Прошло слишком много времени, брак заключить нельзя! :alarm_clock:"))
            await call.message.edit_reply_markup()
            await call.message.delete()


@dp.callback_query_handler(lambda c: c.data == 'refusal')
async def refused(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        try:
            user1_id, user1_name, user2_id, user2_name = db_worker.marriage_disagree(call.from_user.id,
                                        call.message.chat.id,
                                        call.message.message_id)
        except WrongUserException:
            await call.answer("Вы не можете развестись!")
            return
        await call.answer("Вы успешно развелись")
        await call.message.edit_reply_markup()
        await call.message.edit_text(
            f"[{user1_name}](tg://user?id={user1_id}) отказал в браке [{user2_name}](tg://user?id={user2_id})",
            parse_mode='Markdown')


@dp.callback_query_handler(lambda c: c.data == 'witness')
async def witness(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        try:
            married, two_witnesses, user1, user1_name, user2, user2_name = db_worker.marriage_witness(call.from_user.id, call.message.chat.id, call.message.message_id)
            await call.answer("Теперь вы свидетель!")
            if not married:
                await call.message.edit_text(emoji.emojize(
                    f'[{user2_name}](tg://user?id={user2}), вы согласны заключить брак с [{user1_name}](tg://user?id={user1})?\n'
                    f'Для заключения брака так же необходимы два свидетеля\n'
                    f'Согласие: {":check_mark_button:" if married else ":cross_mark:"}\n'
                    f'Первый свидетель: ":check_mark_button:"\n'
                    f'Второй свидетель: {":check_mark_button:" if two_witnesses else ":cross_mark"}'),
                    reply_markup=form_inline_kb(agreement=False if married else True),
                    parse_mode='Markdown')
            else:
                await call.message.edit_text(
                    f"Поздравляем молодоженов! [{user1_name}](tg://user?id={user1}) и [{user2}](tg://user?id={user2_name}) теперь в браке!",
                    parse_mode='Markdown')
        except WrongUserException:
                await call.answer('Вы не можете стать свидетелем!')
        except TimeLimitException:
            await call.answer(emoji.emojize("Прошло слишком много времени, брак заключить нельзя! :alarm_clock:"))
            await call.message.edit_reply_markup()
            await call.message.delete()

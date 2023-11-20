from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import emoji

from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp


@dp.message_handler(commands=['adopt'])
async def adopt_command(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        if message.reply_to_message:
            # В дети нельзя брать себя
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('Вы не можете взять в дети себя!')
                return
            # Детей нельзя без партнера
            if not db_worker.is_married(message.from_user.id, message.from_user.id, message.chat.id):
                await message.reply('Вы еще не в браке!')
                return
            # Нельзя брать в дети партнера
            partner_id = db_worker.get_partner(message.from_user.id, message.chat.id)
            if partner_id == message.reply_to_message.from_user.id:
                await message.reply("Нельзя брать в дети партнера!")
                return
            # В дети нельзя чужого ребенка
            if db_worker.is_adopted(message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Это уже чей-то ребенок!')
                return
            # В дети нельзя своих родителей/дедушек итп
            if db_worker.is_ancestor(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Вы не можете брать в дети своих родителей/прародителей итп')
                return
            # В дети нельзя родителей/дедушек итп партнера
            if db_worker.is_ancestor(partner_id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Вы не можете брать в дети родителей/прародителей итп своего партнера')
                return
            inline_child_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Согласен', callback_data=f'child_agreement {message.chat.id} {message.reply_to_message.from_user.id}'),
                InlineKeyboardButton('Не согласен', callback_data=f'child_refusal {message.chat.id} {message.reply_to_message.from_user.id}')
            )
            await message.reply(
                emoji.emojize(
                    f'<a href="tg://user?id={message.reply_to_message.from_user.id}">{message.reply_to_message.from_user.first_name}</a>, вы хотите стать ребенком '
                    f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>?'
                    f':pleading_face::pleading_face::pleading_face:'), reply_markup=inline_child_kb)
        else:
            await message.reply('Чтобы завести детей вам нужно ответить командной на сообщение')


@dp.callback_query_handler(lambda c: c.data[:13] == 'child_refusal')
async def adopt_refusal(call: types.CallbackQuery):
    s, chat_id, user_id = call.data.split()
    if call.from_user.id != int(user_id):
        await call.answer('Вы не можете отказаться')
        return
    await call.message.edit_text(emoji.emojize(f"{call.from_user.first_name} отказал {call.message.reply_to_message.from_user.first_name} :sad_but_relieved_face:"))


@dp.callback_query_handler(lambda c: c.data[:15] == 'child_agreement')
async def adopt_agreed(call: types.CallbackQuery):
    with WeddingDatabaseManager() as db_worker:
        s, chat_id, user_id = call.data.split()
        if call.from_user.id != int(user_id):
            await call.answer('Вы не можете согласиться')
            return
        parent = call.message.reply_to_message.from_user.id
        partner = db_worker.get_partner(parent, call.message.chat.id)
        child = call.from_user.id
        # В дети нельзя чужого ребенка
        if db_worker.is_adopted(child, call.message.chat.id):
            await call.answer('Это уже чей-то ребенок!')
            await call.message.edit_text('Это уже чей-то ребенок!')
            return
        # В дети нельзя своих родителей/дедушек итп
        if db_worker.is_ancestor(parent, child, call.message.chat.id):
            await call.answer('Вы не можете брать в дети своих родителей/прародителей итп')
            await call.message.edit_text('Вы не можете брать в дети своих родителей/прародителей итп')
            return
        # В дети нельзя родителей/дедушек итп партнера
        if db_worker.is_ancestor(partner, child, call.message.chat.id):
            await call.answer('Вы не можете брать в дети родителей/прародителей итп своего партнера')
            await call.message.edit_text('Вы не можете брать в дети родителей/прародителей итп своего партнера')
            return
        db_worker.add_child(call.message.reply_to_message.from_user.id, call.from_user.id, call.message.chat.id)
        await call.message.edit_text(emoji.emojize(
            f"{call.from_user.first_name} теперь ребенок {call.message.reply_to_message.from_user.first_name} !"))


@dp.message_handler(commands=['abandon'])
async def abandon_kid(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        if message.reply_to_message:
            if not db_worker.is_parent(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply("Это не ваш ребенок!")
                return
            inline_abandon_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Хочу',
                                     callback_data=f'abandon_agreement {message.chat.id} {message.reply_to_message.from_user.id} {message.from_user.id}'),
                InlineKeyboardButton('Не хочу',
                                     callback_data=f'abandon_refusal {message.chat.id} {message.reply_to_message.from_user.id} {message.from_user.id}')
            )
            await message.reply("Вы правда хотите выгнать своего ребенка??", reply_markup=inline_abandon_kb)
        else:
            await message.reply("Чтобы отказаться от ребенка напишите /abandon в ответ на сообщение ребенка")


@dp.callback_query_handler(lambda c: c.data[:17] == 'abandon_agreement')
async def abandon_agreed(call: types.CallbackQuery):
    with WeddingDatabaseManager() as db_worker:
        s, chat_id, child_id, parent_id = call.data.split()
        if call.from_user.id != int(parent_id):
            await call.answer('Вы не можете отказаться от ребенка')
            return
        db_worker.remove_child(parent_id, child_id, chat_id)
        await call.message.edit_text("Вы отказались от ребенка(")


@dp.callback_query_handler(lambda c: c.data[:15] == 'abandon_refusal')
async def abandon_refused(call: types.CallbackQuery):
    s, chat_id, child_id, parent_id = call.data.split()
    if call.from_user.id != int(parent_id):
        await call.answer('Вы не можете отказаться')
        return
    await call.message.edit_text(f"{call.from_user.first_name} сохранил ребенка в семье!")


@dp.message_handler(commands=['escape'])
async def escape_kid(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        res = db_worker.get_parent(message.from_user.id, message.chat.id)
        if not res:
            await message.reply("У вас нет родителей!")
            return
        parent_id = res[0]
        inline_abandon_kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton('Хочу',
                                 callback_data=f'escape_agreement {message.chat.id} {message.from_user.id} {parent_id} '),
            InlineKeyboardButton('Не хочу',
                                 callback_data=f'escape_refusal {message.chat.id} {message.from_user.id} {parent_id}')
        )
        await message.reply("Вы правда хотите убежать от родителей??", reply_markup=inline_abandon_kb)


@dp.callback_query_handler(lambda c: c.data[:16] == 'escape_agreement')
async def escape_agreed(call: types.CallbackQuery):
    with WeddingDatabaseManager() as db_worker:
        s, chat_id, child_id, parent_id = call.data.split()
        if call.from_user.id != int(child_id):
            await call.answer('Вы не можете убежать от родителей')
            return
        db_worker.remove_child(parent_id, child_id, chat_id)
        await call.message.edit_text(f"{call.from_user.first_name} убежал от родителей")


@dp.callback_query_handler(lambda c: c.data[:14] == 'escape_refusal')
async def escape_refused(call: types.CallbackQuery):
    s, chat_id, child_id, parent_id = call.data.split()
    if call.from_user.id != int(child_id):
        await call.answer('Вы не можете убежать от родителей')
        return
    await call.message.edit_text(emoji.emojize(f"{call.from_user.first_name} не убежал от родителей)"))


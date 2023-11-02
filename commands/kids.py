from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import emoji

from database.DatabseManager import DatabaseManager
from loader import dp


@dp.message_handler(commands=['adopt'])
async def new_sex(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                              message.from_user.last_name)
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
            if db_worker.is_parent(message.from_user.id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Вы не можете брать в дети своих родителей/прародителей итп')
                return
            # В дети нельзя родителей/дедушек итп партнера
            if db_worker.is_parent(partner_id, message.reply_to_message.from_user.id, message.chat.id):
                await message.reply('Вы не можете брать в дети родителей/прародителей итп своего партнера')
                return
            inline_child_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Согласен', callback_data=f'child_agreement {message.chat.id} {message.reply_to_message.from_user.id}'),
                InlineKeyboardButton('Не согласен', callback_data=f'child_refusal {message.chat.id} {message.reply_to_message.from_user.id}')
            )
            await message.reply(
                emoji.emojize(
                    f'[{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id}), вы хотите стать ребенком '
                    f'[{message.from_user.first_name}](tg://user?id={message.from_user.id})?'
                    f':pleading_face::pleading_face::pleading_face:'), reply_markup=inline_child_kb, parse_mode='Markdown')
        else:
            await message.reply('Чтобы завести детей вам нужно ответить командной на сообщение')


@dp.callback_query_handler(lambda c: c.data[:13] == 'child_refusal')
async def agreed(call: types.CallbackQuery):
    s, chat_id, user_id = call.data.split()
    if call.from_user.id != int(user_id):
        await call.answer('Вы не можете отказаться')
        return
    await call.message.edit_text(emoji.emojize(f"{call.from_user.first_name} отказал {call.message.reply_to_message.from_user.first_name} :sad_but_relieved_face:"))


@dp.callback_query_handler(lambda c: c.data[:15] == 'child_agreement')
async def agreed(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        s, chat_id, user_id = call.data.split()
        if call.from_user.id != int(user_id):
            await call.answer('Вы не можете согласиться')
            return
        # Нельзя брать в дети партнера
        partner_id = db_worker.get_partner(call.message.from_user.id, call.message.chat.id)
        if partner_id == call.message.reply_to_message.from_user.id:
            await call.answer("Нельзя брать в дети партнера!")
            await call.message.edit_text("Нельзя брать в дети партнера!")
            return
        # В дети нельзя чужого ребенка
        if db_worker.is_adopted(call.message.reply_to_message.from_user.id, call.message.chat.id):
            await call.answer('Это уже чей-то ребенок!')
            await call.message.edit_text('Это уже чей-то ребенок!')
            return
        # В дети нельзя своих родителей/дедушек итп
        if db_worker.is_parent(call.message.from_user.id, call.message.reply_to_message.from_user.id, call.message.chat.id):
            await call.answer('Вы не можете брать в дети своих родителей/прародителей итп')
            await call.message.edit_text('Вы не можете брать в дети своих родителей/прародителей итп')
            return
        # В дети нельзя родителей/дедушек итп партнера
        if db_worker.is_parent(partner_id, call.message.reply_to_message.from_user.id, call.message.chat.id):
            await call.answer('Вы не можете брать в дети родителей/прародителей итп своего партнера')
            await call.message.edit_text('Вы не можете брать в дети родителей/прародителей итп своего партнера')
            return
        db_worker.add_child(call.message.reply_to_message.from_user.id, call.from_user.id, call.message.chat.id)
        await call.message.edit_text(emoji.emojize(
            f"{call.from_user.first_name} теперь ребенок {call.message.reply_to_message.from_user.first_name} !"))


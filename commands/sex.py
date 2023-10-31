from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import emoji

from database.DatabseManager import DatabaseManager
from loader import dp
from utility import format_name


@dp.message_handler(commands=['my_sex'])
async def new_sex(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                              message.from_user.last_name)
        every, unique = db_worker.sex_count(message.chat.id, message.from_user.id)
        data = db_worker.get_sex_history(message.chat.id, message.from_user.id)
        if every == 0:
            await message.reply("У вас пока еще не было секса но не отчаивайтесь!")
        else:
            await message.reply(f"Секс у вас был {every} раз с {unique} партнерами\n"
                                f"Наиболее популярные: \n"
                                + "\n".join([f"  - {name} - {count} раз" for u_id, name, count in data]))


@dp.message_handler(filters.Text(equals='!Секс', ignore_case=True))
@dp.message_handler(commands=['sex'])
async def new_sex(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name,
                              message.from_user.last_name)
        if message.reply_to_message:
            if message.reply_to_message.from_user.id == message.from_user.id:
                await message.reply('Вы не можете заняться сексом сами с собой!')
                return
            inline_sex_kb = InlineKeyboardMarkup().add(
                InlineKeyboardButton('Согласен', callback_data=f'sex_agreement {message.chat.id} {message.reply_to_message.from_user.id}'),
                InlineKeyboardButton('Не согласен', callback_data=f'sex_refusal {message.chat.id} {message.reply_to_message.from_user.id}')
            )
            await message.reply(
                emoji.emojize(
                    f'[{message.reply_to_message.from_user.first_name}](tg://user?id={message.reply_to_message.from_user.id}), '
                    f'[{format_name(message.reply_to_message.from_user.first_name, message.reply_to_message.from_user.last_name)}](tg://user?id={message.reply_to_message.from_user.id}) '
                    f'предлагает вам секс! Вы согласны? :pleading_face::pleading_face::pleading_face: '), reply_markup=inline_sex_kb, parse_mode='Markdown')
        else:
            await message.reply('Чтобы заняться сексом вам необходимо ответить командой на сообщение')


@dp.callback_query_handler(lambda c: c.data[:13] == 'sex_agreement')
async def agreed(call: types.CallbackQuery):
    with DatabaseManager() as db_worker:
        s, chat_id, user_id = call.data.split()
        if call.from_user.id != int(user_id):
            await call.answer('Вы не можете подтвердить секс')
            return
        db_worker.add_sex(call.message.reply_to_message.from_user.id, call.from_user.id, call.message.chat.id)
        await call.message.edit_text(emoji.emojize(f"{call.message.reply_to_message.from_user.first_name} и {call.from_user.first_name} занялись "
                                     f"сексом "
                                     f":smiling_face_with_horns::smiling_face_with_horns::smiling_face_with_horns:"))

@dp.callback_query_handler(lambda c: c.data[:11] == 'sex_refusal')
async def agreed(call: types.CallbackQuery):
    s, chat_id, user_id = call.data.split()
    if call.from_user.id != int(user_id):
        await call.answer('Вы не можете отклонить секс')
        return
    await call.message.edit_text(emoji.emojize(f"{call.from_user.first_name} отказал {call.message.reply_to_message.from_user.first_name} :sad_but_relieved_face:"))




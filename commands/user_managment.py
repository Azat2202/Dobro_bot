import datetime

import aiogram.utils.exceptions
from aiogram import types

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp, bot, API_TOKEN, BOT_ID


@dp.message_handler(commands=["whoami"])
async def whoami(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        db_worker.update_user(
            message.chat.id,
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    await message.reply(
        f"Информация о вашем нике обновлена 😎😎!\nТеперь вы {message.from_user.first_name}"
    )


async def myrights(message: types.Message) -> types.chat_member.ChatMember:
    return await bot.get_chat_member(message.chat.id, API_TOKEN.split(":")[0])


mute_list = {
    "час": datetime.timedelta(hours=1),
    "день": datetime.timedelta(days=1),
    "неделя": datetime.timedelta(days=7),
    "месяц": datetime.timedelta(days=31),
    "навсегда": datetime.timedelta(days=367),
}


@dp.message_handler(commands=["mute"])
async def mute(message: types.Message):
    if not (
        await bot.get_chat_member(message.chat.id, message.from_user.id)
    ).is_chat_admin() or (
        message.reply_to_message
        and message.reply_to_message.from_user.id == message.from_user.id
    ):
        await message.reply("Эта команда для админов!☹️")
        return
    if not message.reply_to_message:
        await message.reply("Ответьте сообщением на человека, кого надо замутить🤗")
        return
    if message.reply_to_message.from_user.id == BOT_ID:
        await message.reply("Не надо меня мутить....😌😌😌")
        return
    ban_time = datetime.timedelta(hours=1)
    ban_message = "час"
    command_length = len("/mute ")
    if len(message.text) > command_length and mute_list[message.text[command_length:]]:
        ban_time = mute_list[message.text[command_length:]]
        ban_message = message.text[command_length:]
    await bot.restrict_chat_member(
        message.chat.id,
        message.reply_to_message.from_user.id,
        can_send_messages=False,
        until_date=ban_time,
    )
    await message.reply(f"Этот пользователь замучен на {ban_message} 😇")


# @dp.message_handler(commands=['check_users'])
# async def check_users(message: types.Message):
#     me = await myrights(message)
#     if not me.is_chat_admin():
#         await message.reply("Сделайте меня администратором! Функция недоступна(((🥺🥺🥺")
#         return
#     deleted_users = []
#
#     class UserLeftChat(Exception):
#         pass
#
#     with UsersDatabaseManager() as db_worker:
#         users = db_worker.get_users(message.chat.id)
#         for user_id, name, surname in users:
#             try:
#                 member = await bot.get_chat_member(message.chat.id,
#                                                    user_id)
#                 if member.status == "left":
#                     raise UserLeftChat
#             except (aiogram.utils.exceptions.BadRequest, UserLeftChat):
#                 deleted_users.append(name)
#                 partner = db_worker.get_partner(user_id, message.chat.id)
#                 parent = db_worker.get_parent(user_id, message.chat.id)
#                 children = db_worker.get_children(user_id, message.chat.id)
#                 db_worker.remove_child(parent, user_id, message.chat.id)
#                 db_worker.divorce(user_id, message.chat.id)
#                 db_worker.remove_user(user_id, message.chat.id)
#                 if partner:
#                     db_worker.move_child(user_id, partner, message.chat.id)
#                 elif parent:
#                     db_worker.move_child(user_id, parent, message.chat.id)
#                 else:
#                     for child in children:
#                         db_worker.remove_child(user_id, child, message.chat.id)
#     await message.reply(
#         "Из чата удалены следующие участники: \n" + "\n".join(deleted_users)
#     )

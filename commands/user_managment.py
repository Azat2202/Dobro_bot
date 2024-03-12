import aiogram.utils.exceptions
from aiogram import types

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp, bot, API_TOKEN


@dp.message_handler(commands=["whoami"])
async def whoami(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        db_worker.update_user(
            message.chat.id,
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.last_name,
        )
    await message.reply("Информация о вашем нике обновлена 😎😎!")


async def myrights(message: types.Message) -> types.chat_member.ChatMember:
    return await bot.get_chat_member(message.chat.id, API_TOKEN.split(":")[0])


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

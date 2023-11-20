from aiogram import types

from database.WeddingDatabseManager import WeddingDatabaseManager
from loader import dp


@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER])
async def user_left_chat(message: types.Message):
    with WeddingDatabaseManager() as db_worker:
        partner = db_worker.get_partner(message.left_chat_member.id, message.chat.id)
        if partner:
            db_worker.move_child(message.left_chat_member.id, partner, message.chat.id)
            main_message = "Все дети были переданы партнеру!"
        else:
            parent = db_worker.get_parent(message.left_chat_member.id, message.chat.id)
            if parent:
                db_worker.move_child(message.left_chat_member.id, parent, message.chat.id)
                main_message = "Все дети были переданы дедушкам и бабушкам!"
            else:
                children = db_worker.get_children(message.left_chat_member.id, message.chat.id)
                for child in children:
                    db_worker.remove_child(message.left_chat_member.id, child, message.chat.id)
                main_message = "Все дети оказались в детдоме(!"
        db_worker.divorce(message.left_chat_member.id, message.chat.id)
    await message.reply(f"Прощайте, {message.left_chat_member.first_name}\n" + main_message + "\nВы разведены!")

from datetime import datetime

from loader import bot
from database.SettingsDatabaseManager import SettingsDatabaseManager
from database.UsersDatabaseManager import UsersDatabaseManager


async def create_poll():
    with SettingsDatabaseManager() as settings_db_worker:
        with UsersDatabaseManager() as users_db_worker:
            for data in settings_db_worker.get_mailing_chats():
                try:
                    created_poll = await bot.send_poll(
                        data[0],
                        question="настроение сегодня",
                        options=["+++😇", "++-🥹", "+--🥲", "---😵‍💫"],
                        is_anonymous=False,
                    )
                    last_poll = users_db_worker.get_last_poll(created_poll.chat.id)
                    users_db_worker.add_poll(
                        created_poll.chat.id,
                        created_poll.poll.id,
                        datetime.now().strftime("%d.%m.%y"),
                        created_poll.message_id,
                    )
                    await bot.pin_chat_message(
                        created_poll.chat.id,
                        created_poll.message_id,
                        disable_notification=True,
                    )
                    if last_poll:
                        await bot.stop_poll(created_poll.chat.id, last_poll[0])
                        await bot.unpin_chat_message(created_poll.chat.id, last_poll[0])
                except Exception as e:
                    pass

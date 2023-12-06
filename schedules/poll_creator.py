from datetime import datetime

from loader import bot
from database.SettingsDatabaseManager import SettingsDatabaseManager
from database.UsersDatabaseManager import UsersDatabaseManager


async def create_poll():
    with SettingsDatabaseManager() as settings_db_worker:
        with UsersDatabaseManager() as users_db_worker:
            for data in settings_db_worker.get_mailing_chats():
                created_poll = await bot.send_poll(data[0], question='настроение сегодня',
                                          options=['+++😇', '++-🥹', '+--🥲', '---😵‍💫'],
                                          is_anonymous=False)
                users_db_worker.add_poll(created_poll.chat.id, created_poll.poll.id, datetime.now().strftime("%d.%m"))

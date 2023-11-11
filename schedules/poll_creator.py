from loader import bot
from database.SettingsDatabaseManager import SettingsDatabaseManager


async def create_poll():
    with SettingsDatabaseManager() as db_worker:
        for data in db_worker.get_mailing_chats():
            await bot.send_poll(data[0], question='настроение сегодня',
                                      options=['+++😇', '++-🥹', '+--🥲', '---😵‍💫'],
                                      is_anonymous=False)

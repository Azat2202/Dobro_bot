import datetime

from aiogram import Bot, Dispatcher, executor

from configuration import *
from database.DatabseManager import DatabaseManager
from get_users import users
import commands
import database
from loader import dp

last_time_banned = datetime.datetime.now() - datetime.timedelta(seconds=wait_seconds)
last_time_mentioned = datetime.datetime.now() - datetime.timedelta(seconds=wait_seconds_for_mention)
massive = [1 for i in users]

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=print("Server started"))

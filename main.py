import asyncio

from loader import dp
import datetime
from aiogram import executor
from configuration import *
import database
import commands
import schedules
import errors
from schedules.poll_creator import create_poll

last_time_banned = datetime.datetime.now() - datetime.timedelta(seconds=wait_seconds)
last_time_mentioned = datetime.datetime.now() - datetime.timedelta(
    seconds=wait_seconds_for_mention
)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=print("Server started"))

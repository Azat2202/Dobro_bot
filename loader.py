from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from configuration import API_TOKEN

bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

scheduler = AsyncIOScheduler()

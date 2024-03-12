import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from middlewares.gpio import GPIOBlinker
from middlewares.message_counter import MessageCounter
from middlewares.message_filter import MessageFilter

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(MessageCounter())
dp.middleware.setup(MessageFilter())
dp.middleware.setup(GPIOBlinker())

from schedules.poll_creator import *

scheduler = AsyncIOScheduler()
scheduler.add_job(create_poll, "cron", day_of_week="*", hour=19, minute=00, second=0)
scheduler.start()

# model_name = 'Skoltech/russian-inappropriate-messages'
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = BertForSequenceClassification.from_pretrained(model_name);

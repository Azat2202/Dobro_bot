import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

from schedules.poll_creator import *
scheduler = AsyncIOScheduler()
scheduler.add_job(create_poll, 'cron', day_of_week='*', hour=19, minute=00, second=0)
scheduler.start()

# model_name = 'Skoltech/russian-inappropriate-messages'
# tokenizer = BertTokenizer.from_pretrained(model_name)
# model = BertForSequenceClassification.from_pretrained(model_name);

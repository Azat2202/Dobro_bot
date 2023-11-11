from random import randint, choice

from aiogram import types
from aiogram.dispatcher import filters

from commands.truth_or_dare import get_dare, get_truth
from database.WeddingDatabseManager import DatabaseManager
from loader import dp, bot


@dp.message_handler(commands='help')
async def help_(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply("""
Список всех доступных команд:
/start - инициализация чата
/help - вывести справку по всем командам
/marry - заключить брак с человеком из чата
/divorce - развестись
/marriages - показать текущие браки
/sex - заняться сексом с участником чата
/my_sex - получить историю половых связей
/adopt - приютить ребенка
/abandon - отказаться от ребенка
/escape - убежать от родителей
/family - семейное древо чата
/anek - отправить случайный анекдот
/horo - получить индивидуальный гороскоп
/horo_for_all - отправить гороскоп для всех
/wish - получить пожелание на следующий день
/truth - получить задание правды
/dare - получить задание действие
/mark_all - отметить всех участников
/top_spamers  - топ участников по сообщениям
/top_karma - топ учатников по карме
Важный вопрос ... - Задать важный вопрос
Вопрос ... - Задать вопрос да/нет
Совместимость ... - Узнать свою совместимость с человеком
добряш или плюс или Спасибо - Повысить карму 
минус или токс - Понизить карму
Настройки:
/poll_creation - отправка ежедневных опросов настроения""")


@dp.message_handler(filters.Text(startswith='Совместимость', ignore_case=True))
async def connection(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply(f'Ты и {message.text[14::]} вместе с шансом {randint(0, 100)}%')


@dp.message_handler(filters.Text(startswith='Вопрос', ignore_case=True))
async def yn(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply(choice(['Да', "Нет"]))


@dp.message_handler(commands='truth')
async def yn(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply(get_truth())


@dp.message_handler(commands='dare')
async def yn(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply(get_dare())

@dp.message_handler(filters.Text(startswith='Важный вопрос', ignore_case=True))
async def yn(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    await message.reply(choice(['Да', "Нет", "Это не важно", "Успокойся", "Не спрашивай такое", "Да, хотя зря",
                                "Никогда", "100%", "1 из 100", "Спроси еще раз"]))


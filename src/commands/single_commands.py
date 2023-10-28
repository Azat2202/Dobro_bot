from random import randint, choice

from aiogram import types
from aiogram.dispatcher import filters

from src.commands.truth_or_dare import get_action, get_true
from src.database.DatabseManager import DatabaseManager
from src.main import dp


@dp.message_handler(filters.Text(equals='!Помощь', ignore_case=True))
@dp.message_handler(commands='help')
async def help_(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply('Список всех доступных команд:\n'
                        '/marry или !Брак - Заключить брак с человеком из чата\n'
                        '/divorce или !Развод - Развестись\n'
                        '/marriages или !Браки - Показать текущие браки\n'
                        '/anek или !Анекдот - Отправить случайный анекдот\n'
                        'Важный вопрос ... - Задать важный вопрос\n'
                        'Вопрос ... - Задать вопрос да/нет\n'
                        'Совместимость ... - Узнать свою совместимость с человеком\n'
                        '/horo или !Гороскоп - Получить индивидуальный гороскоп\n'
                        '/horo_for_all - Отправить гороскоп для всех\n'
                        '/mark_all или !Сбор - Отметить всех участников\n'
                        'добряш или плюс или Спасибо - Повысить карму \n'
                        'минус или токс - Понизить карму\n'
                        '/top_spamers или !Спамеры - Топ участников по сообщениям\n'
                        '/top_karma или !Карма - Топ учатников по карме')


@dp.message_handler(filters.Text(startswith='Совместимость', ignore_case=True))
async def connection(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(f'Ты и {message.text[14::]} вместе с шансом {randint(0, 100)}%')


@dp.message_handler(filters.Text(startswith='Вопрос', ignore_case=True))
async def yn(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(choice(['Да', "Нет"]))


@dp.message_handler(commands='truth')
@dp.message_handler(filters.Text(startswith='!Правда', ignore_case=True))
async def yn(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(get_true())


@dp.message_handler(filters.Text(startswith='!Действие', ignore_case=True))
@dp.message_handler(commands='dare')
async def yn(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(get_action())

@dp.message_handler(filters.Text(startswith='Важный вопрос', ignore_case=True))
async def yn(message: types.Message):
    db_worker = DatabaseManager()
    db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    db_worker.close()
    await message.reply(choice(['Да', "Нет", "Это не важно", "Успокойся", "Не спрашивай такое", "Да, хотя зря",
                                "Никогда", "100%", "1 из 100", "Спроси еще раз"]))


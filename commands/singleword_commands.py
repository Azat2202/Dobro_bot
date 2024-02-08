from random import randint, choice

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from commands.truth_or_dare import get_dare, get_truth
from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp, bot


@dp.message_handler(commands="help")
async def help_(message: types.Message):
    await message.reply(
        """
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
/my_mood - график моего настроения
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
/settings_poll_creation - отправка ежедневных опросов настроения"""
    )


@dp.message_handler(filters.Text(startswith="Совместимость", ignore_case=True))
async def connection(message: types.Message):
    await message.reply(f"Ты и {message.text[14::]} вместе с шансом {randint(0, 100)}%")


@dp.message_handler(filters.Text(startswith="Вопрос", ignore_case=True))
async def yn(message: types.Message):
    await message.reply(choice(["Да", "Нет"]))


@dp.message_handler(commands="truth")
async def truth(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(
        InlineKeyboardButton(
            "🔄", callback_data=f"truth_update {message.from_user.id}"
        ),
        InlineKeyboardButton(
            "✅", callback_data=f"remove_markup {message.from_user.id}"
        ),
    )
    if by_command:
        await message.reply(get_truth(), reply_markup=inline_kb)
    else:
        await bot.edit_message_text(
            get_truth(),
            message.chat.id,
            message.message_id,
            reply_markup=message.reply_markup,
        )


@dp.callback_query_handler(lambda c: c.data[:12] == "truth_update")
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await truth(call.message, False)
        await call.answer()


@dp.callback_query_handler(lambda c: c.data[:13] == "remove_markup")
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете подтвердить выбор!")
    else:
        await call.message.edit_reply_markup(reply_markup=None)
        await call.answer()


@dp.message_handler(commands="dare")
async def dare(message: types.Message, by_command=True):
    inline_kb = InlineKeyboardMarkup()
    inline_kb.add(
        InlineKeyboardButton("🔄", callback_data=f"dare_update {message.from_user.id}"),
        InlineKeyboardButton(
            "✅", callback_data=f"remove_markup {message.from_user.id}"
        ),
    )
    if by_command:
        await message.reply(get_dare(), reply_markup=inline_kb)
    else:
        await bot.edit_message_text(
            get_dare(),
            message.chat.id,
            message.message_id,
            reply_markup=message.reply_markup,
        )


@dp.callback_query_handler(lambda c: c.data[:11] == "dare_update")
async def marriage_refused(call: types.CallbackQuery):
    if call.from_user.id != int(call.data.split()[1]):
        await call.answer("Вы не можете обновить!")
    else:
        await dare(call.message, False)
        await call.answer()


@dp.message_handler(filters.Text(startswith="Важный вопрос", ignore_case=True))
async def yn_important(message: types.Message):
    await message.reply(
        choice(
            [
                "Да",
                "Нет",
                "Это не важно",
                "Успокойся",
                "Не спрашивай такое",
                "Да, хотя зря",
                "Никогда",
                "100%",
                "1 из 100",
                "Спроси еще раз",
            ]
        )
    )

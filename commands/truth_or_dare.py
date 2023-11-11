from random import choice, randint
from database.WishesDatabaseManager import WishesDatabaseManager


def get_wish(users):
    friendly_adj = ["хороший", "добрый", "ахуенный", "пиздатый", "веселый", "успешный", "обычный", "стабильный",
                    "душевный", "радостный", "уютный", "позитивный", "вдохновляющий", "оптимистичный",
                    "жизнерадостный", "щедрый", "теплый", "солнечный", "счастливый",
                    ]
    return choice([f', у тебя будет {choice(friendly_adj)} день',
                   f', cегодня ты найдешь {choice(users)[1]} в своей комнате',
                   f', cегодня ты найдешь {choice(users)[1]} в своем шкафу',
                   f', ты сделаешь что-то очень важное и полезное для людей',
                   f', тебя любит {choice(users)[1]}',
                   f', ты встретишь свою вторую половинку ({choice(users)[1]})',
                   f', ты сделаешь что-то, что никогда раньше не делал',
                   f', ты получишь хорошие новости от {choice(users)[1]}',
                   f', cегодня ты получишь неожиданный звонок от {choice(users)[1]}',
                   f', Ты найдешь деньги на улице.',
                   f', Ты получишь приглашение на интересное мероприятие от {choice(users)[1]}',
                   f', Сегодня ты получишь пятерку по любимому предмету.',
                   f', Ты получишь приглашение на интересное мероприятие от {choice(users)[1]}',
                   f', сегодня ты ляжешь спать раньше {randint(0, 5)}',
                   f', ты {choice(["сдашь", "не сдашь"])} кр по {choice(["матану", "дму", "линалу", "пг"])}',
                   f', ты {choice(["сдашь", "не сдашь"])} лабу по {choice(["информатике", "проге", "опд", "япам", "вебу", "бд"])}',
                   f', сегодня {choice(users)[1]} {choice(["не назовет", "назовет"])} тебя добрым',
                   f', {choice(users)[1]} тебе купит покушать',
                   f', тебе {choice(["", "не "])}купит одноразку {choice(users)[1]}',
                   f', ты завтра {choice(["", "не "])}пойдешь ко второй паре',
                   f', ты выпьешь пива с {choice(users)[1]}',
                   f', ты найдешь решение для сложной проблемы.'
                   ])


def get_next_day_horo():
    with WishesDatabaseManager() as db_worker:
        return db_worker.get_wish()


def get_dare():
    with WishesDatabaseManager() as db_worker:
        return db_worker.get_dare()


def get_truth():
    with WishesDatabaseManager() as db_worker:
        return db_worker.get_truth()

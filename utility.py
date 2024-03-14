import os

spam_degrees = {
    0: "новичок", 
    250: "тихоня",
    1000: "обычный участник",
    5_000: "небольшой спамер",  
    10_000: "активный спамер", 
    50_000: "главный спамер", 
}

karma_degrees = {
    -100: "токс",
    -50: "злой",
    -10: "злюка",
    0: "недоброжелательный",
    10: "добрый",
    25: "очень добрый",
    50: "добряш",
    100: "главный добряш",
    1000: "святой",
}


def get_spammer_rank(count: int):
    rank = ""
    for c, r in spam_degrees.items():
        if count < c:
            rank = r
            break
    return rank


def get_karma_rank(karma: int):
    rank = ""
    for c, r in karma_degrees.items():
        if karma < c:
            rank = r
            break
    return rank


def format_name(name, surname):
    return f"{name}{' ' + surname if surname else ''}"


def beautiful_time_repr(time_):
    if time_.days > 365:
        return f"{time_.days // 365} лет и {time_.days % 365} дней"
    if time_.days > 0:
        if time_.days == 1:
            return f"{time_.days} день"
        elif 1 < time_.days <= 4:
            return f"{time_.days} дня"
        else:
            return f"{time_.days} дней"
    if time_.seconds > 3601:
        if time_.seconds // 3601 == 1:
            return f"{time_.seconds // 3601} час"
        elif 1 < time_.days // 3601 <= 4:
            return f"{time_.seconds // 3601} часа"
        else:
            return f"{time_.seconds // 3601} часов"
    if time_.seconds > 60:
        if time_.seconds // 60 == 1:
            return f"{time_.seconds // 60} минута"
        elif 1 < time_.days // 60 <= 4:
            return f"{time_.seconds // 60} минуты"
        else:
            return f"{time_.seconds // 60} минут"
    return f"{time_.seconds} секунд"


emoji_font = "NotoEmoji-Medium.ttf"
font_path = os.path.join(os.path.join(os.getcwd(), "fonts"))
emoji_font_path = os.path.join(os.path.join(os.getcwd(), "fonts", emoji_font))

def format_name(name, surname):
    return f"{name}{' ' + surname if surname else ''}"


def beautiful_time_repr(time_):
    if time_.days > 365:
        return f'{time_.days // 365} лет и {time_.days % 365} дней'
    if time_.days > 0:
        return f'{time_.days} дней'
    if time_.seconds > 3601:
        return f'{time_.seconds // 3601} часов'
    if time_.seconds > 60:
        return f'{time_.seconds // 60} минут'
    return f'{time_.seconds} секунд'

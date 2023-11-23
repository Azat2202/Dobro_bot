from io import BytesIO

import seaborn as sns
from aiogram import types
from matplotlib import pyplot as plt
from pandas import DataFrame

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp


def create_graph(user_id: int, chat_id: int, user_name: str) -> BytesIO | None:
    with UsersDatabaseManager() as db_worker:
        data = db_worker.get_user_mood(user_id, chat_id)
    if not data:
        return None
    sns.set_theme(style="ticks")
    sns.set_context("notebook", font_scale=.9, rc={"grid.linewidth": 1})
    plt.rcParams['font.family'] = 'Arial'
    x, y_user, y_avg = zip(*data)
    df_user = DataFrame({'x': x, 'y': y_user})
    df_avg = DataFrame({'x': x, 'y': y_avg})
    sns.lineplot(x='x', y='y', data=df_user, label=user_name)
    plot = sns.lineplot(x='x', y='y', data=df_avg, label="среднее значение")
    plot.set(xlabel=None)
    plot.set(ylabel=None)
    plt.xticks(rotation=80)
    plot.lines[1].set_linestyle("--")
    plt.title(f"Настроение {user_name}", fontdict={'fontsize': 18})
    plt.yticks([0, 1, 2, 3], ["---", "+--", "++-", "+++"], size=18)
    buffer = BytesIO()
    plot.figure.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    return buffer


@dp.message_handler(commands='my_mood')
async def my_mood(message: types.Message):
    bytes = create_graph(message.from_user.id, message.chat.id, message.from_user.first_name)
    if not bytes:
        await message.reply("Вы еще не голосовали в опросах(")
        return
    await message.reply_photo(bytes)
    bytes.close()

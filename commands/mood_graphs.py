import datetime
import os

import seaborn as sns
from aiogram import types
from matplotlib import pyplot as plt, font_manager
from pandas import DataFrame

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp
from utility import emoji_font_path, emoji_font

font_manager.fontManager.addfont(emoji_font_path)


def create_graph(user_id: int, chat_id: int, user_name: str) -> bool:
    with UsersDatabaseManager() as db_worker:
        data = db_worker.get_user_mood(user_id, chat_id)
    if not data or len(data) == 1:
        return False
    user_name = user_name.replace(r"$", r"\$")
    x, y_user, y_avg = zip(*data)
    sns.set_theme(style="ticks")
    sns.set_context("paper", font_scale=0.7, rc={"grid.linewidth": 1})
    df_user = DataFrame({"x": x, "y": y_user})
    df_avg = DataFrame({"x": x, "y": y_avg})
    sns.lineplot(x="x", y="y", data=df_user, label=user_name)
    plot = sns.lineplot(x="x", y="y", data=df_avg, label="среднее значение")
    for i, date in enumerate(x):
        day, month, year = date.split(".")
        if datetime.datetime(int(year), int(month), int(day)).weekday() == 0:
            plt.plot(x[i], y_user[i], marker="o", color="blue")
    plot.set(xlabel=None)
    plot.set(ylabel=None)
    plt.xticks(rotation=80)
    plot.lines[1].set_linestyle("--")
    plt.title(
        rf"Настроение {user_name}", fontdict={"fontsize": 18}, fontname=emoji_font
    )
    plt.yticks([0, 1, 2, 3], ["---", "+--", "++-", "+++"], size=18)
    plot.figure.savefig(os.path.join("graphs", f"mood_{user_id}_{chat_id}.png"))
    plt.close()
    return True


@dp.message_handler(commands="my_mood")
async def my_mood(message: types.Message):
    if not create_graph(
        message.from_user.id, message.chat.id, message.from_user.first_name
    ):
        await message.reply("Вы еще не голосовали в опросах(")
        return
    path = os.path.join("graphs", f"mood_{message.from_user.id}_{message.chat.id}.png")
    with open(path, "rb") as inp_f:
        await message.reply_photo(inp_f)
    # os.remove(path)

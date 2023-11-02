import os

from aiogram import types
from aiogram.dispatcher import filters
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.utils import emoji

from database.DatabseManager import DatabaseManager
from loader import dp
from graphviz import Graph


@dp.message_handler(commands=['family'])
async def family_repr(message: types.Message):
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
        edges = db_worker.get_edges(message.chat.id)
        marriages = [[data[1], data[3]] for data in db_worker.marriages_repr(message.chat.id)]
        nodes = [item for sublist in marriages for item in sublist] + [item for sublist in edges for item in sublist]
        make_graph(nodes, edges, marriages, message.chat.full_name, f"for_{message.from_user.id}")
        await message.reply_photo(InputFile(os.path.join("graphs", f"for_{message.from_user.id}.png")))
        os.remove(os.path.join("graphs", f"for_{message.from_user.id}"))
        os.remove(os.path.join("graphs", f"for_{message.from_user.id}.png"))


def make_graph(nodes, edges, marriages, chat_name, id: str):
    f = Graph('neato', format='pdf', encoding='utf8',
              filename='fam', node_attr={'style': 'filled,rounded',
                                              'color': 'black',
                                              'fillcolor': 'lightblue2'})
    f.attr('node', shape='box')
    f.attr(label=f'{chat_name}\r\n')
    f.attr(labelloc='t')
    f.attr(fontsize='12')
    f.attr(fontname='Arial')
    for n, k in enumerate(marriages):
        i, j = k
        c = Graph(f'child{n}')
        c.attr(color='blue')
        c.attr(rank='same')
        c.node(i)
        c.node(j)
        c.edge(i, j, _attributes={'color': 'black:black'})
        f.subgraph(c)
    for nod in nodes:
        if all(nod not in sublist for sublist in marriages):
            f.node(nod, label=nod)
    for i, j in edges:
        f.edge(i, j, label='')
    f.render(os.path.join('graphs', id), format='png', view=False)
import os
from dataclasses import dataclass

from aiogram import types
from graphviz import Graph

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp


@dataclass
class User:
    id: int
    name: str


@dp.message_handler(commands=['family'])
async def family_repr(message: types.Message):
    with UsersDatabaseManager() as db_worker:
        edges = [[User(data[0], data[1]), User(data[2], data[3])] for data in db_worker.get_edges(message.chat.id)]
        marriages = [[User(data[0], data[1]), User(data[2], data[3])] for data in db_worker.get_marriages(message.chat.id)]
        nodes = [item for sublist in marriages for item in sublist] + [item for sublist in edges for item in sublist]
        make_graph(nodes, edges, marriages, message.chat.full_name, f"for_{message.from_user.id}")
        with open(os.path.join("..", "graphs", f"for_{message.from_user.id}.png"), 'rb') as inp_f:
            await message.reply_photo(inp_f)
        os.remove(os.path.join("..", "graphs", f"for_{message.from_user.id}"))
        os.remove(os.path.join("..", "graphs", f"for_{message.from_user.id}.png"))


def make_graph(nodes, edges, marriages, chat_name, id: str):
    f = Graph('dot', format='pdf', encoding='utf8', engine="dot",
              filename='fam',
              node_attr={'style': 'filled,rounded',
                         'color': 'black',
                         'fillcolor': 'lightblue2'
                         },
              graph_attr={
                  'bgcolor': '#EEEEEE'
              })
    f.attr('node', shape='box')
    f.attr(label=f'{chat_name}')
    f.attr(labelloc='t')
    f.attr(fontname='Tahoma')
    f.attr(ranksep='0.65')
    for n, k in enumerate(marriages):
        user_1: User
        user_2: User
        user_1, user_2 = k
        c = Graph(f'parents{n}')
        c.attr(color='blue')
        c.attr(rank='same')
        c.attr(cluster='true')
        c.attr(peripheries='0')
        c.attr(label="")
        c.node(str(user_1), label=user_1.name,
               _attributes={'fillcolor': '#99B2DD' if len(user_1.name) % 2 == 0 else '#E9AFA3'})
        c.node(str(user_2), label=user_2.name,
               _attributes={'fillcolor': '#E9AFA3' if len(user_1.name) % 2 == 0 else '#99B2DD'})
        c.edge(str(user_1), str(user_2), _attributes={'color': 'black:black', 'constraint': 'false'})
        f.subgraph(c)
    for nod in nodes:
        if all(nod not in sublist for sublist in marriages):
            f.node(str(nod), label=nod.name, _attributes={'fillcolor': '#99B2DD'})
    for i, j in edges:
        f.edge(str(i), str(j), label='')
    f.render(os.path.join('..','graphs', id), format='png', view=False)


if __name__ == '__main__':
    with UsersDatabaseManager() as db_worker:
        edges = [[User(data[0], data[1]), User(data[2], data[3])] for data in db_worker.get_edges(-1001819892143)]
        marriages = [[User(data[0], data[1]), User(data[2], data[3])] for data in
                     db_worker.get_marriages(-1001819892143)]
        nodes = [item for sublist in marriages for item in sublist] + [item for sublist in edges for item in sublist]
        make_graph(nodes, edges, marriages, "VT FLOOD FRIENDLY", "1")

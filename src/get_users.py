from telethon import TelegramClient, events, sync
from dataclasses import dataclass, field
import sys
import os
import time

API_TOKEN_TELETHON = os.environ.get("API_TOKEN_TELETHON")
users = []
channel_id = -1001819892143


@dataclass(order=True)
class user:
    user_id: int
    name: str
    surname: str
    username: str


def get_env(name, message, cast=str):
    if name in os.environ:
        return os.environ[name]
    while True:
        value = input(message)
        try:
            return cast(value)
        except ValueError as e:
            print(e, file=sys.stderr)
            time.sleep(1)


api_id = int(os.environ.get("api_id"))
api_hash = os.environ.get("api_hash")
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=API_TOKEN_TELETHON)
client.start()
count = 0
for participant in client.get_participants(channel_id):
    if not participant.bot:
        users.append(user(participant.id, participant.first_name, participant.last_name, participant.username))
# for participant in client.iter_participants(channel_id, aggressive=True):
#     users.append(user(participant.id, participant.first_name, participant.last_name))
client.disconnect()
users.sort()
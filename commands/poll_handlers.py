from aiogram import types

from database.UsersDatabaseManager import UsersDatabaseManager
from loader import dp


@dp.poll_answer_handler()
async def mood_poll_answer(poll_answer: types.PollAnswer):
    with UsersDatabaseManager() as db_worker:
        if len(poll_answer.option_ids) != 0:
            db_worker.add_poll_answer(poll_answer.user.id, poll_answer.poll_id, poll_answer.option_ids[0])
        else:
            db_worker.remove_poll_anser(poll_answer.user.id, poll_answer.poll_id)

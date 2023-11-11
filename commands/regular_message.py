import datetime

import torch
from aiogram import types

from database.WeddingDatabseManager import DatabaseManager
from loader import dp


@dp.message_handler()
async def common_message(message: types.Message):
    startTime = datetime.datetime.now()
    with DatabaseManager() as db_worker:
        db_worker.inc_message(message.from_user.id, message.chat.id, message.from_user.first_name, message.from_user.last_name)
    # tokenized = tokenizer.batch_encode_plus([message.text], max_length=512, pad_to_max_length=True, truncation=True,
    #                                         return_token_type_ids=False)
    # tokens_ids, mask = torch.tensor(tokenized['input_ids']), torch.tensor(tokenized['attention_mask'])
    # with torch.no_grad():
    #     model_output = model(tokens_ids, mask)
    #     scores = model_output['logits'].softmax(dim=1).detach().numpy()[0]

    # await message.reply(f"Доброты: {scores[0]} \n"
    #                          f"Зла: {scores[1]}")
    # if scores[1] > 0.999:
    #     await message.reply("Ваше сообщение очень агрессивное, ваша карма уменьшена")
    #     with DatabaseManager() as db_worker:
    #         db_worker.dec_karma(message.from_user.id, message.chat.id)
    # if scores[1] > 0.99:
    #     await message.reply("Ваше сообщение выглядит достаточно агрессивно, пожалуйста, будь добрее")
    # print((datetime.datetime.now() - startTime))

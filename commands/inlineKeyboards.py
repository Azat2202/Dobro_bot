from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



def form_inline_kb(agreement: bool = True, witness: bool = True) -> types.InlineKeyboardMarkup:
    inline_wedding_agreement = InlineKeyboardButton('Согласен', callback_data='agreement')
    inline_wedding_refusal = InlineKeyboardButton('Не согласен', callback_data='refusal')
    inline_wedding_witness = InlineKeyboardButton('Я свидетель', callback_data='witness')
    inline_wedding_kb = InlineKeyboardMarkup()
    if agreement:
        inline_wedding_kb.add(inline_wedding_agreement, inline_wedding_refusal)
    if witness:
        inline_wedding_kb.add(inline_wedding_witness)
    return inline_wedding_kb

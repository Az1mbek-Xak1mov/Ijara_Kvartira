from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def make_inline_btn(btns, sizes):
    builder = InlineKeyboardBuilder()
    for text in btns:
        builder.add(InlineKeyboardButton(text=text, callback_data=text))  # important!
    builder.adjust(*sizes)
    return builder.as_markup()

def make_inline_btn_confirm(btns, sizes,chat_id):
    builder = InlineKeyboardBuilder()
    for text in btns:
        builder.add(InlineKeyboardButton(text=text, callback_data=f"{text}_{str(chat_id)}"))  # important!
    builder.adjust(*sizes)
    return builder.as_markup()

def make_inline_btn_like(btns, sizes,id):
    builder = InlineKeyboardBuilder()
    for text in btns:
        builder.add(InlineKeyboardButton(text=text, callback_data=f"Liked_{id}"))
    builder.adjust(*sizes)
    return builder.as_markup()
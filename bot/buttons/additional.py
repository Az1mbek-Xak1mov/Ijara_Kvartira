from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def contact_request_btn():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Nomerni ulashing", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb
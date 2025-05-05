#Asking contact owner
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy import text
from sqlalchemy.orm import Session

from bot.buttons.additional import contact_request_btn
from bot.buttons.reply import *
from bot.buttons.inline import *
from bot.dispatcher import dp
from bot.states import *
from db.engine import engine
from db.models import Owner
from db.engine import SessionLocal
from db.manager import *

db = SessionLocal()

@dp.callback_query(StepByStepStates.start, F.data == "Ijaraga beruvchi")
@dp.callback_query(F.data == "Ijaraga beruvchi")
async def name_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(RoleState.role)
    await state.update_data({"role": "owner"})
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM owners WHERE chat_id = :chat_id"), {"chat_id": callback.from_user.id}).fetchone()
    if result:
        await state.set_state(StepByStepStates.main)
        btns = [
            "🏠 Kvartira Joylash",
            "📋 Mening Kvartiralarim",
            "⚙️ Sozlamalar",
            "🔙 Orqaga"
        ]
        await callback.answer()
        await callback.message.edit_text(
            text=f"Hush kelisbz {callback.from_user.full_name}",
            reply_markup=None
        )
        sizes = [1, 2, 1]
        markup = make_reply_btn(btns, sizes)
        await callback.message.answer("Asosiy Panel", reply_markup=markup)
        return
    else:
        user = callback.from_user
        chat_id = user.id
        fullname = user.full_name
        await state.update_data({"fullname": fullname,"chat_id":chat_id})
        await state.set_state(OwnerState.phone_number)
        await (callback.message.reply("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=contact_request_btn()))

#Main panel
@dp.message(OwnerState.phone_number)
async def name_handler(message: Message, state: FSMContext):
    phone_number = message.contact.phone_number
    await state.update_data({"phone_number": phone_number[4:]})
    owner_info = await state.get_data()
    save(Owner,owner_info)
    await state.clear()
    await state.set_state(StepByStepStates.main)
    btns = [
        "🏠 Kvartira Joylash",
        "📋 Mening Kvartiralarim",
        "⚙️ Sozlamalar",
        "🔙 Orqaga"
    ]
    sizes=[1,2,1]
    markup=make_reply_btn(btns,sizes)
    await message.answer("Asosiy Panel",reply_markup=markup)

@dp.message(StepByStepStates.main,F.text=="🔙 Orqaga")
async def name_handler(message:Message,state:FSMContext):
    btns = [
        "Ijarachi",
        "Ijaraga beruvchi"
    ]
    sizes = [2]
    markup = make_inline_btn(btns, sizes)
    await state.set_state(StepByStepStates.start)
    await message.answer("Assalomu aleykum", reply_markup=ReplyKeyboardRemove())
    await message.answer("Siz kimsiz?", reply_markup=markup)


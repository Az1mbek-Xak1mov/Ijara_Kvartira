#Settings for renter and owner
from aiogram import types
from sqlalchemy import text
from db.engine import SessionLocal, engine
from db.manager import *
db = SessionLocal()
from bot.buttons.inline import make_inline_btn
from bot.buttons.reply import make_reply_btn
from bot.states import StepByStepStates ,RoleState
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from bot.dispatcher import dp
from db.models import Owner, Renter, Apartment, LikedListing


@dp.message(StepByStepStates.main, F.text == "⚙️ Sozlamalar")
async def name_handler(message: types.Message, state: FSMContext):
    await state.set_state(StepByStepStates.settings)
    btns = [
        "🌐 Tilni Tanlash",
        "👤 Ro'lni o'zgartirish",
        "📞 Telefon raqamni o'zgartirish",
        "🗑️ Hisobni o'chirish",
        "🔙 Orqaga"
    ]
    sizes = [2, 2, 1]
    markup = make_inline_btn(btns, sizes)
    await message.answer("⚙️ Sozlamalar",reply_markup=ReplyKeyboardRemove())
    await message.answer("Tanlang", reply_markup=markup)


@dp.callback_query(F.data == "🔙 Orqaga",StepByStepStates.settings)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    with engine.connect() as connection:
        result = connection.execute(text("SELECT * FROM owners WHERE chat_id = :chat_id"),
                                    {"chat_id": callback.from_user.id}).fetchone()
    if result:
        await state.set_state(StepByStepStates.main)
        btns = [
            "🏠 Kvartira Joylash",
            "📋 Mening Kvartiralarim",
            "⚙️ Sozlamalar",
            "🔙 Orqaga"
        ]
        sizes = [1, 2, 1]
        markup = make_reply_btn(btns, sizes)
        await callback.message.answer("Asosiy Panel", reply_markup=markup)
    else:
        btns = [
            "🔍 Kvartira Qidirish",
            "❤️ Yoqgan kvartiralar",
            "⚙️ Sozlamalar",
            "🔙 Orqaga"
        ]
        sizes = [1, 2, 1]
        markup = make_reply_btn(btns, sizes)
        await state.set_state(StepByStepStates.main)
        await callback.message.answer("Asosiy Panel", reply_markup=markup)

@dp.callback_query(F.data == "🗑️ Hisobni o'chirish",StepByStepStates.settings)
async def name_handler(callback:CallbackQuery):
    btns=[
        "Ha",
        "Yoq"
    ]
    sizes=[2]
    markup=make_inline_btn(btns,sizes)
    await callback.message.answer("Ishonchingiz komilmi?",reply_markup=markup)


@dp.callback_query(F.data == "Ha", StepByStepStates.settings)
async def name_handler(callback: CallbackQuery, state: FSMContext):
    chat_id = callback.message.chat.id
    data = await state.get_data()
    role = data.get("role")
    if role == "owner":
        delete_record(model=Apartment, filter_value=chat_id)
        delete_record(model=Owner, filter_value=chat_id)
    elif role == "renter":
        delete_record(model=LikedListing, filter_value=chat_id)
        delete_record(model=Renter, filter_value=chat_id)
    else:
        await callback.message.answer("Xatolik: rol aniqlanmadi ❌")
        return

    await callback.message.answer("Hisobingiz o'chirildi ✅", reply_markup=ReplyKeyboardRemove())
    await state.clear()



@dp.callback_query(F.data == "📞 Telefon raqamni o'zgartirish",StepByStepStates.settings)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    await state.set_state(StepByStepStates.new_phone)
    await callback.message.answer("Yangi telefon nomeringizni kiriting(901234567):")

@dp.message(StepByStepStates.new_phone, F.text.isdigit())
async def name_handler(message: Message, state: FSMContext):
    phone_number = message.text
    chat_id = message.chat.id
    btns = ["🔙 Orqaga"]
    sizes = [1]
    markup = make_reply_btn(btns, sizes)
    data = await state.get_data()
    role = data.get("role")

    if role == "owner":
        owner = select_one(model=Owner, filter_value=chat_id)
        if owner:
            update_record(Owner, owner.chat_id, phone_number)
            await message.answer("Telefon raqamingiz yangilandi ✅", reply_markup=markup)
    elif role == "renter":
        renter = select_one(model=Renter, filter_value=chat_id)
        if renter:
            update_record(Renter, renter.chat_id, phone_number)
            await message.answer("Telefon raqamingiz yangilandi ✅", reply_markup=markup)
    else:
        await message.answer("Xatolik: rolni aniqlay olmadim ❌")

    await state.set_state(StepByStepStates.settings)



@dp.message(StepByStepStates.settings, F.text == "🔙 Orqaga")
async def name_handler(message: types.Message, state: FSMContext):
    await state.set_state(StepByStepStates.settings)
    btns = [
        "🌐 Tilni Tanlash",
        "👤 Ro'lni o'zgartirish",
        "📞 Telefon raqamni o'zgartirish",
        "🗑️ Hisobni o'chirish",
        "🔙 Orqaga"
    ]
    sizes = [2, 2, 1]
    markup = make_inline_btn(btns, sizes)
    await message.answer("⚙️ Sozlamalar", reply_markup=markup)
    await message.answer("⚙️ Sozlamalar bo'limiga qaytinggiz",reply_markup=ReplyKeyboardRemove())

@dp.callback_query(F.data == "👤 Ro'lni o'zgartirish",StepByStepStates.settings)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    btns = [
        "Ijarachi",
        "Ijaraga beruvchi"
    ]
    sizes = [2]
    markup = make_inline_btn(btns, sizes)
    await state.set_state(StepByStepStates.start)
    await callback.message.answer("Assalomu aleykum", reply_markup=ReplyKeyboardRemove())
    await callback.message.answer("Siz kimsiz?", reply_markup=markup)

@dp.callback_query(F.data == "🌐 Tilni Tanlash",StepByStepStates.settings)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    await callback.message.answer("Hozircha faqat o'zbek tili")
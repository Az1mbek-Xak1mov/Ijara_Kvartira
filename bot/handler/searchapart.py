from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, InlineKeyboardButton, InputMediaPhoto, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder

from sqlalchemy import and_, text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from bot.buttons.reply import make_reply_btn
from bot.buttons.inline import make_inline_btn, make_inline_btn_like
from bot.dispatcher import dp
from bot.handler import bot
from bot.states import StepByStepStates, SearchState

from db.models import Apartment
from db.engine import SessionLocal
from db.manager import *

import re


db = SessionLocal()

@dp.message(StepByStepStates.main, F.text == "🔍 Kvartira Qidirish")
async def name_handler(message: Message, state: FSMContext):
    await state.set_state(SearchState.district)

    btns = [
        "Almazor tumani", "Bektemir tumani", "Mirzo Ulug'bek tumani",
        "Sergeli tumani", "Chilonzor tumani", "Shayxontaxur tumani",
        "Yunusobod tumani", "Yakkasaroy tumani", "Yashnobod tumani", "Uchtepin tumani"
    ]
    sizes = [2, 2, 2, 2, 2]
    markup = make_inline_btn(btns, sizes)
    await message.delete()
    await message.answer(
        text="...",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        "📍 Qaysi rayondan kvartira kerak:",
        reply_markup=markup
    )


@dp.callback_query(SearchState.district,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    district=callback.data
    await state.update_data({"district":district})
    await state.set_state(SearchState.rooms)
    btns=[
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
    ]
    sizes=[3,3]
    markup=make_inline_btn(btns,sizes)
    await callback.message.edit_text(
        text="🛏️ Kvartira necha xonali bo'lsin?",
        reply_markup=markup
    )
    await callback.answer()


@dp.callback_query(SearchState.rooms, F.data)
async def name_handler(callback: CallbackQuery, state: FSMContext):
    rooms=callback.data
    await state.update_data({"rooms":rooms})
    await state.set_state(SearchState.start_price)
    await callback.message.edit_text(
        text="💰 Kvartiraning boshlang'ich narxi:",
        reply_markup=None
    )
    await callback.answer()

@dp.message(SearchState.start_price, F.text.isdigit())
async def name_handler(message: Message, state: FSMContext):
    start_price=message.text
    await state.update_data({"start_price":start_price})
    await state.set_state(SearchState.end_price)
    await message.answer(
        text="💵 Kvartiraning oxirgi narxi:",
        reply_markup=None
    )

@dp.message(SearchState.end_price, F.text.isdigit())
async def price_handler(message: Message, state: FSMContext):
    end_price = message.text
    await state.update_data({"end_price": end_price})
    data = await state.get_data()
    await state.clear()
    required_keys = ["rooms", "district", "start_price",'end_price']
    if not all(key in data for key in required_keys):
        await message.answer("Iltimos, barcha ma'lumotlarni to'ldiring (xona, tuman, qavat, narx).")
        return

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("SELECT * FROM apartments WHERE rooms = :rooms AND district = :district AND price > :start_price AND price < :end_price"),
                {
                    "rooms": data["rooms"],
                    "district": data["district"],
                    "start_price": data["start_price"],
                    "end_price": data["end_price"]
                }
            ).fetchall()
        print(result)
        if result:
            for row in result:
                photos = row.images  # This is a string
                if photos:
                    photo_ids = re.sub(r'[{}]', '', photos).split(',')
                    photo_ids = [pid.strip() for pid in photo_ids if pid.strip()]
                    response = (
                        f"🛏️ Xona: {row.rooms}\n"
                        f"🏢 Turi: {row.type}\n"
                        f"🛠️ Remont: {row.repair}\n"
                        f"📞 Uy egasi raqami: {row.phone_number}\n"
                        f"📍 Tuman: {row.district}\n"
                        f"🏬 Qavat: {row.floor}\n"
                        f"💰 Narx: {row.price} $\n"
                    )
                    media_group = []

                    for idx, photo_id in enumerate(photo_ids):
                        if idx == 0:
                            media_group.append(InputMediaPhoto(media=photo_id, caption=response, parse_mode="HTML"))
                        else:
                            media_group.append(InputMediaPhoto(media=photo_id))
                    btns=["❤️Yoqdi"]
                    sizes=[1]
                    markup=make_inline_btn_like(btns,sizes,row.id)
                    await message.answer_media_group(media_group)
                    await message.answer(text="❤️ Yoqgan kvartiralar listiga qo'shish",reply_markup=markup)
                else:
                    response = (
                        f"📍 Tuman: {row.district}\n"
                        f"🛏️ Xona: {row.rooms}\n"
                        f"🏬 Qavat: {row.floor}\n"
                        f"🏢 Turi: {row.type}\n"
                        f"🛠️ Remont: {row.repair}\n"
                        f"💰 Narx: {row.price} so'm\n"
                        f"📞 Uy egasi raqami: {row.phone_number}\n"
                    )
                    await message.answer(response)
        else:
            await message.answer("🚫 Hech qanday uy topilmadi.")

    except SQLAlchemyError as e:
        await message.answer("⚠️ Ma'lumotlar bazasida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        return

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙Orqaga", callback_data="Ijarachi"))
    builder.adjust(1)

    await message.answer("⬅️ Asosiy panelga qaytish", reply_markup=builder.as_markup())
    await state.set_state(StepByStepStates.start)

@dp.callback_query(F.data.startswith("Liked_"))
async def name_handler(callback: CallbackQuery, state: FSMContext):
    print(1)
    d={}
    d["renter_id"] = int(str(callback.from_user.id))
    d["apartment_id"] = int(callback.data.split('_')[1])
    save_liked(LikedListing,d,["apartment_id"])
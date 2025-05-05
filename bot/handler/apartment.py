#Posting Apartment
import re

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.types import InputMediaPhoto
from aiogram import Bot
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from bot.buttons.additional import contact_request_btn
from bot.buttons.reply import *
from bot.buttons.inline import *
from bot.dispatcher import dp
from bot.handler import bot
from bot.states import *
from db.engine import engine
from db.models import Apartment,Owner
from aiogram.types import ReplyKeyboardRemove
from db.engine import SessionLocal
from db.manager import *
from aiogram.types import InputMediaPhoto
from sqlalchemy.orm import Session
db = SessionLocal()
from environment.utils import Env

Admin_Chat_id=Env.bot.ADMIN_CHAT_ID

@dp.message(StepByStepStates.main, F.text == "🏠 Kvartira Joylash")
async def name_handler(message: Message, state: FSMContext):
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT * FROM owners WHERE chat_id = :chat_id"),
            {"chat_id": message.from_user.id}
        ).fetchone()
    if result:
        await state.update_data({
            "owner_id": message.from_user.id,
            "phone_number": result[3]
        })

    await state.set_state(ApartmentState.district)
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
        "📍 Kvartira joylashgan rayonni kiriting:",
        reply_markup=markup
    )

@dp.callback_query(ApartmentState.district,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    district=callback.data
    await state.update_data({"district":district})
    await state.set_state(ApartmentState.rooms)
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
        text="🛏 Kvartirangizni xonalar sonini kiriting:",
        reply_markup=markup
    )
    await callback.answer()

@dp.callback_query(ApartmentState.rooms,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    rooms=callback.data
    await state.update_data({"rooms":rooms})
    await state.set_state(ApartmentState.floor)
    btns=[
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10"
    ]
    sizes=[3,3,3,1]
    markup=make_inline_btn(btns,sizes)
    await callback.message.edit_text("🏢 Kvartirangiz nechanchi qavatda joylashgan?",reply_markup=markup)
    await callback.answer()

@dp.callback_query(ApartmentState.floor,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    floor=callback.data
    await state.update_data({"floor":floor})
    await state.set_state(ApartmentState.repair)
    btns=[
        "Yevro",
        "O'rta",
        "Remontsiz"
    ]
    sizes=[1,2]
    markup=make_inline_btn(btns,sizes)
    await callback.message.edit_text("🔧 Kvartirangizni remont holatini kiriting:",reply_markup=markup)

@dp.callback_query(ApartmentState.repair,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    repair=callback.data
    await state.update_data({"repair":repair})
    await state.set_state(ApartmentState.type)
    btns=[
        "Yangi bino",
        "Eski bino",
    ]
    sizes=[2]
    markup=make_inline_btn(btns,sizes)
    await callback.message.edit_text("🏠 Kvartirangizning turini kiriting:",reply_markup=markup)

@dp.callback_query(ApartmentState.type,F.data)
async def name_handler(callback:CallbackQuery,state:FSMContext):
    type=callback.data
    await state.update_data({"type":type})
    await state.set_state(ApartmentState.images)
    await callback.message.answer("📷Kvartirangizni rasmlarini kiriting:",reply_markup=ReplyKeyboardRemove())

@dp.message(ApartmentState.images, F.photo)
async def collect_images(message: Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("images", [])
    if message.photo:
        file_id = message.photo[-1].file_id
        photos.append(file_id)
        await state.update_data({"images": photos})
        btns=["Tugadi"]
        sizes=[1]
        markup=make_reply_btn(btns,sizes)
        await message.answer("✅ Rasm qabul qilindi. Yana rasm yuboring yoki 'Tugadi' degan tugmani bosing.",reply_markup=markup)
    else:
        await message.answer("❌ Rasmni yuklashda xatolik. Iltimos, yana urinib ko‘ring.")


@dp.message(ApartmentState.images, F.text.lower() == "tugadi")
async def done_with_photos(message: Message, state: FSMContext):
    data = await state.get_data()
    if not data.get("images"):
        await message.answer("Hech qanday rasm topilmadi. Iltimos, avval rasm yuboring.",reply_markup=ReplyKeyboardRemove())
        return
    await state.set_state(ApartmentState.price)
    await message.answer("💰 Kvartirangiz narxini kiriting ($):",reply_markup=ReplyKeyboardRemove())

@dp.message(ApartmentState.price, F.text.isdigit())
async def price_handler(message: Message, state: FSMContext):
    price = message.text
    await state.update_data({"price": price})
    data = await state.get_data()
    if 'role' in data:
        del data['role']
        await state.update_data(data)
    await state.clear()
    caption = (
        f"🏢 <b>Rayon:</b> {data['district']}\n"
        f"🛏 <b>Xonalar:</b> {data['rooms']}\n"
        f"📶 <b>Qavat:</b> {data['floor']}\n"
        f"🔧 <b>Remont:</b> {data['repair']}\n"
        f"🏠 <b>Tur:</b> {data['type']}\n"
        f"💰 <b>Narx:</b> {data['price']} $\n"
        f"📞 <b>Aloqa:</b> {data.get('phone_number', 'Nomaʼlum')}"
    )
    save(Apartment,data)
    media = [InputMediaPhoto(media=file_id) for file_id in data["images"]]
    media[0].caption = caption
    media[0].parse_mode = "HTML"
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Orqaga", callback_data="Ijaraga beruvchi"))  # important!
    builder.adjust(1)
    await message.answer("✅ Maʼlumotlar adminga yuborildi!",reply_markup=builder.as_markup())
    btns = ["Tasdiqlash","Rad etish"]
    sizes = [2]
    markup = make_inline_btn_confirm(btns, sizes,message.chat.id)
    await bot.send_media_group(chat_id=Admin_Chat_id, media=media)
    await bot.send_message(chat_id=Admin_Chat_id,text="Tasdiqlang:",reply_markup=markup)

@dp.callback_query(F.data.startswith("Tasdiqlash"))
async def name_handler(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split('_')[1])
    await bot.send_message(chat_id=chat_id, text="✅ Admin kvartirani tasdiqladi!")
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                     SELECT *
                     FROM apartments a
                     JOIN owners o ON a.owner_id = o.chat_id
                     WHERE o.chat_id = :chat_id
                     ORDER BY a.created_at DESC LIMIT 1
                     """),
                {
                    "chat_id": chat_id
                }
            ).fetchall()
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
                    await callback.message.answer_media_group(media_group)
    except SQLAlchemyError as e:
        await callback.message.answer("⚠️ Ma'lumotlar bazasida xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")
        return

@dp.callback_query(F.data.startswith("Rad etish"))
async def name_handler(callback: CallbackQuery, state: FSMContext):
    chat_id = int(callback.data.split('_')[1])
    await bot.send_message(chat_id=chat_id, text="❌ Admin kvartirani tasdiqlamadi.")
    with engine.connect() as connection:
        result = connection.execute(
            text("""
                 DELETE FROM apartments a
                 USING owners o
                 WHERE a.owner_id = o.chat_id
                 AND o.chat_id = :chat_id
                 AND a.created_at = (
                     SELECT MAX(created_at)
                     FROM apartments
                     WHERE owner_id = o.chat_id
                 )
                 """),
            {
                "chat_id": chat_id
            }
        )
        connection.commit()

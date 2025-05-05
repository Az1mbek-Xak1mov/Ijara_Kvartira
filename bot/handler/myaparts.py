import re
from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputMediaPhoto, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import text
from bot.dispatcher import dp
from bot.states import StepByStepStates
from db.engine import engine


@dp.message(StepByStepStates.main,F.text=="📋 Mening Kvartiralarim")
async def name_handler(message:Message,state:FSMContext):
    with engine.connect() as connection:
        result = connection.execute(
            text(
                "SELECT * FROM apartments WHERE owner_id = :chat_id"),
            {
                "chat_id": message.chat.id,
            }
        ).fetchall()
    if result:
        for row in result:
            photos = row.images
            if photos:
                photo_ids = re.sub(r'[{}]', '', photos).split(',')
                photo_ids = [pid.strip() for pid in photo_ids if pid.strip()]  # Clean whitespace
                response = (
                    f"📍 <b>Tuman:</b> {row.district}\n"
                    f"🛏 <b>Xonalar:</b> {row.rooms}\n"
                    f"🏠 <b>Tur:</b> {row.type}\n"
                    f"🔧 <b>Remont:</b> {row.repair}\n"
                    f"🏢 <b>Qavat:</b> {row.floor}\n"
                    f"💰 <b>Narx:</b> {row.price} $\n"
                    f"📞 <b>Aloqa:</b> {row.phone_number}\n"
                )
                media_group = []
                for idx, photo_id in enumerate(photo_ids):
                    if idx == 0:
                        media_group.append(InputMediaPhoto(media=photo_id, caption=response, parse_mode="HTML"))
                    else:
                        media_group.append(InputMediaPhoto(media=photo_id))
                await message.answer_media_group(media_group)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙Orqaga", callback_data="Ijaraga beruvchi"))
    builder.adjust(1)

    await message.answer("⬅️ Asosiy panelga qaytish", reply_markup=builder.as_markup())
    await state.set_state(StepByStepStates.start)
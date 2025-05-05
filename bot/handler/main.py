from aiogram import Bot
from db.manager import *
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, URLInputFile, FSInputFile
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import asyncio
import logging
import sys
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from bot.buttons.additional import contact_request_btn
from bot.buttons.reply import *
from bot.buttons.inline import *
from bot.states import *
from bot.dispatcher import dp
from environment.utils import Env
from db.engine import SessionLocal


db = SessionLocal()
admin_chat_id=Env().bot.ADMIN_CHAT_ID
bot=Bot(Env.bot.TOKEN)


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    #checking admin or not
    # if message.chat.id == admin_chat_id:
    #     return
    btns = [
        "Ijarachi",
        "Ijaraga beruvchi"
    ]
    sizes = [2]
    markup = make_inline_btn(btns, sizes)
    await state.set_state(StepByStepStates.start)
    await message.answer("Assalomu alaykum! 👋", reply_markup=ReplyKeyboardRemove())
    await message.answer("Siz kimsiz?👇", reply_markup=markup)

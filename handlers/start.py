from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.default import get_menu_keyboard
from keyboards.menu import back_to_menu_keyboard
from texts.texts import welcome_text, main_menu_text, help_text
from auth import get_user

router = Router()

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.delete()
    kb = get_menu_keyboard(call.from_user.id)
    await call.message.answer(
        "Выбери действие:", reply_markup=kb
    )
    
    
@router.callback_query(F.data == "main_menu")
async def main_menu(call: CallbackQuery):
    kb = get_menu_keyboard(call.from_user.id)
    if not get_user(call.from_user.id):
        text = welcome_text
    else: 
        text = main_menu_text
    await call.message.answer(
        text,
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    kb = get_menu_keyboard(message.from_user.id)
    if not get_user(message.from_user.id):
        text = welcome_text
    else: 
        text = main_menu_text
    await message.answer(
        text,
        reply_markup=kb,
        parse_mode="HTML"
    )

@router.callback_query(F.data == "help")
async def help_callback(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(help_text, reply_markup=back_to_menu_keyboard(), parse_mode="HTML")



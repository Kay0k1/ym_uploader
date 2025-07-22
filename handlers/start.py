from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.default_kb import get_menu_keyboard
from keyboards.menu_kb import back_to_menu_keyboard
from keyboards.auth_kb import get_auth_keyboard
from texts.texts import main_menu_text, help_text, reg_text
from auth_utils import get_user

router = Router()

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    user = message.from_user.id
    if not await get_user(user):
        kb = await get_auth_keyboard()
        await message.answer(
            reg_text,
            reply_markup=kb,
            parse_mode="HTML"
        )
    else:
        kb = await get_menu_keyboard()
        await message.answer(
            main_menu_text,
            reply_markup=kb,
            parse_mode="HTML"
        )


@router.message(F.text == "/help")
async def help_callback(message: Message):
    if not await get_user(message.from_user.id):
        kb = await get_auth_keyboard()
    else:
        kb = await back_to_menu_keyboard()
    await message.answer(
        reg_text,
        reply_markup=kb,
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.message.delete()
    kb = await get_menu_keyboard()
    await call.message.answer(
        main_menu_text,
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "main_menu")
async def main_menu(call: CallbackQuery):
    kb = await get_menu_keyboard()
    await call.message.answer(
        main_menu_text,
        reply_markup=kb,
        parse_mode="HTML"
    )

 
@router.callback_query(F.data == "help")
async def help_callback(call: CallbackQuery):
    await call.message.delete()
    kb = await back_to_menu_keyboard()
    await call.message.answer(
        help_text,
        reply_markup=kb,
        parse_mode="HTML",
        disable_web_page_preview=True
    )
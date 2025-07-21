from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_auth_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="🔑 Авторизоваться", callback_data="auth")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
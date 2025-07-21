from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from auth import get_user

def get_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📥 Загрузить трек", callback_data="add_track")],
        [InlineKeyboardButton(text="🎵 Изменить плейлист", callback_data="change_playlist")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ]
    if not get_user(user_id):
        buttons.append([InlineKeyboardButton(text="🔑 Авторизоваться", callback_data="auth")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

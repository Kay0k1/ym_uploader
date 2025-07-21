from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="📥 Загрузить трек", callback_data="add_track")],
        [InlineKeyboardButton(text="🎵 Изменить плейлист", callback_data="change_playlist")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

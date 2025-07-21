from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="back_to_menu")]
    ])

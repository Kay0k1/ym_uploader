from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def get_admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👤 Список пользователей", callback_data="admin_users")],
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_menu")],
    ])

async def get_back_admin_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Назад", callback_data="back_to_admin_menu")]
    ])
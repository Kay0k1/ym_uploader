from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from keyboards.admin_kb import get_admin_menu
from keyboards.menu_kb import back_to_menu_keyboard
from database.requests import get_all_users, get_user_by_tg_id

router = Router()

ADMINS = [5228802546]

USERS_PER_PAGE = 5

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id not in ADMINS:
        await message.answer("🚫 У тебя нет доступа к этой команде.")
        return
    
    kb = await get_admin_menu()
    await message.answer(
        "👑 Админ-панель",
        reply_markup=kb
    )
    

@router.callback_query(F.data == "back_to_admin_menu")
async def admin_menu(call: CallbackQuery):
    await call.message.delete()
    kb = await get_admin_menu()
    await call.message.answer(
        "👑 Админ-панель",
        reply_markup=kb
    )


@router.callback_query(F.data.startswith("admin_users"))
async def show_users_paginated(call: CallbackQuery):
    try:
        page = int(call.data.split(":")[1])
    except IndexError:
        page = 0

    users = await get_all_users()
    total_pages = (len(users) - 1) // USERS_PER_PAGE + 1

    start = page * USERS_PER_PAGE
    end = start + USERS_PER_PAGE
    chunk = users[start:end]

    if not chunk:
        kb = await back_to_menu_keyboard
        await call.message.edit_text(
            "Пользователи не найдены.",
            reply_markup=kb
            )
        return

    text = "<b>📋 Список пользователей:</b>\n\n"
    for user in chunk:
        text += f"• <code>{user.tg_id}</code> — треков: {user.track_count or 0}\n"
    text += f"\n📄 Страница {page + 1} из {total_pages}\n"

    kb = InlineKeyboardBuilder()
    for user in chunk:
        kb.button(
            text=f"➡️ Профиль {user.tg_id}",
            callback_data=f"user_profile:{user.tg_id}:{page}"
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Назад", callback_data=f"admin_users:{page - 1}")
        )
    if end < len(users):
        nav_buttons.append(
            InlineKeyboardButton(text="➡️ Вперёд", callback_data=f"admin_users:{page + 1}")
        )

    kb.row(*nav_buttons)
    kb.button(text="🔙 Назад", callback_data="admin_panel")
    kb.row(InlineKeyboardButton(text="↩️ Назад в главное меню", callback_data="back_to_admin_menu"))

    await call.message.edit_text(
        text,
        reply_markup=kb.as_markup(),
        parse_mode="HTML"
    )
    

@router.callback_query(F.data.startswith("user_profile:"))
async def show_user_profile(call: CallbackQuery):
    parts = call.data.split(":")
    tg_id = int(parts[1])
    page = int(parts[2]) if len(parts) > 2 else 0
    user = await get_user_by_tg_id(tg_id)

    if not user:
        await call.message.edit_text("❌ Пользователь не найден.")
        return

    text = (
        f"<b>👤 Профиль пользователя</b>\n\n"
        f"<b>Telegram ID:</b> <code>{user.tg_id}</code>\n"
        f"<b>Token:</b> <code>{user.token}</code>\n"
        f"<b>Playlist kind:</b> <code>{user.playlist_kind}</code>\n"
        f"<b>Загружено треков:</b> {user.track_count}\n"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data=f"admin_users:{page}")],
    ])

    await call.message.edit_text(
        text,
        reply_markup=kb,
        parse_mode="HTML"
    )

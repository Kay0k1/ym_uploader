from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import PlaylistState
import auth_utils
from texts.texts import main_menu_text
from keyboards.menu_kb import back_to_menu_keyboard
from keyboards.default_kb import get_menu_keyboard

router = Router()


@router.callback_query(F.data == "change_playlist")
async def change_playlist(call: CallbackQuery, state: FSMContext):
    kb = await back_to_menu_keyboard()
    await call.message.edit_text(
        "🔁 Пришли мне новую ссылку на плейлист:",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(PlaylistState.waiting_new_link)
    

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(call: CallbackQuery, state: FSMContext):
    await state.clear()
    kb = await get_menu_keyboard()
    await call.message.edit_text(
        main_menu_text,
        reply_markup=kb,
        parse_mode="HTML"
    )


@router.message(PlaylistState.waiting_new_link)
async def receive_new_playlist(message: Message, state: FSMContext):
    user_data = await auth_utils.get_user(message.from_user.id)
    new_link = message.text.strip()
    try:
        playlist_kind = auth_utils.get_kind(new_link)
        await auth_utils.save_user(message.from_user.id, user_data["token"], playlist_kind)
        kb = await get_menu_keyboard()
        await message.answer(
            f"✅ Плейлист успешно обновлён!\n"
            f"<b>Новый kind:</b> <code>{playlist_kind}</code>",
            reply_markup=kb,
            parse_mode="HTML"
        )
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при обработке ссылки: {e}\n"
            "Пример корректной ссылки:\n"
            "<code>https://music.yandex.ru/users/имя/playlists/1234</code>",
            parse_mode="HTML"
        )
    await state.clear()

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from states import PlaylistState
import auth
from keyboards.menu import back_to_menu_keyboard
from keyboards.default import get_menu_keyboard

router = Router()

@router.callback_query(F.data == "change_playlist")
async def change_playlist(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "🔁 Пришли новую ссылку на плейлист:",
        reply_markup=back_to_menu_keyboard()
    )
    await state.set_state(PlaylistState.waiting_new_link)


@router.message(PlaylistState.waiting_new_link)
async def receive_new_playlist(message: Message, state: FSMContext):
    if message.text == "🔙 Назад":
        await message.answer(
            "Главное меню:",
            reply_markup=get_menu_keyboard(message.from_user.id)
        )
        await state.clear()
        return

    user_data = auth.get_user(message.from_user.id)
    if not user_data:
        await message.answer("❌ Сначала авторизуйтесь через /auth")
        await state.clear()
        return
    new_link = message.text.strip()
    try:
        playlist_kind = auth.get_kind(new_link)
        auth.save_user(message.from_user.id, user_data["token"], playlist_kind)
        await message.answer(
            f"✅ Плейлист успешно обновлён. Новый kind: {playlist_kind}",
            reply_markup=get_menu_keyboard(message.from_user.id)
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при обработке ссылки: {e}")
    await state.clear()

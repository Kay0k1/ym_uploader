from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AuthState
import auth as auth_utils
from texts.texts import auth_text
from keyboards.menu import back_to_menu_keyboard

router = Router()

@router.message(F.text == "/auth")
async def start_auth(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AuthState.waiting_token:
        return
    await message.answer(auth_text, parse_mode="HTML")
    await state.set_state(AuthState.waiting_token)


@router.callback_query(F.data == "auth")
async def auth_callback(call: CallbackQuery, state: FSMContext):
    await call.message.answer(auth_text, parse_mode="HTML")
    await state.set_state(AuthState.waiting_token)

@router.message(AuthState.waiting_token)
async def receive_token(message: Message, state: FSMContext):
    token = message.text.strip()
    if not token.startswith("y0_"):
        await message.answer("❌ Неверный формат токена. Попробуй снова.")
        return
    await state.update_data(token=token)
    await message.answer("🎵 Теперь пришли ссылку на плейлист, куда будет загружаться треки")
    await state.set_state(AuthState.waiting_playlist)

@router.message(AuthState.waiting_playlist)
async def receive_playlist(message: Message, state: FSMContext):
    playlist_link = message.text.strip()
    data = await state.get_data()
    try:
        kind = await auth_utils.authenticate(message.from_user.id, data["token"], playlist_link)
        await message.answer(
            f"✅ Успешно! Токен и плейлист сохранены.\n"
            f"<b>kind:</b> <code>{kind}</code>\n\n"
            "Теперь можно загружать треки 👇",
            reply_markup=back_to_menu_keyboard(),
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer(f"❌ Ошибка при сохранении: {e}")
    await state.clear()
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import AuthState
import auth_utils
from texts.texts import reg_text, auth_text
from keyboards.menu_kb import back_to_menu_keyboard
from keyboards.auth_kb import get_auth_keyboard

router = Router()

@router.message(F.text == "/auth")
async def start_auth(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AuthState.waiting_token:
        return
    kb = await get_auth_keyboard()
    await message.answer(
        reg_text,
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.set_state(AuthState.waiting_token)


@router.callback_query(F.data == "auth")
async def auth_callback(call: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state == AuthState.waiting_token:
        await call.answer()
        return
    await state.set_state(AuthState.waiting_token)
    
    await call.message.edit_text(auth_text, parse_mode="HTML")
    await call.answer()



@router.message(AuthState.waiting_token)
async def receive_token(message: Message, state: FSMContext):
    token = message.text.strip()
    if not token.startswith("y0_"):
        await message.answer("❌ Неверный формат токена. Напиши /start, чтобы попробовать снова")
        await state.clear()
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
        kb = await back_to_menu_keyboard()
        await message.answer(
            f"✅ Успешно! Токен и плейлист сохранены.\n"
            f"<b>kind:</b> <code>{kind}</code>\n\n"
            "Теперь можно загружать треки 👇",
            reply_markup=kb,
            parse_mode="HTML"
        )

    except Exception as e:
        await message.answer(
            f"❌ Ошибка при сохранении: {e}\n обратись к @avtilomm за помощью",
            disable_web_page_preview=True
        )
    await state.clear()
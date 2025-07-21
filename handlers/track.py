from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states import AddTrackState
from downloader import set_mp3_metadata, download_audio, extract_youtube_id
import os
import sys
import uploader
import auth
import asyncio
import logging

sys.path.append(".")
router = Router()


@router.callback_query(F.data == "add_track")
async def add_track_callback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("🎧 Введи название трека или ссылку на него:")
    await state.set_state(AddTrackState.waiting_query)


@router.message(AddTrackState.waiting_query)
async def process_query(message: Message, state: FSMContext):
    user_id = message.from_user.id
    query = message.text.strip()

    data = auth.get_user(user_id)
    if not data:
        await message.answer("Сначала авторизуйтесь через /auth")
        await state.clear()
        return

    await message.answer("⏬ Скачиваю аудио...")
    try:
        mp3_path = await asyncio.to_thread(download_audio, query)
    except Exception as e:
        logging.exception("download error")
        await message.answer(f"❌ Ошибка загрузки аудио: {e}")
        await state.clear()
        return

    await state.update_data(mp3_path=mp3_path, original_query=query)
    await message.answer("✍️ Введите, как будет отображаться трек в плейлисте:")
    await state.set_state(AddTrackState.waiting_title)


@router.message(AddTrackState.waiting_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    await message.answer(
        "🖼️ Выберите обложку для трека:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Оставить как на YouTube", callback_data="cover_youtube")],
            [InlineKeyboardButton(text="Без обложки", callback_data="cover_none")],
            [InlineKeyboardButton(text="Загрузить свою", callback_data="cover_custom")]
        ])
    )
    await state.set_state(AddTrackState.waiting_cover_choice)


@router.callback_query(F.data.startswith("cover_"))
async def cover_choice_handler(call: CallbackQuery, state: FSMContext):
    choice = call.data.split("_")[1]
    await state.update_data(cover_type=choice)

    if choice == "custom":
        await call.message.edit_text("📎 Пришли изображение (JPG/PNG), которое будет обложкой для трека:")
        await state.set_state(AddTrackState.waiting_cover_file)
    else:
        if choice == "youtube":
            data = await state.get_data()
            youtube_id = extract_youtube_id(data.get("original_query", ""))
            if youtube_id:
                await state.update_data(cover_url=f"https://i.ytimg.com/vi/{youtube_id}/maxresdefault.jpg")
        await finalize_upload(call.message, call.from_user.id, state)


@router.message(AddTrackState.waiting_cover_file, F.photo)
async def process_cover_file(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_info = await message.bot.get_file(photo.file_id)
    file_path = f"/tmp/{photo.file_id}.jpg"
    await message.bot.download_file(file_info.file_path, destination=file_path)

    await state.update_data(cover_path=file_path)
    await finalize_upload(message, message.from_user.id, state)


async def finalize_upload(reply_target: Message, user_id: int, state: FSMContext):
    data = await state.get_data()
    user = auth.get_user(user_id)

    if not user:
        await reply_target.answer("❌ Вы не авторизованы. Используйте /auth.")
        await state.clear()
        return

    await reply_target.answer("📤 Загружаю в Яндекс.Музыку...")

    try:
        await asyncio.to_thread(
            set_mp3_metadata,
            data["mp3_path"],
            data["title"],
            cover_path=data.get("cover_path") if data.get("cover_type") == "custom" else None,
            cover_url=data.get("cover_url") if data.get("cover_type") == "youtube" else None
        )

        await asyncio.to_thread(
            uploader.upload_track,
            token=user["token"],
            playlist_kind=user["playlist_kind"],
            file_path=data["mp3_path"]
        )

    except Exception as e:
        logging.exception("upload error")
        await reply_target.answer(f"❌ Ошибка загрузки в плейлист: {e}")
        await state.clear()
        return

    os.remove(data["mp3_path"])
    cover_path = data.get("cover_path")
    if cover_path and os.path.exists(cover_path):
        os.remove(cover_path)

    await reply_target.answer("✅ Трек загружен!")
    await state.clear()

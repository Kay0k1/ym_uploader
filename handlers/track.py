from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from states import AddTrackState
from database.requests import add_user_track
from yt_downloader import set_mp3_metadata, download_audio
from texts.texts import mp3_instruction_text
import os
import uploader
import auth_utils
import asyncio
import logging
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

router = Router()

@router.callback_query(F.data == "add_track")
async def add_track_callback(call: CallbackQuery, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔎 Загрузить с YouTube", callback_data="track_source_youtube")],
        [InlineKeyboardButton(text="📁 Загрузить MP3", callback_data="track_source_mp3")]
    ])
    await call.message.edit_text("Выберите способ загрузки трека:", reply_markup=kb)
    await state.set_state(AddTrackState.choosing_source)


@router.callback_query(F.data.startswith("track_source_"))
async def choose_track_source(call: CallbackQuery, state: FSMContext):
    source = call.data.split("_")[-1]

    if source == "youtube":
        await call.message.edit_text("🎧 Введи название трека или ссылку на него:")
        await state.set_state(AddTrackState.waiting_query)
    elif source == "mp3":
        await call.message.edit_text(
            mp3_instruction_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")]
            ]),
            parse_mode="HTML"
        )
        await state.set_state(AddTrackState.waiting_mp3_file)


@router.message(AddTrackState.waiting_query)
async def process_query(message: Message, state: FSMContext):
    query = message.text.strip()

    msg = await message.answer("⏬ Скачиваю аудио...\nЭто может занять некоторое время")
    try:
        mp3_path, cover_url = await asyncio.to_thread(download_audio, query)
        await state.update_data(
            mp3_path=mp3_path,
            original_query=query,
            cover_url=cover_url,
            source="youtube"
        )
    except Exception as e:
        logging.exception("download error")
        await msg.edit_text(
            f"❌ Ошибка загрузки аудио: {e}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")]
            ])
        )
        await state.clear()
        return

    await msg.edit_text("✍️ Введите, как будет отображаться трек в плейлисте:")
    await state.set_state(AddTrackState.waiting_title)


@router.message(AddTrackState.waiting_mp3_file)
async def handle_mp3_entry(message: Message, state: FSMContext):
    file = message.audio or message.document

    if not file:
        logging.info("Skip non-file message in mp3 wait: %s", message.content_type)
        return

    if not file.mime_type or file.mime_type != "audio/mpeg":
        await message.answer(
            "❌ Это не mp3-файл. Попробуй ещё раз.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")]
            ])
        )
        return

    file_info = await message.bot.get_file(file.file_id)
    file_path = f"/tmp/{file.file_unique_id}.mp3"
    await message.bot.download_file(file_info.file_path, destination=file_path)

    has_cover = False
    try:
        audio = MP3(file_path, ID3=ID3)
        has_cover = any(tag.FrameID == "APIC" for tag in audio.tags.values())
    except Exception as e:
        logging.warning(f"Ошибка при чтении ID3: {e}")

    original_query = file.file_name
    if message.via_bot and message.audio:
        original_query = f"{file.performer or ''} - {file.title or ''}".strip()

    await state.update_data(
        mp3_path=file_path,
        original_query=original_query,
        has_cover=has_cover,
        source="mp3"
    )

    await message.answer("✍️ Введите, как будет отображаться трек в плейлисте:")
    await state.set_state(AddTrackState.waiting_title)


@router.message(AddTrackState.waiting_title)
async def process_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text.strip())
    data = await state.get_data()

    buttons = []
    if data.get("source") == "youtube":
        buttons.append([InlineKeyboardButton(text="Оставить как на YouTube", callback_data="cover_youtube")])
    elif data.get("has_cover"):
        buttons.append([InlineKeyboardButton(text="Оставить как в mp3", callback_data="cover_mp3")])

    buttons.append([InlineKeyboardButton(text="Как в loaditbot", callback_data="cover_none")])
    buttons.append([InlineKeyboardButton(text="Загрузить свою", callback_data="cover_custom")])
    buttons.append([InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")])

    await message.answer("🖼️ Выберите обложку для трека:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await state.set_state(AddTrackState.waiting_cover_choice)


@router.callback_query(F.data.startswith("cover_"))
async def cover_choice_handler(call: CallbackQuery, state: FSMContext):
    choice = call.data.split("_")[1]
    await state.update_data(cover_type=choice)

    if choice == "custom":
        await call.message.edit_text("📎 Пришли изображение (JPG/PNG):", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")]
        ]))
        await state.set_state(AddTrackState.waiting_cover_file)
    else:
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
    user = await auth_utils.get_user(user_id)

    msg = await reply_target.answer("📤 Загружаю в Яндекс.Музыку...")

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
        await msg.edit_text(
            f"❌ Ошибка загрузки: {e}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="↩️ Вернуться в меню", callback_data="main_menu")]
            ])
        )
        await state.clear()
        return

    os.remove(data["mp3_path"])
    if data.get("cover_path") and os.path.exists(data["cover_path"]):
        os.remove(data["cover_path"])

    await msg.edit_text(
        f"✅ Трек <b>{data['title']}</b> загружен!",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="↩️ В меню", callback_data="main_menu")],
            [InlineKeyboardButton(text="📥 Загрузить ещё", callback_data="add_track")]
        ]),
        parse_mode="HTML"
    )
    await add_user_track(user_id, data["title"])
    await state.clear()

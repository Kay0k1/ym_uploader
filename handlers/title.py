from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from states import AddTrackState
import auth_utils
import asyncio
import uploader
import os
import logging
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from keyboards.menu_kb import back_to_menu_keyboard

router = Router()

@router.message(AddTrackState.waiting_title)
async def set_custom_title(message: Message, state: FSMContext):
    data = await state.get_data()
    mp3_path = data.get("mp3_path")
    if not mp3_path:
        await message.answer("❌ Не удалось найти загруженный трек.")
        await state.clear()
        return

    title = message.text.strip()
    try:
        audio = MP3(mp3_path, ID3=EasyID3)
        audio["title"] = title
        audio.save()
    except Exception as e:
        logging.exception("tag error")
        await message.answer(f"❌ Не удалось установить название: {e}")
        await state.clear()
        return

    await message.answer("🚀 Загружаю в Яндекс.Музыку...")

    user_data = await auth_utils.get_user(message.from_user.id)
    
    try:
        await asyncio.to_thread(
            uploader.upload_track,
            user_data["token"],
            user_data["playlist_kind"],
            mp3_path
        )
    except Exception as e:
        logging.exception("upload error")
        await message.answer(f"❌ Ошибка загрузки в плейлист: {e}")
        await state.clear()
        return

    os.remove(mp3_path)
    kb = await back_to_menu_keyboard()
    await message.answer(
        f"✅ Трек {title} загружен!",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await state.clear()

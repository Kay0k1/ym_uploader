import os
from aiogram.types import Message


async def save_mp3_file(message: Message, file_path: str) -> str:
    """
    Сохраняет документ (mp3-файл), загруженный через вложения.
    """
    file_info = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file_info.file_path, destination=file_path)
    return file_path


async def save_inline_audio(message: Message, file_path: str) -> str:
    """
    Сохраняет аудио, отправленное как inline-аудиофайл (например, через @loaditbot).
    """
    file_info = await message.bot.get_file(message.audio.file_id)
    await message.bot.download_file(file_info.file_path, destination=file_path)
    return file_path
import os
import uuid
import re
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, APIC
import requests


def download_audio(query: str) -> tuple[str, str | None]:
    """Скачивает аудио и возвращает путь к mp3-файлу."""
    if not query.startswith(("http://", "https://")):
        query = f"ytsearch1:{query}"

    output_path = f"/tmp/{uuid.uuid4()}.%(ext)s"
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "ffmpeg_location": "path/to/ffmpeg", #чтобы узнать путь пропишите which ffmpeg
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "noprogress": True,
        "proxy": "socks5h://login:pass@ipv4:port",
        "socket_timeout": 10
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=True)
    except DownloadError as e:
        raise RuntimeError(f"yt-dlp error: {e}")
    
    final_path = output_path.replace(".%(ext)s", ".mp3")
    if not os.path.exists(final_path):
        raise RuntimeError("MP3 файл не найден после загрузки.")
    
    if info.get("_type") == "playlist":
        info = info["entries"][0]
    return final_path, info.get("thumbnail")


def set_mp3_metadata(
    file_path: str,
    title: str,
    cover_path: str | None = None,
    cover_url: str | None = None
) -> None:
    """
    Добавляет метаданные в mp3-файл: название и обложку.
    
    Аргументы:
        `file_path`: путь до файла
        `title`: название трека
        `cover_path`: путь до обложки
        `cover_url`: ссылка на обложку
    """
    audio = MP3(file_path, ID3=ID3)

    try:
        audio.add_tags()
    except Exception:
        pass

    audio.tags["TIT2"] = TIT2(encoding=3, text=title)

    if cover_path and os.path.exists(cover_path):
        with open(cover_path, 'rb') as img:
            audio.tags["APIC"] = APIC(
                encoding=3,
                mime='image/jpeg',
                type=3,
                desc='Cover',
                data=img.read()
            )
    elif cover_url:
        img_data = requests.get(cover_url, allow_redirects=True).content
        audio.tags["APIC"] = APIC(
            encoding=3,
            mime='image/jpeg',
            type=3,
            desc='Cover',
            data=img_data
        )

    audio.save()


def extract_youtube_id(url_or_query: str) -> str | None:
    """
    Возвращает `YouTube ID` из ссылки или `None`, если не удалось.
    """
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11})", 
        r"youtu\.be\/([0-9A-Za-z_-]{11})", 
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_query)
        if match:
            return match.group(1)
    return None

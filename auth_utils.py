from database.requests import get_user_by_tg_id, save_or_update_user
from typing import Optional

def get_kind(link: str) -> str:
    """
    Получение уникального `kind` плейлиста пользователя
    """
    parts = link.split("/")
    if len(parts) >= 7:
        return parts[6].split("?")[0]
    raise ValueError("Не удалось определить kind плейлиста")

async def get_user(user_id: int) -> Optional[dict]:
    user = await get_user_by_tg_id(user_id)
    if user and user.token and user.playlist_kind:
        return {
            "token": user.token,
            "playlist_kind": user.playlist_kind
        }
    return None

async def save_user(user_id: int, token: str, playlist_kind: str) -> None:
    await save_or_update_user(user_id, token, playlist_kind)

async def authenticate(user_id: int, token: str, playlist_link: str) -> str:
    playlist_kind = get_kind(playlist_link)
    await save_user(user_id, token, playlist_kind)
    return playlist_kind

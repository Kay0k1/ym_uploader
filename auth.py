import json
from pathlib import Path
from typing import Optional

DB_PATH = Path("db.json")


def load_db() -> dict:
    if DB_PATH.exists():
        with DB_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_db(db: dict) -> None:
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
        f.flush()
        

def get_user(user_id: int) -> Optional[dict]:
    return load_db().get(str(user_id))


def save_user(user_id: int, token: str, playlist_kind: str) -> None:
    db = load_db()
    db[str(user_id)] = {"token": token, "playlist_kind": playlist_kind}
    save_db(db)

    
    
def get_kind(link: str) -> str:
    """Извлечение `kind` из ссылки на плейлист."""
    parts = link.split("/")
    if len(parts) >= 7:
        return parts[6].split("?")[0]
    raise ValueError("Не удалось определить kind плейлиста")


def authenticate(user_id: int, token: str, playlist_link: str) -> str:
    """Сохранение токена и kind плейлиста пользователя."""
    playlist_kind = get_kind(playlist_link)
    save_user(user_id, token, playlist_kind)
    return playlist_kind

import os
import urllib.parse
from typing import Optional
from yandex_music import Client


def upload_track(
    token: str,
    playlist_kind: str,
    file_path: str,
    title: Optional[str] = None,
    cover_path: Optional[str] = None,
) -> None:
    """Загрузка файла в приватный плейлист по его `kind`, с кастомным названием и опциональной обложкой."""
    client = Client(token).init()
    file_name = os.path.basename(file_path)
    encoded = urllib.parse.quote(file_name, safe='_!() ')
    encoded = encoded.replace(' ', '+')

    params = {
        'filename': encoded,
        'kind': playlist_kind,
        'visibility': 'private',
        'lang': 'ru',
        'external-domain': 'music.yandex.ru',
        'overembed': 'false',
    }

    data = client.request.get(
        url='https://music.yandex.ru/handlers/ugc-upload.jsx',
        params=params,
        timeout=3,
    )

    upload_url = data['post_target'].replace(':443', '', 1)

    # Загружаем сам трек
    with open(file_path, 'rb') as f:
        resp = client.request.post(
            url=upload_url,
            files={'file': f},
            timeout=120,
        )
    if resp != 'CREATED':
        raise RuntimeError(f'Upload failed: {resp}')

    # Меняем название трека, если указано
    track_id = data.get("track_id")
    if title and track_id:
        client.request.post(
            url="https://music.yandex.ru/api/v2/handlers/edit-track-name",
            json={"trackId": track_id, "value": title},
            timeout=3,
        )

    # Загружаем обложку, если указана
    if cover_path and os.path.exists(cover_path) and track_id:
        with open(cover_path, "rb") as img:
            client.request.post(
                url="https://music.yandex.ru/api/v2/handlers/edit-track-cover",
                params={"trackId": track_id},
                files={"cover": img.read()},
                timeout=5,
            )

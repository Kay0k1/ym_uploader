from .auth import router as auth_handler
from .track import router as track
from .start import router as start
from .playlist import router as playlist
from .title import router as title

__all__ = ["auth", "track", "start", "playlist", "title"]

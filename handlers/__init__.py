from .auth import router as auth
from .track import router as track
from .start import router as start
from .playlist import router as playlist
from .admin import router as admin

__all__ = ["auth", "track", "start", "playlist", "admin"]

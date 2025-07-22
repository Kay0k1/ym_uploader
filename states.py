from aiogram.fsm.state import State, StatesGroup

class AuthState(StatesGroup):
    waiting_token = State()
    waiting_playlist = State()

class PlaylistState(StatesGroup):
    waiting_new_link = State()

class AddTrackState(StatesGroup):
    waiting_mp3_file = State()
    waiting_query = State()
    waiting_title = State()
    waiting_cover_choice = State()
    waiting_cover_file = State()
    choosing_source = State()
    
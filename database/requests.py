from sqlalchemy import select
from database.models import async_session, User, Track

async def add_user_track(tg_id: int, title: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if not user:
            return

        track = Track(user_id=user.id, title=title)
        session.add(track)
        user.track_count += 1
        await session.commit()

async def get_user_by_tg_id(tg_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

async def reg_user(tg_id: int) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if not user:
            session.add(User(tg_id=tg_id, token="", playlist_kind=""))
            await session.commit()

async def save_or_update_user(tg_id: int, token: str, kind: str) -> None:
    async with async_session() as session:
        result = await session.execute(select(User).where(User.tg_id == tg_id))
        user = result.scalar_one_or_none()

        if user:
            user.token = token
            user.playlist_kind = kind
        else:
            user = User(tg_id=tg_id, token=token, playlist_kind=kind)
            session.add(user)

        await session.commit()

async def get_all_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()

import logging
import os
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database.models import async_main

from handlers import start, auth, track, playlist, admin

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set BOT_TOKEN environment variable")

bot = Bot(BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(start)
dp.include_router(auth)
dp.include_router(track)
dp.include_router(playlist)
dp.include_router(admin)

async def main():
    await async_main()
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit") 

import os
from datetime import datetime
from os.path import exists
from typing import Tuple

import aiofiles
import httpx
import pytz
from fastapi import Query

from app.config import settings


async def save_file(file, location):
    async with aiofiles.open(location, "wb") as f:
        while content := await file.read(1024):  # Read file in chunks
            await f.write(content)
    return {"info": f"file '{file.filename}' saved at '{location}'"}


async def update_file(file, old_location, location):
    if exists(old_location):
        if old_location == location:
            return
        os.remove(old_location)
    async with aiofiles.open(location, "wb") as f:
        while content := await file.read(1024):  # Read file in chunks
            await f.write(content)
    return


def get_current_time() -> datetime:
    tz = pytz.timezone('Asia/Tashkent')
    return datetime.now(tz)


async def pagination_dependency(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
) -> Tuple[int, int]:
    """
    Pagination dependency.

    :param page: The page number (starting from 1).
    :param size: Number of items per page (page size).
    :return: A tuple (offset, limit) to be used in database queries.
    """
    offset = (page - 1) * size
    limit = size
    return offset, limit


async def paginate(pagination_func, query, db):
    offset, limit = pagination_func
    result = await db.execute(query.offset(offset).limit(limit))
    return result.scalars().all()


async def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{settings.BUG_BOT}/sendMessage"
    payload = {
        "chat_id": settings.ABROR_CHAT_ID,
        "text": message,
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, data=payload)
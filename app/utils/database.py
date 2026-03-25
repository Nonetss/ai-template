from noneai import init_db as _noneai_init_db
from noneai import close_db


async def init_db():
    from core.config import DATABASE_URL
    await _noneai_init_db(DATABASE_URL)

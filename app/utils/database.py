from tortoise import Tortoise
from core.config import DATABASE_URL

# Tortoise espera "postgres://" — convertimos desde el formato SQLAlchemy si hace falta
_db_url = DATABASE_URL.replace("postgresql+asyncpg://", "postgres://")

TORTOISE_ORM = {
    "connections": {
        "default": _db_url,
    },
    "apps": {
        "models": {
            "models": ["models.conversation"],
            "default_connection": "default",
        },
    },
}


async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()


async def close_db():
    await Tortoise.close_connections()

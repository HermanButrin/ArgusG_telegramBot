import asyncpg

from aiogram_bot_template.data import config


ALLOWED_RARITIES = (
    "common",
    "uncommon",
    "rare",
    "epic",
    "legendary",
)


async def item_exists(name: str) -> bool:
    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        exists = await pool.fetchval(
            'SELECT 1 FROM "item" WHERE lower(name) = lower($1)',
            name,
        )
        return bool(exists)
    finally:
        await pool.close()


async def insert_item(
    name: str,
    description: str | None,
    price: int,
    rarity: str,
) -> None:
    pool = await asyncpg.create_pool(config.PG_LINK, min_size=1, max_size=1)
    try:
        await pool.execute(
            """
            INSERT INTO "item" (name, description, price, rarity)
            VALUES ($1, $2, $3, $4)
            """,
            name,
            description,
            price,
            rarity,
        )
    finally:
        await pool.close()

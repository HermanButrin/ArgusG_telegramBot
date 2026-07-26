from datetime import datetime

import asyncpg


ALLOWED_RARITIES = (
    "common",
    "uncommon",
    "rare",
    "epic",
    "legendary",
)


async def item_exists(pool: asyncpg.Pool, name: str) -> bool:
    exists = await pool.fetchval(
        'SELECT 1 FROM "item" WHERE lower(name) = lower($1)',
        name,
    )
    return bool(exists)


async def insert_item(
    pool: asyncpg.Pool,
    name: str,
    description: str | None,
    price: int,
    rarity: str,
) -> None:
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

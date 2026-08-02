from asyncpg import Pool

ALLOWED_RARITIES = (
    "common",
    "uncommon",
    "rare",
    "epic",
    "legendary",
)


ALLOWED_GENRES = (
    "heavy metal",
    "thrash metal",
    "death metal",
    "black metal",
    "doom metal",
    "power metal",
    "progressive metal",
)


async def item_exists(pool: Pool, name: str) -> bool:
    exists = await pool.fetchval(
        'SELECT 1 FROM "item" WHERE lower(name) = lower($1)',
        name,
    )
    return bool(exists)


# ruff: noqa: PLR0913, PLR0917, FBT001
async def insert_item(
    pool: Pool,
    name: str,
    description: str,
    price: int,
    rarity: str,
    is_stackable: bool,
    genre: str,
    proficiency_bonus: int,
) -> None:
    await pool.execute(
        """
        INSERT INTO item
        (
            name,
            description,
            price,
            rarity,
            is_stackable,
            genre,
            proficiency_bonus
        )
        VALUES
        ($1,$2,$3,$4,$5,$6,$7)
        """,
        name,
        description,
        price,
        rarity,
        is_stackable,
        genre,
        proficiency_bonus,
    )


async def remove_item(pool: Pool, name: str) -> bool:
    result = await pool.execute(
        """
        DELETE FROM item
        WHERE lower(name)=lower($1)
        """,
        name,
    )

    return result != "DELETE 0"

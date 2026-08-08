from asyncpg import Pool

ALLOWED_RARITIES = {
    "common": "",
    "uncommon": "🟢",
    "rare": "🔵",
    "epic": "🟣",
    "legendary": "🟡",
}


RARITY_ORDER = {
    "common": 0,
    "uncommon": 1,
    "rare": 2,
    "epic": 3,
    "legendary": 4,
}


ALLOWED_GENRES = (
    "heavy metal",
    "thrash metal",
    "death metal",
    "black metal",
    "doom metal",
    "power metal",
    "progressive metal",
)


ALLOWED_TYPES = (
    "guitar",
    "bass",
    "drums",
    "keyboard",
    "vocal",
    "other",
)


async def item_exists(pool: Pool, instrument_type: str, brand: str, model: str) -> bool:
    exists = await pool.fetchval(
        'SELECT 1 FROM "item" WHERE lower(type) = lower($1) AND lower(brand) = lower($2) AND lower(model) = lower($3)',
        instrument_type,
        brand,
        model,
    )
    return bool(exists)


# ruff: noqa: PLR0913, PLR0917, FBT001
async def insert_item(
    pool: Pool,
    instrument_type: str,
    brand: str,
    model: str,
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
            type,
            brand,
            model,
            description,
            price,
            rarity,
            is_stackable,
            genre,
            proficiency_bonus
        )
        VALUES
        ($1,$2,$3,$4,$5,$6,$7,$8,$9)
        """,
        instrument_type,
        brand,
        model,
        description,
        price,
        rarity,
        is_stackable,
        genre,
        proficiency_bonus,
    )


async def remove_item(pool: Pool, instrument_type: str, brand: str, model: str) -> bool:
    result = await pool.execute(
        """
        DELETE FROM item
        WHERE lower(type)=lower($1) AND lower(brand)=lower($2) AND lower(model)=lower($3)
        """,
        instrument_type,
        brand,
        model,
    )

    return result != "DELETE 0"


async def get_item_by_id(pool: Pool, item_id: int) -> dict | None:
    row = await pool.fetchrow(
        """
        SELECT *
        FROM item
        WHERE id = $1
        """,
        item_id,
    )
    return dict(row) if row else None


async def get_item_by_brand_model(
    pool: Pool,
    brand: str,
    model: str,
) -> dict | None:
    row = await pool.fetchrow(
        """
        SELECT *
        FROM item
        WHERE lower(brand) = lower($1)
          AND lower(model) = lower($2)
        """,
        brand,
        model,
    )
    return dict(row) if row else None


async def get_distinct_instrument_types(pool: Pool) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT DISTINCT type
        FROM item
        ORDER BY type
        """,
    )
    return [row["type"] for row in rows]


async def get_distinct_brands_by_type(pool: Pool, instrument_type: str) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT DISTINCT brand
        FROM item
        WHERE lower(type) = lower($1)
        ORDER BY brand
        """,
        instrument_type,
    )
    return [row["brand"] for row in rows]


async def get_models_by_brand(pool: Pool, instrument_type: str, brand: str) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT model
        FROM item
        WHERE lower(type) = lower($1) AND lower(brand) = lower($2)
        ORDER BY model
        """,
        instrument_type,
        brand,
    )
    return [row["model"] for row in rows]


async def get_models_with_rarity_by_brand(pool: Pool, instrument_type: str, brand: str) -> list[str]:
    rows = await pool.fetch(
        """
        SELECT ON (lower(model))
            model,
            rarity
        FROM item
        WHERE lower(type) = lower($1)
          AND lower(brand) = lower($2)
        ORDER BY lower(model), rarity
        """,
        instrument_type,
        brand,
    )

    models = [dict(row) for row in rows]

    return sorted(
        models,
        key=lambda item: RARITY_ORDER[item["rarity"]],
    )


async def get_all_items(pool: Pool) -> list[dict]:
    rows = await pool.fetch(
        """
        SELECT *
        FROM item
        """,
    )
    return [dict(row) for row in rows]

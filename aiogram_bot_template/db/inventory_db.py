import asyncpg


async def add_item_to_inventory(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
    quantity: int = 1,
) -> None:
    await pool.execute(
        """
        INSERT INTO useritem (telegram_id, item_id, quantity)
        VALUES ($1, $2, $3)
        ON CONFLICT (telegram_id, item_id)
        DO UPDATE SET
            quantity = useritem.quantity + EXCLUDED.quantity
        """,
        telegram_id,
        item_id,
        quantity,
    )


async def remove_item_from_inventory(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
    quantity: int = 1,
) -> None:
    await pool.execute(
        """
        UPDATE useritem
        SET quantity = quantity - $3
        WHERE telegram_id = $1
          AND item_id = $2
        """,
        telegram_id,
        item_id,
        quantity,
    )

    await pool.execute(
        """
        DELETE FROM useritem
        WHERE quantity <= 0
        """,
    )


async def find_useritem_by_user_id(
    pool: asyncpg.Pool,
    telegram_id: int,
) -> list[dict[str, object]]:
    rows = await pool.fetch(
        """
        SELECT
            i.id,
            i.type,
            i.brand,
            i.model,
            i.description,
            i.price,
            i.rarity,
            ui.quantity
        FROM useritem ui
        JOIN item i
            ON ui.item_id = i.id
        WHERE ui.telegram_id = $1
        ORDER BY i.rarity DESC, i.brand, i.model
        """,
        telegram_id,
    )

    return [dict(row) for row in rows]


async def user_has_item(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
) -> bool:
    row = await pool.fetchrow(
        """
        SELECT 1
        FROM useritem
        WHERE telegram_id = $1
          AND item_id = $2
        """,
        telegram_id,
        item_id,
    )

    return row is not None


async def get_item_quantity(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
) -> int:
    row = await pool.fetchrow(
        """
        SELECT quantity
        FROM useritem
        WHERE telegram_id = $1
          AND item_id = $2
        """,
        telegram_id,
        item_id,
    )

    return 0 if row is None else row["quantity"]

from enum import Enum

import asyncpg


class PurchaseResult(Enum):
    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found"
    NOT_ENOUGH_COINS = "not_enough_coins"
    ITEM_NOT_FOUND = "item_not_found"
    ITEM_ALREADY_OWNED = "item_already_owned"


async def buy_item(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
) -> PurchaseResult:
    async with (
        pool.acquire() as connection,
        connection.transaction(),
    ):
        item = await connection.fetchrow(
            """
            SELECT id, price, is_stackable
            FROM item
            WHERE id = $1
            """,
            item_id,
        )

        if item is None:
            return PurchaseResult.ITEM_NOT_FOUND

        user = await connection.fetchrow(
            """
            SELECT telegram_id, coins
            FROM "user"
            WHERE telegram_id = $1
            FOR UPDATE
            """,
            telegram_id,
        )

        if user is None:
            return PurchaseResult.USER_NOT_FOUND

        is_stackable = bool(item["is_stackable"])

        if not is_stackable:
            existing_item = await connection.fetchrow(
                """
                SELECT quantity
                FROM useritem
                WHERE telegram_id = $1
                  AND item_id = $2
                """,
                telegram_id,
                item_id,
            )

            if existing_item is not None:
                return PurchaseResult.ITEM_ALREADY_OWNED

        price = item["price"]

        if user["coins"] < price:
            return PurchaseResult.NOT_ENOUGH_COINS

        await connection.execute(
            """
            UPDATE "user"
            SET coins = coins - $1
            WHERE telegram_id = $2
            """,
            price,
            telegram_id,
        )

        if is_stackable:
            await connection.execute(
                """
                INSERT INTO useritem (
                    telegram_id,
                    item_id,
                    quantity
                )
                VALUES ($1, $2, 1)
                ON CONFLICT (telegram_id, item_id)
                DO UPDATE SET
                    quantity = useritem.quantity + 1
                """,
                telegram_id,
                item_id,
            )
        else:
            await connection.execute(
                """
                INSERT INTO useritem (
                    telegram_id,
                    item_id,
                    quantity
                )
                VALUES ($1, $2, 1)
                """,
                telegram_id,
                item_id,
            )

        return PurchaseResult.SUCCESS

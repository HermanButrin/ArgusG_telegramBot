import asyncpg


class PurchaseResult:
    SUCCESS = "success"
    USER_NOT_FOUND = "user_not_found"
    NOT_ENOUGH_COINS = "not_enough_coins"
    ITEM_NOT_FOUND = "item_not_found"


async def buy_item(
    pool: asyncpg.Pool,
    telegram_id: int,
    item_id: int,
) -> str:
    async with (
        pool.acquire() as connection,
        connection.transaction(),
    ):
        item = await connection.fetchrow(
            """
            SELECT id, price
            FROM item
            WHERE id = $1
            """,
            item_id,
        )

        if item is None:
            return PurchaseResult.ITEM_NOT_FOUND

        price = item["price"]

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

        return PurchaseResult.SUCCESS

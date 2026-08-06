import asyncpg


async def ensure_user_exists(pool: asyncpg.Pool, telegram_id: int) -> None:
    await pool.execute(
        """
        INSERT INTO "user" (telegram_id)
        VALUES ($1)
        ON CONFLICT (telegram_id) DO NOTHING
        """,
        telegram_id,
    )


async def update_last_active(pool: asyncpg.Pool, telegram_id: int) -> None:
    await pool.execute(
        """
        UPDATE "user"
        SET last_active_at = NOW()
        WHERE telegram_id = $1
        """,
        telegram_id,
    )


async def upsert_user(
    pool: asyncpg.Pool,
    telegram_id: int,
    first_name: str | None,
    last_name: str | None,
    username: str | None,
) -> None:
    await pool.execute(
        """
        INSERT INTO "user" (telegram_id, first_name, last_name, username)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            username = EXCLUDED.username
        """,
        telegram_id,
        first_name,
        last_name,
        username,
    )


async def fetch_user(
    pool: asyncpg.Pool,
    telegram_id: int,
) -> dict[str, object] | None:
    user_row = await pool.fetchrow(
        """
        SELECT
            telegram_id,
            first_name,
            last_name,
            username,
            coins,
            is_banned,
            is_admin,
            created_at,
            updated_at,
            last_active_at,
            coins_cooldown
        FROM "user"
        WHERE telegram_id = $1
        """,
        telegram_id,
    )
    return dict(user_row) if user_row is not None else None


async def is_user_admin(pool: asyncpg.Pool, telegram_id: int) -> bool:
    user_row = await pool.fetchrow(
        'SELECT is_admin FROM "user" WHERE telegram_id = $1',
        telegram_id,
    )
    if user_row is None:
        return False
    return bool(user_row["is_admin"])


async def promote_user_by_username(pool: asyncpg.Pool, username: str) -> bool:
    updated_user = await pool.fetchrow(
        """
        UPDATE "user"
        SET is_admin = TRUE
        WHERE username = $1
        RETURNING telegram_id
        """,
        username,
    )
    return updated_user is not None


async def is_user_not_banned(pool: asyncpg.Pool, telegram_id: int) -> bool:
    user_row = await pool.fetchrow(
        'SELECT is_banned FROM "user" WHERE telegram_id = $1',
        telegram_id,
    )
    if user_row is None:
        return True
    return not bool(user_row["is_banned"])


async def ban_user_by_username(pool: asyncpg.Pool, username: str) -> bool:
    updated_user = await pool.fetchrow(
        """
        UPDATE "user"
        SET is_banned = TRUE
        WHERE username = $1
        RETURNING telegram_id
        """,
        username,
    )
    return updated_user is not None


async def unban_user_by_username(pool: asyncpg.Pool, username: str) -> bool:
    updated_user = await pool.fetchrow(
        """
        UPDATE "user"
        SET is_banned = FALSE
        WHERE username = $1
        RETURNING telegram_id
        """,
        username,
    )
    return updated_user is not None


async def award_user_coins(
    pool: asyncpg.Pool,
    telegram_id: int,
    coins: int,
    coins_cooldown: object,
) -> None:
    await pool.execute(
        """
        INSERT INTO "user" (telegram_id, coins, coins_cooldown)
        VALUES ($1, $2, $3)
        ON CONFLICT (telegram_id)
        DO UPDATE SET
            coins = "user".coins + EXCLUDED.coins,
            coins_cooldown = EXCLUDED.coins_cooldown
        """,
        telegram_id,
        coins,
        coins_cooldown,
    )

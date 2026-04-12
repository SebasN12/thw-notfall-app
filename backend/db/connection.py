import os
import ssl
import aiomysql
from dotenv import load_dotenv

load_dotenv()

pool: aiomysql.Pool | None = None


async def init_db():
    global pool

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    pool = await aiomysql.create_pool(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME"),
        autocommit=False,
        minsize=1,
        maxsize=10,
        ssl=ssl_ctx,
    )


async def close_db():
    global pool
    if pool:
        pool.close()
        await pool.wait_closed()


def get_pool() -> aiomysql.Pool:
    if pool is None:
        raise RuntimeError("Datenbankverbindung nicht initialisiert")
    return pool
from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.db.connection import init_db, close_db, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "API running successfully!"}

@app.get("/test-db")
async def test_db():
    try:
        pool = get_pool()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT 1;")
                result = await cursor.fetchone()

        return {
            "db": "connected",
            "result": result
        }

    except Exception as e:
        return {"error": str(e)}
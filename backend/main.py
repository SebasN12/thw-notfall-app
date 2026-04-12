from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.db.connection import init_db, close_db

from backend.app.routes import lager_routes as lager
from backend.app.routes import stock_routes as stock


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Lagerbestand API", lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "API running successfully!"}


@app.get("/test-db")
async def test_db():
    try:
        from backend.db.connection import get_pool

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


# Router registrieren
app.include_router(lager.router)
app.include_router(stock.router)
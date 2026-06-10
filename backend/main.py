from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.db.connection import init_db, close_db

from backend.app.routes import lager_routes as lager
from backend.app.routes import stock_routes as stock
from backend.app.routes import supply_routes as supply


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(title="Lagerbestand API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


@app.get("/debug/tables")
async def debug_tables():
    try:
        from backend.db.connection import get_pool

        pool = get_pool()

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SHOW TABLES;")
                result = await cursor.fetchall()

        return {"tables": result}

    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/calculator-schema")
async def debug_calculator_schema():
    try:
        from backend.db.connection import get_pool

        pool = get_pool()

        tables = [
            "erzeugnisgruppe",
            "product_threshold",
            "product",
            "stock",
        ]

        result = {}

        async with pool.acquire() as conn:
            async with conn.cursor() as cursor:
                for table in tables:
                    await cursor.execute(f"SHOW COLUMNS FROM {table};")
                    result[table] = await cursor.fetchall()

        return result

    except Exception as e:
        return {"error": str(e)}

# Router registrieren
app.include_router(lager.router)
app.include_router(stock.router)
app.include_router(supply.router)
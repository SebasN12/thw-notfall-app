from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.connection import init_db, close_db
from app.routes import lager_routes as lager
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()
 
 
app = FastAPI(title="Lagerbestand API", lifespan=lifespan)
 
app.include_router(lager.router)
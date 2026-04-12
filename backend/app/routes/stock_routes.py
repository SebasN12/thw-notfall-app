from fastapi import APIRouter
from backend.db.connection import get_pool
from backend.app.models.stock_model import (
    StockRemoveRequest,
    StockAddRequest,
    StockActionResponse,
)
from backend.app.services import stock_service

router = APIRouter(prefix="/stock", tags=["Bestand"])


@router.post("/remove", response_model=StockActionResponse)
async def stock_remove(data: StockRemoveRequest):
    return await stock_service.remove_stock(get_pool(), data)


@router.post("/add", response_model=StockActionResponse)
async def stock_add(data: StockAddRequest):
    return await stock_service.add_stock(get_pool(), data)
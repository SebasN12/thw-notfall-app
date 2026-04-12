from pydantic import BaseModel, Field
from datetime import date, datetime


class StockRemoveRequest(BaseModel):
    stock_id: int
    user_id: int
    quantity: int = Field(..., gt=0)
    reason: str | None = None


class StockAddRequest(BaseModel):
    shelf_slot_id: int
    product_id: int
    user_id: int
    quantity: int = Field(..., gt=0)
    best_before: date | None = None
    stored_at: date | None = None
    reason: str | None = None


class StockActionResponse(BaseModel):
    message: str
    stock_id: int
    quantity: int


class StockMovementResponse(BaseModel):
    id: int
    stock_id: int
    user_id: int
    type: str
    reason: str | None = None
    quantity: int
    timestamp: datetime | None = None
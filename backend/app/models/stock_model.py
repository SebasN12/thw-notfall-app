from pydantic import BaseModel, Field
from datetime import date, datetime


class NaehrwerteSchema(BaseModel):
    kcal: float | None
    protein: float | None
    fett: float | None
    kohlenhydrate: float | None


class StockDetailResponse(BaseModel):
    stock_id: int
    produkt_id: int
    shelf_slot_id: int
    name: str | None
    marke: str | None
    menge: str | None
    erzeugnisgruppe: str | None
    mhd: date | None
    menge_eingelagert: int
    menge_geoeffnet: int
    barcode: str | None
    naehrwerte: NaehrwerteSchema

    lagerfach_id: int
    lagerfach_position: str | None
    regal_id: int
    regal_bezeichnung: str | None
    warehouse_id: int
    warehouse_name: str | None


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
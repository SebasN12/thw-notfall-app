from fastapi import APIRouter, HTTPException
from backend.db.connection import get_pool
from backend.app.models.lager_model import (
    OrtsverbandListItem,
    LagerListItem,
    LagerDetailSchema,
)
from backend.app.services import lager_service
 
router = APIRouter(tags=["Lager"])
 

@router.get("/ortsverbaende", response_model=list[OrtsverbandListItem])
async def ortsverbaende_liste():
    return await lager_service.get_alle_ortsverbaende(get_pool())
 
 
@router.get("/ortsverbaende/{ortsverband_id}/warehouses", response_model=list[LagerListItem])
async def lager_liste(ortsverband_id: int):
    result = await lager_service.get_lager_by_ortsverband(get_pool(), ortsverband_id)
    if not result:
        raise HTTPException(status_code=404, detail="Kein Lager für diesen Ortsverband gefunden")
    return result
 
 
@router.get("/warehouses/{warehouse_id}", response_model=LagerDetailSchema)
async def lager_detail(warehouse_id: int):
    result = await lager_service.get_lager_detail(get_pool(), warehouse_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lager nicht gefunden")
    return result
 
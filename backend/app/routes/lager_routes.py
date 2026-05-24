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
    result = await lager_service.get_lager_detail_v2(get_pool(), warehouse_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lager nicht gefunden")
    return result

@router.get("/benchmark/lager_detail")
async def benchmark():
    import time

    runs = 10
    times = []
    times_v2 = []

    for _ in range(runs):
        start = time.perf_counter()

        # 1323 test warehouse for Karlstadt

        result = await lager_service.get_lager_detail(get_pool(), 1323)

        end = time.perf_counter()

        times.append(end - start)

    avg_time = sum(times) / runs

    for _ in range(runs):
        start = time.perf_counter()

        result = await lager_service.get_lager_detail_v2(get_pool(), 1323)

        end = time.perf_counter()

        times_v2.append(end - start)

    avg_time_v2 = sum(times_v2) / runs

    return {
        "comparison": {
            "get_lager_detail": {
                "runs": runs,
                "average_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "performance_ok": False if avg_time > 0.5 else True,
                "ok": True
            },
            "get_lager_detail_v2": {
                "runs": runs,
                "average_time": avg_time_v2,
                "min_time": min(times_v2),
                "max_time": max(times_v2),
                "performance_ok": False if avg_time_v2 > 0.5 else True,
                "ok": True
            }
        }
    }
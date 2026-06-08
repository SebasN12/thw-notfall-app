from fastapi import APIRouter, HTTPException, Query
from backend.db.connection import get_pool
from backend.app.models.lager_model import (
    OrtsverbandListItem,
    LagerListItem,
    LagerDetailSchema,
    ExpiringProductSchema
)
from backend.app.services import lager_service
 
router = APIRouter()
 

@router.get("/ortsverbaende", tags=["Lager"], response_model=list[OrtsverbandListItem])
async def ortsverbaende_liste():
    return await lager_service.get_alle_ortsverbaende(get_pool())
 
 
@router.get("/ortsverbaende/{ortsverband_id}/warehouses", tags=["Lager"], response_model=list[LagerListItem])
async def lager_liste(ortsverband_id: int):
    result = await lager_service.get_lager_by_ortsverband(get_pool(), ortsverband_id)
    if not result:
        raise HTTPException(status_code=404, detail="Kein Lager für diesen Ortsverband gefunden")
    return result
 
 
@router.get("/warehouses/{warehouse_id}", tags=["Lager"], response_model=LagerDetailSchema)
async def lager_detail(warehouse_id: int):
    result = await lager_service.get_lager_detail_v2(get_pool(), warehouse_id)
    if not result:
        raise HTTPException(status_code=404, detail="Lager nicht gefunden")
    return result

@router.get("/benchmark/lager_detail", tags=["benchmark"])
async def benchmark():
    import time
    import random

    runs = 10
    times = []
    times_v2 = []

    warehouse_ids = await lager_service.get_all_warehouse_ids(get_pool())

    for _ in range(runs):
        start = time.perf_counter()

        warehouse_id = random.choice(warehouse_ids)

        result = await lager_service.get_lager_detail(get_pool(), warehouse_id)

        end = time.perf_counter()

        times.append(end - start)

    avg_time = sum(times) / runs

    for _ in range(runs):
        start = time.perf_counter()

        warehouse_id = random.choice(warehouse_ids)

        result = await lager_service.get_lager_detail_v2(get_pool(), warehouse_id)

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

@router.get("/benchmark/expiring-products", tags=["benchmark"])
async def benchmark_expiring_products():
    import time
    import random

    runs = 100
    times = []

    warehouse_ids = await lager_service.get_all_warehouse_ids(get_pool())

    for _ in range(runs):

        warehouse_id = random.choice(warehouse_ids)

        start = time.perf_counter()

        result = await lager_service.get_expiring_products(get_pool(), warehouse_id, 30)

        end = time.perf_counter()

        times.append(end - start)

    avg_time = sum(times) / runs

    return {
            "get_expiring_products": {
                "runs": runs,
                "average_time": avg_time,
                "min_time": min(times),
                "max_time": max(times),
                "performance_ok": False if avg_time > 0.5 else True,
                "ok": True
            },
    }

@router.get("/{warehouse_id}/expiring-products", tags=["expiring-products"], response_model=list[ExpiringProductSchema])
async def expiring_products_by_warehouse(warehouse_id: int, expiring_within_days: int = Query(30, ge=1, le=365)):
    return await lager_service.get_expiring_products(
        pool=get_pool(),
        warehouse_id=warehouse_id,
        days=expiring_within_days,
    )
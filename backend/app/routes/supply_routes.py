from fastapi import APIRouter, HTTPException, status

from backend.db.connection import get_pool
from backend.app.models.supply_model import (
    SupplyCalculatorRequest,
    SupplyCalculatorResponse,
    ProductThresholdResponse,
    WarehouseStockResponse,
)
from backend.app.services import supply_service


router = APIRouter(
    prefix="/api/v1/supply-calculator",
    tags=["Vorratsrechner"],
)


@router.post("/calculate", response_model=SupplyCalculatorResponse)
async def calculate_supply(data: SupplyCalculatorRequest):
    try:
        return await supply_service.calculate_supply(
            pool=get_pool(),
            ortsverband_id=data.ortsverband_id,
            num_persons=data.num_persons,
            duration_days=data.duration_days,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/product-thresholds", response_model=list[ProductThresholdResponse])
async def product_thresholds():
    try:
        return await supply_service.get_product_thresholds(get_pool())

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/warehouse-stock/{ortsverband_id}", response_model=list[WarehouseStockResponse])
async def warehouse_stock(ortsverband_id: int):
    try:
        return await supply_service.get_warehouse_stock(
            pool=get_pool(),
            ortsverband_id=ortsverband_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "supply-calculator",
    }
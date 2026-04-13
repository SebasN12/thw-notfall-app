from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from mysql.connector import Error
from supply_calculator_service import SupplyCalculatorService
from models import (
    SupplyCalculatorRequest,
    SupplyCalculatorResponse,
    ProductThresholdResponse,
    WarehouseStockResponse,
    ErrorResponse,
)
from db import get_db_connection  # Abhängig von deiner DB-Connection Struktur

# Router für Vorratsrechner-Endpoints
router = APIRouter(
    prefix="/api/v1/supply-calculator",
    tags=["supply-calculator"],
    responses={
        404: {"model": ErrorResponse, "description": "Ressource nicht gefunden"},
        500: {"model": ErrorResponse, "description": "Interner Serverfehler"},
    },
)


@router.post(
    "/calculate",
    response_model=SupplyCalculatorResponse,
    status_code=200,
    summary="Vorratsrechnung durchführen",
    description="Berechnet Vorratsdeckung basierend auf Personenanzahl und Versorgungsdauer",
)
async def calculate_supply(
    request: SupplyCalculatorRequest,
    db_connection=Depends(get_db_connection),
) -> SupplyCalculatorResponse:
    """
    Hauptendpoint für Vorratsrechnung

    **Parameter:**
    - `ortsverband_id`: ID des Ortsverbands
    - `num_persons`: Anzahl zu versorgender Personen (> 0)
    - `duration_days`: Versorgungsdauer in Tagen (> 0)

    **Returns:**
    - Detaillierte Vorratsrechnung mit Deckungsgrad pro Erzeugnisgruppe
    - Gesamtbewertung in Personentagen
    - Ampelstatus (GREEN/YELLOW/RED)

    **Beispiel Request:**
    ```json
    {
        "ortsverband_id": 1,
        "num_persons": 50,
        "duration_days": 14
    }
    ```

    **Beispiel Response:**
    ```json
    {
        "ortsverband_id": 1,
        "ortsverband_name": "Karlstadt",
        "input_persons": 50,
        "input_duration_days": 14,
        "total_person_days": 28.5,
        "overall_status": "YELLOW",
        "product_groups": [
            {
                "erzeugnisgruppe_name": "Getreideprodukte",
                "required_amount": 231.0,
                "current_stock": 150.0,
                "coverage_percentage": 65.0,
                "status": "YELLOW"
            }
        ]
    }
    ```
    """
    try:
        service = SupplyCalculatorService(db_connection)
        result = service.calculate_supply(
            ortsverband_id=request.ortsverband_id,
            num_persons=request.num_persons,
            duration_days=request.duration_days,
        )
        return result

    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(ve),
        )
    except Error as db_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Datenbankfehler: {str(db_error)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Fehler: {str(e)}",
        )


@router.get(
    "/product-thresholds",
    response_model=list[ProductThresholdResponse],
    status_code=200,
    summary="BBK-Schwellwerte abrufen",
    description="Gibt alle BBK-Mindestmengen pro Erzeugnisgruppe zurück",
)
async def get_product_thresholds(
    db_connection=Depends(get_db_connection),
) -> list[ProductThresholdResponse]:
    """
    Holt alle BBK-Empfehlungen 2023 für Erzeugnisgruppen

    **Returns:**
    - Liste aller Erzeugnisgruppen mit Mindestmengen pro Person und Tag

    **Beispiel Response:**
    ```json
    [
        {
            "erzeugnisgruppe_id": 1,
            "erzeugnisgruppe_name": "Getreideprodukte",
            "min_quantity": 0.33,
            "unit": "kg"
        },
        {
            "erzeugnisgruppe_id": 2,
            "erzeugnisgruppe_name": "Obst & Gemüse",
            "min_quantity": 0.25,
            "unit": "kg"
        }
    ]
    ```
    """
    try:
        service = SupplyCalculatorService(db_connection)
        result = service.get_product_thresholds()
        return result

    except Error as db_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Datenbankfehler: {str(db_error)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Fehler: {str(e)}",
        )


@router.get(
    "/warehouse-stock/{ortsverband_id}",
    response_model=list[WarehouseStockResponse],
    status_code=200,
    summary="Lagerbestand abrufen",
    description="Gibt aktuellen Lagerbestand eines Ortsverbands pro Erzeugnisgruppe",
)
async def get_warehouse_stock(
    ortsverband_id: int,
    db_connection=Depends(get_db_connection),
) -> list[WarehouseStockResponse]:
    """
    Holt aktuellen Lagerbestand eines Ortsverbands

    **Parameter:**
    - `ortsverband_id`: ID des Ortsverbands

    **Returns:**
    - Aktueller Bestand pro Erzeugnisgruppe

    **Beispiel Response:**
    ```json
    [
        {
            "erzeugnisgruppe_id": 1,
            "erzeugnisgruppe_name": "Getreideprodukte",
            "current_stock": 150.0,
            "unit": "kg"
        }
    ]
    ```
    """
    try:
        service = SupplyCalculatorService(db_connection)
        result = service.get_warehouse_stock(ortsverband_id)
        return result

    except Error as db_error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Datenbankfehler: {str(db_error)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Fehler: {str(e)}",
        )


@router.get(
    "/health",
    status_code=200,
    summary="Health Check",
    description="Prüft Verfügbarkeit des Supply Calculator Service",
)
async def health_check():
    """
    Health Check Endpoint

    **Returns:**
    ```json
    {
        "status": "healthy",
        "service": "supply-calculator"
    }
    ```
    """
    return {"status": "healthy", "service": "supply-calculator"}

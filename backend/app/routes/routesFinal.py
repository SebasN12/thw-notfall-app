"""
🔀 ROUTES - Alle API Routes zusammengefasst
Alternative Struktur für größere Projekte
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import logging

from supply_calculator_FINAL import (
    calculate_supply,
    calculate_supply_timeline,
    get_supply_history,
    compare_regional_supply,
    clear_cache,
    get_health_status
)

from models import (
    CalculateResponse,
    TimelineResponse,
    HistoryResponse,
    RegionalResponse,
    CacheResponse,
    HealthResponse
)

# ==================== SETUP ====================

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/supply-calculator", tags=["Supply Calculator"])

# ==================== ROUTES ====================

@router.post("/calculate", response_model=CalculateResponse)
async def calculate(
    ortsverband_id: int = Query(..., gt=0, description="ID des Ortsverbands"),
    num_persons: int = Query(..., gt=0, le=10000, description="Anzahl Personen"),
    duration_days: int = Query(..., gt=0, le=365, description="Anzahl Tage")
):
    """
    📊 CALCULATE: Berechne Deckungsgrad
    
    Gibt für alle Produktgruppen an, wie viel % davon vorhanden ist.
    """
    
    try:
        logger.info(f"Calculate: {num_persons} Personen, {duration_days} Tage")
        result = calculate_supply(ortsverband_id, num_persons, duration_days)
        return result
        
    except Exception as e:
        logger.error(f"Calculate Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-timeline/{ortsverband_id}", response_model=TimelineResponse)
async def timeline(
    ortsverband_id: int = Query(..., gt=0),
    num_persons: int = Query(..., gt=0, le=10000),
    max_days: int = Query(30, gt=0, le=365)
):
    """
    📈 TIMELINE: Zeige kritische Tage
    
    Frage: "Ab wann wird es kritisch?"
    """
    
    try:
        logger.info(f"Timeline: {num_persons} Personen, bis Tag {max_days}")
        result = calculate_supply_timeline(ortsverband_id, num_persons, max_days)
        return result
        
    except Exception as e:
        logger.error(f"Timeline Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{ortsverband_id}", response_model=HistoryResponse)
async def history(
    ortsverband_id: int = Query(..., gt=0),
    days: int = Query(30, gt=0, le=365)
):
    """
    📊 HISTORY: Zeige historische Trends
    
    Frage: "Wird die Situation besser oder schlechter?"
    """
    
    try:
        logger.info(f"History: {ortsverband_id}, {days} Tage")
        result = get_supply_history(ortsverband_id, days)
        return result
        
    except Exception as e:
        logger.error(f"History Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-regional/{regional_id}", response_model=RegionalResponse)
async def regional(
    regional_id: int = Query(..., gt=0),
    num_persons: int = Query(..., gt=0, le=10000),
    duration_days: int = Query(..., gt=0, le=365)
):
    """
    🌍 REGIONAL: Vergleiche Ortsverbände
    
    Frage: "Wo können wir Vorrätе umverteilen?"
    """
    
    try:
        logger.info(f"Regional: {regional_id}, {num_persons} Personen")
        result = compare_regional_supply(regional_id, num_persons, duration_days)
        return result
        
    except Exception as e:
        logger.error(f"Regional Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cache/clear", response_model=CacheResponse)
async def cache_clear():
    """
    🗑️ CACHE CLEAR: Leert Redis Cache
    
    Nutze nach Datenbankänderungen
    """
    
    try:
        logger.warning("Cache Clear requested")
        result = clear_cache()
        return result
        
    except Exception as e:
        logger.error(f"Cache Clear Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthResponse)
async def health():
    """
    ❤️ HEALTH: Überprüfe System Status
    """
    
    try:
        logger.info("Health Check")
        result = get_health_status()
        return result
        
    except Exception as e:
        logger.error(f"Health Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


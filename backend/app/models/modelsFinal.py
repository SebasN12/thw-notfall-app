"""
📊 MODELS - Pydantic Request/Response Modelle
Für Input-Validierung und API-Dokumentation
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# ==================== REQUEST MODELS ====================

class CalculateRequest(BaseModel):
    """Request für Calculate Endpoint"""
    ortsverband_id: int = Field(..., gt=0, description="ID des Ortsverbands (1-100)")
    num_persons: int = Field(..., gt=0, le=10000, description="Anzahl Personen (1-10000)")
    duration_days: int = Field(..., gt=0, le=365, description="Anzahl Tage (1-365)")
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "num_persons": 50,
            "duration_days": 14
        }

class TimelineRequest(BaseModel):
    """Request für Timeline Endpoint"""
    ortsverband_id: int = Field(..., gt=0, description="ID des Ortsverbands")
    num_persons: int = Field(..., gt=0, le=10000, description="Anzahl Personen")
    max_days: int = Field(30, gt=0, le=365, description="Max Tage (default: 30)")
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "num_persons": 50,
            "max_days": 30
        }

class HistoryRequest(BaseModel):
    """Request für History Endpoint"""
    ortsverband_id: int = Field(..., gt=0, description="ID des Ortsverbands")
    days: int = Field(30, gt=0, le=365, description="Tage in Vergangenheit (default: 30)")
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "days": 30
        }

class RegionalRequest(BaseModel):
    """Request für Regional Endpoint"""
    regional_id: int = Field(..., gt=0, description="ID der Region")
    num_persons: int = Field(..., gt=0, le=10000, description="Anzahl Personen")
    duration_days: int = Field(..., gt=0, le=365, description="Anzahl Tage")
    
    class Config:
        example = {
            "regional_id": 1,
            "num_persons": 50,
            "duration_days": 14
        }

# ==================== RESPONSE MODELS ====================

class ProductGroupResult(BaseModel):
    """Ergebnis für eine Produktgruppe"""
    product_id: int
    product_name: str
    required: float = Field(..., description="Benötigte Menge in kg/Liter")
    stock: float = Field(..., description="Aktueller Bestand in kg/Liter")
    coverage_percent: float = Field(..., description="Deckungsgrad in %")
    status: str = Field(..., description="Status: 🟢 GRÜN / 🟡 GELB / 🔴 ROT")
    
    class Config:
        example = {
            "product_id": 1,
            "product_name": "Getreideprodukte",
            "required": 245.5,
            "stock": 500.0,
            "coverage_percent": 203.7,
            "status": "🟢 GRÜN"
        }

class CalculateResponse(BaseModel):
    """Response für Calculate Endpoint"""
    ortsverband_id: int
    num_persons: int
    duration_days: int
    total_person_days: float
    overall_coverage: float = Field(..., description="Gesamt-Deckungsgrad in %")
    overall_status: str = Field(..., description="Gesamt-Status")
    products: List[ProductGroupResult]
    timestamp: str
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "num_persons": 50,
            "duration_days": 14,
            "total_person_days": 700,
            "overall_coverage": 85.5,
            "overall_status": "🟡 GELB",
            "products": [
                {
                    "product_id": 1,
                    "product_name": "Getreideprodukte",
                    "required": 245.5,
                    "stock": 500.0,
                    "coverage_percent": 203.7,
                    "status": "🟢 GRÜN"
                }
            ],
            "timestamp": "2026-05-27T14:30:45.123456"
        }

class TimelineDay(BaseModel):
    """Ein Tag in der Timeline"""
    day: int
    coverage: float = Field(..., description="Deckungsgrad in %")
    status: str = Field(..., description="Status für diesen Tag")

class TimelineResponse(BaseModel):
    """Response für Timeline Endpoint"""
    ortsverband_id: int
    num_persons: int
    max_days: int
    days: List[TimelineDay]
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "num_persons": 50,
            "max_days": 30,
            "days": [
                {"day": 1, "coverage": 95.0, "status": "🟢 GRÜN"},
                {"day": 2, "coverage": 92.0, "status": "🟢 GRÜN"},
                {"day": 15, "coverage": 65.0, "status": "🔴 ROT"}
            ]
        }

class HistoryEntry(BaseModel):
    """Ein Eintrag in der History"""
    date: str
    coverage: float = Field(..., description="Deckungsgrad in %")
    status: str = Field(..., description="Status an diesem Datum")

class HistoryResponse(BaseModel):
    """Response für History Endpoint"""
    ortsverband_id: int
    period_days: int
    entries: List[HistoryEntry]
    trend: str = Field(..., description="Trend: 📈 VERBESSERND / 📉 VERSCHLECHTERND / 📊 STABIL")
    
    class Config:
        example = {
            "ortsverband_id": 1,
            "period_days": 30,
            "entries": [
                {"date": "2026-04-27", "coverage": 75.0, "status": "🟡 GELB"},
                {"date": "2026-04-28", "coverage": 78.0, "status": "🟡 GELB"},
                {"date": "2026-05-27", "coverage": 90.0, "status": "🟢 GRÜN"}
            ],
            "trend": "📈 VERBESSERND"
        }

class RegionalOrtsverband(BaseModel):
    """Ein Ortsverband im Regional-Vergleich"""
    ortsverband_id: int
    coverage: float = Field(..., description="Deckungsgrad in %")
    capacity: str = Field(..., description="Kategorie: ÜBERSCHUSS / AUSREICHEND / DEFIZIT")

class RegionalResponse(BaseModel):
    """Response für Regional Endpoint"""
    region_id: int
    ortsverbände: List[RegionalOrtsverband]
    
    class Config:
        example = {
            "region_id": 1,
            "ortsverbände": [
                {"ortsverband_id": 1, "coverage": 120.0, "capacity": "🟢 ÜBERSCHUSS (Kann geben)"},
                {"ortsverband_id": 2, "coverage": 85.0, "capacity": "🟡 AUSREICHEND"},
                {"ortsverband_id": 3, "coverage": 55.0, "capacity": "🔴 DEFIZIT (Braucht Hilfe)"}
            ]
        }

class CacheResponse(BaseModel):
    """Response für Cache Clear"""
    status: str = Field(..., description="success oder error")
    message: str = Field(..., description="Beschreibung")
    
    class Config:
        example = {
            "status": "success",
            "message": "Cache cleared"
        }

class HealthComponent(BaseModel):
    """Eine Komponente im Health Check"""
    api: str = Field(..., description="API Status")
    database: str = Field(..., description="Datenbank Status")
    cache: str = Field(..., description="Cache Status")
    logging: str = Field(..., description="Logging Status")

class HealthResponse(BaseModel):
    """Response für Health Endpoint"""
    status: str = Field(..., description="healthy oder warning")
    timestamp: str
    components: HealthComponent
    
    class Config:
        example = {
            "status": "healthy",
            "timestamp": "2026-05-27T14:30:45.123456",
            "components": {
                "api": "✅ Running",
                "database": "✅ Connected",
                "cache": "✅ Connected",
                "logging": "✅ Active"
            }
        }

# ==================== ERROR MODELS ====================

class ErrorResponse(BaseModel):
    """Standard Error Response"""
    error: bool = True
    status_code: int
    detail: str
    timestamp: str
    
    class Config:
        example = {
            "error": True,
            "status_code": 400,
            "detail": "num_persons muss > 0 sein",
            "timestamp": "2026-05-27T14:30:45.123456"
        }

# ==================== INFO MODELS ====================

class RootResponse(BaseModel):
    """Response für Root Endpoint"""
    message: str
    version: str
    timestamp: str
    features: List[str]
    docs: str
    endpoints: dict


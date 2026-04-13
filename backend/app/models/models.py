from pydantic import BaseModel, Field
from typing import Optional


class SupplyCalculatorRequest(BaseModel):
    """
    Request-Modell für den Vorratsrechner
    Benutzer gibt Anzahl Personen und Versorgungsdauer ein
    """
    ortsverband_id: int = Field(..., gt=0, description="ID des Ortsverbands")
    num_persons: int = Field(..., gt=0, description="Anzahl zu versorgender Personen")
    duration_days: int = Field(..., gt=0, description="Versorgungsdauer in Tagen")


class ProductGroupRequirement(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    unit: str
    min_quantity: float = Field(
        ..., description="BBK Mindestmenge pro Person und Tag"
    )
    required_amount: float = Field(
        ..., description="Bedarf = min_quantity × Personen × Tage"
    )
    current_stock: float = Field(
        ..., description="Aktueller Bestand im Ortsverband"
    )
    coverage_percentage: float = Field(
        ..., ge=0, le=200, description="Deckungsgrad in Prozent"
    )
    status: str = Field(
        ..., description="Status: 'GREEN' (≥100%), 'YELLOW' (<100% & ≥50%), 'RED' (<50%)"
    )
    kcal_available: float = Field(
        ..., description="Verfügbare Kilokalorien dieser Gruppe"
    )
    kcal_required: float = Field(
        ..., description="Benötigte Kilokalorien dieser Gruppe"
    )


class SupplyCalculatorResponse(BaseModel):
    """
    Response-Modell für den Vorratsrechner mit Gesamtbewertung
    """
    ortsverband_id: int
    ortsverband_name: str
    calculation_date: str
    input_persons: int
    input_duration_days: int
    product_groups: list[ProductGroupRequirement]
    total_kcal_available: float = Field(
        ..., description="Gesamte verfügbare Kilokalorien"
    )
    total_kcal_required: float = Field(
        ..., description="Gesamt benötigte Kilokalorien (2200 kcal/Person/Tag)"
    )
    total_person_days: float = Field(
        ..., description="Wie viele Personentage kann der Vorrat leisten?"
    )
    overall_status: str = Field(
        ...,
        description="Gesamtstatus: 'GREEN' (100-150% coverage), 'YELLOW' (50-99%), 'RED' (<50%)",
    )
    summary: str = Field(..., description="Zusammenfassung in Worten")


class ProductThresholdResponse(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    min_quantity: float
    unit: str
    bemerkung: Optional[str] = None


class WarehouseStockResponse(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    current_stock: float
    unit: str
    shelf_details: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    status_code: int

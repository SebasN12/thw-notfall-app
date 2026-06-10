from pydantic import BaseModel, Field


class SupplyCalculatorRequest(BaseModel):
    ortsverband_id: int = Field(..., gt=0)
    num_persons: int = Field(..., gt=0, le=10000)
    duration_days: int = Field(..., gt=0, le=365)


class ProductGroupRequirement(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    unit: str | None
    min_quantity: float
    required_amount: float
    current_stock: float
    coverage_percentage: float
    status: str
    kcal_available: float
    kcal_required: float


class SupplyCalculatorResponse(BaseModel):
    ortsverband_id: int
    ortsverband_name: str
    calculation_date: str
    input_persons: int
    input_duration_days: int
    product_groups: list[ProductGroupRequirement]
    total_kcal_available: float
    total_kcal_required: float
    total_person_days: float
    overall_status: str
    summary: str


class ProductThresholdResponse(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    min_quantity: float
    unit: str | None
    bemerkung: str | None = None


class WarehouseStockResponse(BaseModel):
    erzeugnisgruppe_id: int
    erzeugnisgruppe_name: str
    current_stock: float
    unit: str | None
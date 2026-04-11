from pydantic import BaseModel
from datetime import date


class OrtsverbandListItem(BaseModel):
    id: int
    name: str | None


class NaehrwerteSchema(BaseModel):
    kcal: float | None
    protein: float | None
    fett: float | None
    kohlenhydrate: float | None


class ProduktImFachSchema(BaseModel):
    stock_id: int
    produkt_id: int
    name: str | None
    marke: str | None
    menge: str | None
    erzeugnisgruppe: str | None
    mhd: date | None
    menge_eingelagert: int | None
    barcode: str | None
    naehrwerte: NaehrwerteSchema


class LagerfachSchema(BaseModel):
    id: int
    position: str | None
    max_kapazitaet: int | None
    produkte: list[ProduktImFachSchema]


class RegalSchema(BaseModel):
    id: int
    bezeichnung: str | None
    lagerfaecher: list[LagerfachSchema]


class LagerDetailSchema(BaseModel):
    id: int
    name: str | None
    regale: list[RegalSchema]


class LagerListItem(BaseModel):
    id: int
    name: str | None
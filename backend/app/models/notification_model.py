from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

class WarnungTyp(str, Enum):
    MHD_ROT = "MHD_ROT"
    MHD_GELB = "MHD_GELB"
    BESTAND_KRITISCH = "BESTAND_KRITISCH"

class BaseWarnungSchema(BaseModel):
    warnung_id: str
    typ: WarnungTyp
    produkt_id: int
    produkt_name: str
    marke: Optional[str] = None
    lagerort: str
    unit: str

class MhdWarnungSchema(BaseWarnungSchema):
    restmenge: float
    mhd: date
    tage_bis_ablauf: int

class BestandWarnungSchema(BaseWarnungSchema):
    restmenge: float
    schwellwert: float


class WarnungenResponse(BaseModel):
    ortsverband_id: int
    ortsverband_name: str

    mhd_warnungen: list[MhdWarnungSchema]
    bestand_warnungen: list[BestandWarnungSchema]

    gesamt_warnungen: int
    mhd_rot: int
    mhd_gelb: int
    bestand_kritisch: int

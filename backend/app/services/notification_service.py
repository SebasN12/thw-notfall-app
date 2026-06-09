import asyncio
from .mhd_warning_service import get_mhd_warnungen
from .bestand_warning_service import get_bestand_warnungen

async def get_warnungen(pool, ortsverband_id):
    mhd, bestand = await asyncio.gather(
        get_mhd_warnungen(pool, ortsverband_id),
        get_bestand_warnungen(pool, ortsverband_id),
    )

    return {
        "mhd_warnungen": mhd,
        "bestand_warnungen": bestand,
        "gesamt_warnungen": len(mhd) + len(bestand),
        "mhd_rot": sum(1 for w in mhd if w["typ"] == "MHD_ROT"),
        "mhd_gelb": sum(1 for w in mhd if w["typ"] == "MHD_GELB"),
        "bestand_kritisch": len(bestand),
    }
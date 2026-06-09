from fastapi import APIRouter, HTTPException
from backend.db.connection import get_pool
from backend.app.models.notification_model import (
    WarnungenResponse,
)
import backend.app.services.notification_service as notification_service

router = APIRouter(prefix="/notifications", tags=["Benachrichtigungen"])


@router.get("/{ortsverband_id}", response_model=WarnungenResponse)
async def get_warnungen(ortsverband_id: int):
    try:
        pool = get_pool()

        # Ortsverband holen
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT name FROM ortsverband WHERE id = %s",
                    (ortsverband_id,),
                )
                ov = await cur.fetchone()

        if not ov:
            raise HTTPException(status_code=404, detail="Ortsverband nicht gefunden")

        result = await notification_service.get_warnungen(pool, ortsverband_id)

        return WarnungenResponse(
            ortsverband_id=ortsverband_id,
            ortsverband_name=ov[0],
            **result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

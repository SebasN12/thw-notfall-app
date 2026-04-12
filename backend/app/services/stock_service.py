import aiomysql
from fastapi import HTTPException

from backend.app.models.stock_model import (
    StockRemoveRequest,
    StockAddRequest,
    StockActionResponse,
)


async def add_stock(
        pool: aiomysql.Pool,
        data: StockAddRequest,
) -> StockActionResponse:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await conn.begin()

                # Prüfen ob Lagerfach existiert
                await cur.execute(
                    "SELECT id FROM shelf_slot WHERE id = %s",
                    (data.shelf_slot_id,),
                )
                slot = await cur.fetchone()
                if not slot:
                    raise HTTPException(status_code=404, detail="Lagerfach nicht gefunden")

                # Prüfen ob Produkt existiert
                await cur.execute(
                    "SELECT id FROM product WHERE id = %s",
                    (data.product_id,),
                )
                product = await cur.fetchone()
                if not product:
                    raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

                # Prüfen ob Bestand mit gleichem Slot, Produkt und MHD schon existiert
                await cur.execute(
                    """
                    SELECT id, quantity
                    FROM stock
                    WHERE shelf_slot_id = %s
                      AND product_id = %s
                      AND (best_before <=> %s)
                    LIMIT 1
                    """,
                    (
                        data.shelf_slot_id,
                        data.product_id,
                        data.best_before,
                    ),
                )
                existing_stock = await cur.fetchone()

                if existing_stock:
                    new_quantity = (existing_stock["quantity"] or 0) + data.quantity

                    await cur.execute(
                        """
                        UPDATE stock
                        SET quantity = %s
                        WHERE id = %s
                        """,
                        (new_quantity, existing_stock["id"]),
                    )

                    stock_id = existing_stock["id"]

                    # optional stored_at aktualisieren, falls gesetzt
                    if data.stored_at is not None:
                        await cur.execute(
                            """
                            UPDATE stock
                            SET stored_at = %s
                            WHERE id = %s
                            """,
                            (data.stored_at, stock_id),
                        )

                else:
                    await cur.execute(
                        """
                        INSERT INTO stock (
                            shelf_slot_id,
                            product_id,
                            best_before,
                            stored_at,
                            zustand,
                            geoeffnet_am,
                            quantity
                        )
                        VALUES (%s, %s, %s, %s, 'geschlossen', NULL, %s)
                        """,
                        (
                            data.shelf_slot_id,
                            data.product_id,
                            data.best_before,
                            data.stored_at,
                            data.quantity,
                        ),
                    )
                    stock_id = cur.lastrowid
                    new_quantity = data.quantity

                # Bewegungs-Header schreiben
                await cur.execute(
                    """
                    INSERT INTO stock_movement_header (benutzer_id, aktion, grund)
                    VALUES (%s, 'EINLAGERUNG', %s)
                    """,
                    (data.user_id, data.reason),
                )
                header_id = cur.lastrowid

                # Bewegungs-Item schreiben
                await cur.execute(
                    """
                    INSERT INTO stock_movement_item (header_id, stock_id, bemerkung)
                    VALUES (%s, %s, %s)
                    """,
                    (header_id, stock_id, data.reason),
                )

                await conn.commit()

                return StockActionResponse(
                    message="Einlagerung erfolgreich gebucht",
                    stock_id=stock_id,
                    quantity=new_quantity,
                )

            except HTTPException:
                await conn.rollback()
                raise
            except Exception as e:
                await conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))


async def remove_stock(
        pool: aiomysql.Pool,
        data: StockRemoveRequest,
) -> StockActionResponse:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await conn.begin()

                await cur.execute(
                    """
                    SELECT id, quantity
                    FROM stock
                    WHERE id = %s
                    """,
                    (data.stock_id,),
                )
                stock = await cur.fetchone()

                if not stock:
                    raise HTTPException(status_code=404, detail="Bestand nicht gefunden")

                current_quantity = stock["quantity"] or 0

                if current_quantity < data.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail="Nicht genug Bestand vorhanden",
                    )

                new_quantity = current_quantity - data.quantity

                if new_quantity == 0:
                    await cur.execute(
                        "DELETE FROM stock WHERE id = %s",
                        (data.stock_id,),
                    )
                else:
                    await cur.execute(
                        """
                        UPDATE stock
                        SET quantity = %s
                        WHERE id = %s
                        """,
                        (new_quantity, data.stock_id),
                    )

                # Bewegungs-Header schreiben
                await cur.execute(
                    """
                    INSERT INTO stock_movement_header (benutzer_id, aktion, grund)
                    VALUES (%s, 'ENTNAHME', %s)
                    """,
                    (data.user_id, data.reason),
                )
                header_id = cur.lastrowid

                # Bewegungs-Item schreiben
                await cur.execute(
                    """
                    INSERT INTO stock_movement_item (header_id, stock_id, bemerkung)
                    VALUES (%s, %s, %s)
                    """,
                    (header_id, data.stock_id, data.reason),
                )

                await conn.commit()

                return StockActionResponse(
                    message="Entnahme erfolgreich gebucht",
                    stock_id=data.stock_id,
                    quantity=new_quantity,
                )

            except HTTPException:
                await conn.rollback()
                raise
            except Exception as e:
                await conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))
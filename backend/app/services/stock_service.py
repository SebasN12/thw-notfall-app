import aiomysql
from fastapi import HTTPException

from backend.app.models.stock_model import (
    StockRemoveRequest,
    StockAddRequest,
    StockActionResponse,
    StockDetailResponse,
    NaehrwerteSchema,
)


async def get_stock_detail(
    pool: aiomysql.Pool,
    stock_id: int,
) -> StockDetailResponse:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    s.id AS stock_id,
                    s.shelf_slot_id,
                    s.product_id,
                    s.best_before,

                    p.id AS produkt_id,
                    p.name,
                    p.marke,
                    p.menge,
                    p.lebensmittelgruppe AS erzeugnisgruppe,
                    p.barcode,
                    p.kcal,
                    p.protein,
                    p.fat AS fett,
                    p.carbs AS kohlenhydrate,

                    ss.id AS lagerfach_id,
                    ss.position AS lagerfach_position,

                    sh.id AS regal_id,
                    sh.label AS regal_bezeichnung,

                    w.id AS warehouse_id,
                    w.name AS warehouse_name
                FROM stock s
                JOIN product p
                    ON p.id = s.product_id
                JOIN shelf_slot ss
                    ON ss.id = s.shelf_slot_id
                JOIN shelf sh
                    ON sh.id = ss.shelf_id
                JOIN warehouse w
                    ON w.id = sh.warehouse_id
                WHERE s.id = %s
                """,
                (stock_id,),
            )

            base = await cur.fetchone()

            if not base:
                raise HTTPException(status_code=404, detail="Bestand nicht gefunden")

            await cur.execute(
                """
                SELECT
                    COUNT(*) AS menge_eingelagert,
                    SUM(zustand = 'geöffnet') AS menge_geoeffnet,
                    MIN(best_before) AS mhd,
                    MIN(id) AS stock_id
                FROM stock
                WHERE shelf_slot_id = %s
                  AND product_id = %s
                """,
                (
                    base["shelf_slot_id"],
                    base["product_id"],
                ),
            )

            aggregation = await cur.fetchone()

    return StockDetailResponse(
        stock_id=aggregation["stock_id"],
        produkt_id=base["produkt_id"],
        shelf_slot_id=base["shelf_slot_id"],

        name=base["name"],
        marke=base["marke"],
        menge=base["menge"],
        erzeugnisgruppe=base["erzeugnisgruppe"],
        mhd=aggregation["mhd"],
        menge_eingelagert=aggregation["menge_eingelagert"] or 0,
        menge_geoeffnet=aggregation["menge_geoeffnet"] or 0,
        barcode=base["barcode"],
        naehrwerte=NaehrwerteSchema(
            kcal=base["kcal"],
            protein=base["protein"],
            fett=base["fett"],
            kohlenhydrate=base["kohlenhydrate"],
        ),

        lagerfach_id=base["lagerfach_id"],
        lagerfach_position=base["lagerfach_position"],
        regal_id=base["regal_id"],
        regal_bezeichnung=base["regal_bezeichnung"],
        warehouse_id=base["warehouse_id"],
        warehouse_name=base["warehouse_name"],
    )


async def add_stock(
    pool: aiomysql.Pool,
    data: StockAddRequest,
) -> StockActionResponse:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await conn.begin()

                await cur.execute(
                    "SELECT id FROM shelf_slot WHERE id = %s",
                    (data.shelf_slot_id,),
                )
                slot = await cur.fetchone()

                if not slot:
                    raise HTTPException(status_code=404, detail="Lagerfach nicht gefunden")

                await cur.execute(
                    "SELECT id FROM product WHERE id = %s",
                    (data.product_id,),
                )
                product = await cur.fetchone()

                if not product:
                    raise HTTPException(status_code=404, detail="Produkt nicht gefunden")

                inserted_stock_ids: list[int] = []

                for _ in range(data.quantity):
                    await cur.execute(
                        """
                        INSERT INTO stock (
                            shelf_slot_id,
                            product_id,
                            best_before,
                            stored_at,
                            zustand,
                            geoeffnet_am
                        )
                        VALUES (%s, %s, %s, %s, 'geschlossen', NULL)
                        """,
                        (
                            data.shelf_slot_id,
                            data.product_id,
                            data.best_before,
                            data.stored_at,
                        ),
                    )

                    inserted_stock_ids.append(cur.lastrowid)

# TODO: Audit-Log temporär deaktiviert.
# Der DB-Trigger trg_movement_refresh auf stock_movement_header
# löst Fehler 1422 aus, weil refresh_pantrist_export_cache()
# innerhalb eines Triggers eine nicht erlaubte Operation ausführt.
#                await cur.execute(
#                    """
#                    INSERT INTO stock_movement_header (benutzer_id, aktion, grund)
#                    VALUES (%s, 'EINLAGERUNG', %s)
#                    """,
#                    (data.user_id, data.reason),
#                )
#                header_id = cur.lastrowid
#
#                for inserted_stock_id in inserted_stock_ids:
#                    await cur.execute(
#                        """
#                        INSERT INTO stock_movement_item (header_id, stock_id, bemerkung)
#                        VALUES (%s, %s, %s)
#                        """,
#                        (header_id, inserted_stock_id, data.reason),
#                    )

                await cur.execute(
                    """
                    SELECT COUNT(*) AS current_quantity
                    FROM stock
                    WHERE shelf_slot_id = %s
                      AND product_id = %s
                    """,
                    (
                        data.shelf_slot_id,
                        data.product_id,
                    ),
                )
                count_row = await cur.fetchone()

                await conn.commit()

                return StockActionResponse(
                    message="Einlagerung erfolgreich gebucht",
                    stock_id=inserted_stock_ids[0],
                    quantity=count_row["current_quantity"] or 0,
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
                    SELECT
                        id,
                        shelf_slot_id,
                        product_id
                    FROM stock
                    WHERE id = %s
                    """,
                    (data.stock_id,),
                )
                selected_stock = await cur.fetchone()

                if not selected_stock:
                    raise HTTPException(status_code=404, detail="Bestand nicht gefunden")

                await cur.execute(
                    """
                    SELECT id
                    FROM stock
                    WHERE shelf_slot_id = %s
                      AND product_id = %s
                    ORDER BY
                      best_before IS NULL,
                      best_before ASC,
                      id ASC
                    LIMIT %s
                    """,
                    (
                        selected_stock["shelf_slot_id"],
                        selected_stock["product_id"],
                        data.quantity,
                    ),
                )
                stocks_to_remove = await cur.fetchall()

                if len(stocks_to_remove) < data.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail="Nicht genug Bestand vorhanden",
                    )

                remove_ids = [row["id"] for row in stocks_to_remove]

                # TODO: Audit-Log temporär deaktiviert.
                # Der DB-Trigger trg_movement_refresh auf stock_movement_header
                # löst Fehler 1422 aus, weil refresh_pantrist_export_cache()
                # innerhalb eines Triggers eine nicht erlaubte Operation ausführt.
                #
                # Sobald der Trigger/Cache-Refresh repariert ist, sollen
                # stock_movement_header und stock_movement_item wieder beschrieben werden.
                #
                # await cur.execute(
                #     """
                #     INSERT INTO stock_movement_header (benutzer_id, aktion, grund)
                #     VALUES (%s, 'ENTNAHME', %s)
                #     """,
                #     (data.user_id, data.reason),
                # )
                # header_id = cur.lastrowid
                #
                # for remove_id in remove_ids:
                #     await cur.execute(
                #         """
                #         INSERT INTO stock_movement_item (header_id, stock_id, bemerkung)
                #         VALUES (%s, %s, %s)
                #         """,
                #         (header_id, remove_id, data.reason),
                #     )

                placeholders = ", ".join(["%s"] * len(remove_ids))

                await cur.execute(
                    f"""
                    DELETE FROM stock
                    WHERE id IN ({placeholders})
                    """,
                    remove_ids,
                )

                await cur.execute(
                    """
                    SELECT
                        COUNT(*) AS current_quantity,
                        MIN(id) AS next_stock_id
                    FROM stock
                    WHERE shelf_slot_id = %s
                      AND product_id = %s
                    """,
                    (
                        selected_stock["shelf_slot_id"],
                        selected_stock["product_id"],
                    ),
                )
                count_row = await cur.fetchone()

                current_quantity = count_row["current_quantity"] or 0
                next_stock_id = count_row["next_stock_id"] or data.stock_id

                await conn.commit()

                return StockActionResponse(
                    message="Entnahme erfolgreich gebucht",
                    stock_id=next_stock_id,
                    quantity=current_quantity,
                )

            except HTTPException:
                await conn.rollback()
                raise

            except Exception as e:
                await conn.rollback()
                raise HTTPException(status_code=500, detail=str(e))
import aiomysql
from backend.app.models.lager_model import (
    OrtsverbandListItem,
    LagerListItem,
    LagerDetailSchema,
    RegalSchema,
    LagerfachSchema,
    ProduktImFachSchema,
    NaehrwerteSchema,
)

async def get_alle_ortsverbaende(pool: aiomysql.Pool) -> list[OrtsverbandListItem]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT id, name FROM ortsverband ORDER BY name")
            rows = await cur.fetchall()
    return [OrtsverbandListItem(id=r["id"], name=r["name"]) for r in rows]


async def get_lager_by_ortsverband(
    pool: aiomysql.Pool, ortsverband_id: int
) -> list[LagerListItem]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, name FROM warehouse WHERE ortsverband_id = %s ORDER BY name",
                (ortsverband_id,),
            )
            rows = await cur.fetchall()
    return [LagerListItem(id=r["id"], name=r["name"]) for r in rows]


async def get_lager_detail(
    pool: aiomysql.Pool, warehouse_id: int
) -> LagerDetailSchema | None:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            await cur.execute(
                "SELECT id, name FROM warehouse WHERE id = %s",
                (warehouse_id,),
            )
            warehouse = await cur.fetchone()
            if not warehouse:
                return None

            await cur.execute(
                "SELECT id, label FROM shelf WHERE warehouse_id = %s ORDER BY label",
                (warehouse_id,),
            )
            regale_rows = await cur.fetchall()

            regale: list[RegalSchema] = []

            for regal in regale_rows:
                await cur.execute(
                    """
                    SELECT id, position, max_capacity
                    FROM shelf_slot
                    WHERE shelf_id = %s
                    ORDER BY position
                    """,
                    (regal["id"],),
                )
                slot_rows = await cur.fetchall()

                lagerfaecher: list[LagerfachSchema] = []

                for slot in slot_rows:
                    await cur.execute(
                        """
                        SELECT
                            MIN(s.id)                                           AS stock_id,
                            p.id                                                AS produkt_id,
                            p.name                                              AS name,
                            p.marke                                             AS marke,
                            p.menge                                             AS menge,
                            p.lebensmittelgruppe                                AS erzeugnisgruppe,
                            MIN(s.best_before)                                  AS mhd,
                            COUNT(s.id)                                         AS menge_eingelagert,
                            SUM(s.zustand = 'geöffnet')                         AS menge_geoeffnet,
                            p.barcode                                           AS barcode,
                            p.kcal                                              AS kcal,
                            p.protein                                           AS protein,
                            p.fat                                               AS fett,
                            p.carbs                                             AS kohlenhydrate
                        FROM stock s
                        JOIN product p ON s.product_id = p.id
                        WHERE s.shelf_slot_id = %s
                        GROUP BY
                            p.id, p.name, p.marke, p.menge, p.lebensmittelgruppe,
                            p.barcode, p.kcal, p.protein, p.fat, p.carbs
                        ORDER BY MIN(s.best_before) ASC
                        """,
                        (slot["id"],),
                    )
                    produkt_rows = await cur.fetchall()

                    produkte: list[ProduktImFachSchema] = [
                        ProduktImFachSchema(
                            stock_id=p["stock_id"],
                            produkt_id=p["produkt_id"],
                            name=p["name"],
                            marke=p["marke"],
                            menge=p["menge"],
                            erzeugnisgruppe=p["erzeugnisgruppe"],
                            mhd=p["mhd"],
                            menge_eingelagert=p["menge_eingelagert"],
                            menge_geoeffnet=p["menge_geoeffnet"],
                            barcode=p["barcode"],
                            naehrwerte=NaehrwerteSchema(
                                kcal=p["kcal"],
                                protein=p["protein"],
                                fett=p["fett"],
                                kohlenhydrate=p["kohlenhydrate"],
                            ),
                        )
                        for p in produkt_rows
                    ]

                    lagerfaecher.append(
                        LagerfachSchema(
                            id=slot["id"],
                            position=slot["position"],
                            max_kapazitaet=slot["max_capacity"],
                            produkte=produkte,
                        )
                    )

                regale.append(
                    RegalSchema(
                        id=regal["id"],
                        bezeichnung=regal["label"],
                        lagerfaecher=lagerfaecher,
                    )
                )

    return LagerDetailSchema(
        id=warehouse["id"],
        name=warehouse["name"],
        regale=regale,
    )
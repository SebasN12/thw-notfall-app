import aiomysql
from collections import defaultdict
from datetime import date
from backend.app.models.lager_model import (
    OrtsverbandListItem,
    LagerListItem,
    LagerDetailSchema,
    RegalSchema,
    LagerfachSchema,
    ProduktImFachSchema,
    NaehrwerteSchema,
    ExpiringProductSchema,
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

async def get_lager_detail_v2(
    pool: aiomysql.Pool, warehouse_id: int
) -> LagerDetailSchema | None:

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            await cur.execute(
                """
                SELECT id, name
                FROM warehouse
                WHERE id = %s
                """,
                (warehouse_id,),
            )

            warehouse = await cur.fetchone()

            if not warehouse:
                return None


            await cur.execute(
                """
                SELECT
                    sh.id                AS shelf_id,
                    sh.label             AS shelf_label,
                    ss.id                AS slot_id,
                    ss.position          AS slot_position,
                    ss.max_capacity      AS slot_capacity
                FROM shelf sh
                LEFT JOIN shelf_slot ss
                    ON ss.shelf_id = sh.id
                WHERE sh.warehouse_id = %s
                ORDER BY sh.label, ss.position
                """,
                (warehouse_id,),
            )

            slot_rows = await cur.fetchall()

            
            await cur.execute(
                """
                SELECT
                    s.shelf_slot_id                                    AS slot_id,

                    MIN(s.id)                                          AS stock_id,

                    p.id                                               AS produkt_id,
                    p.name                                             AS name,
                    p.marke                                            AS marke,
                    p.menge                                            AS menge,
                    p.lebensmittelgruppe                               AS erzeugnisgruppe,

                    MIN(s.best_before)                                 AS mhd,

                    COUNT(s.id)                                        AS menge_eingelagert,

                    SUM(s.zustand = 'geöffnet')                        AS menge_geoeffnet,

                    p.barcode                                          AS barcode,
                    p.kcal                                             AS kcal,
                    p.protein                                          AS protein,
                    p.fat                                              AS fett,
                    p.carbs                                            AS kohlenhydrate

                FROM stock s
                JOIN product p
                    ON p.id = s.product_id

                JOIN shelf_slot ss
                    ON ss.id = s.shelf_slot_id

                JOIN shelf sh
                    ON sh.id = ss.shelf_id

                WHERE sh.warehouse_id = %s

                GROUP BY
                    s.shelf_slot_id,
                    p.id,
                    p.name,
                    p.marke,
                    p.menge,
                    p.lebensmittelgruppe,
                    p.barcode,
                    p.kcal,
                    p.protein,
                    p.fat,
                    p.carbs

                ORDER BY
                    s.shelf_slot_id,
                    MIN(s.best_before)
                """,
                (warehouse_id,),
            )

            product_rows = await cur.fetchall()

    
    produkte_by_slot: dict[int, list[ProduktImFachSchema]] = defaultdict(list)

    for p in product_rows:
        produkte_by_slot[p["slot_id"]].append(
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
        )

    
    shelves_map: dict[int, RegalSchema] = {}

    for row in slot_rows:

        shelf_id = row["shelf_id"]

        if shelf_id not in shelves_map:
            shelves_map[shelf_id] = RegalSchema(
                id=shelf_id,
                bezeichnung=row["shelf_label"],
                lagerfaecher=[],
            )

        if row["slot_id"] is not None:
            shelves_map[shelf_id].lagerfaecher.append(
                LagerfachSchema(
                    id=row["slot_id"],
                    position=row["slot_position"],
                    max_kapazitaet=row["slot_capacity"],
                    produkte=produkte_by_slot.get(row["slot_id"], []),
                )
            )

    return LagerDetailSchema(
        id=warehouse["id"],
        name=warehouse["name"],
        regale=list(shelves_map.values()),
    )

async def get_expiring_products(
    pool: aiomysql.Pool,
    warehouse_id: int | None = None,
    days: int = 7,
) -> list[ExpiringProductSchema]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            query = """
                SELECT
                    s.id AS stock_id,
                    s.product_id,
                    p.name,
                    p.marke,
                    s.best_before AS mhd,
                    sh.id AS warehouse_id,
                    sh.label AS warehouse_name
                FROM stock s
                JOIN product p ON p.id = s.product_id
                JOIN shelf_slot ss ON ss.id = s.shelf_slot_id
                JOIN shelf sh ON sh.id = ss.shelf_id
                WHERE s.best_before IS NOT NULL
                  AND s.best_before <= DATE_ADD(CURDATE(), INTERVAL %s DAY)
            """

            params = [days]

            if warehouse_id is not None:
                query += " AND sh.warehouse_id = %s"
                params.append(warehouse_id)

            query += " ORDER BY s.best_before ASC"

            await cur.execute(query, params)
            rows = await cur.fetchall()

        result: list[ExpiringProductSchema] = []

        for r in rows:
            mhd = r["mhd"]

            days_left = None
            status = "unknown"

            if mhd:
                days_left = (mhd - date.today()).days

                if days_left <= 0:
                    status = "expired"
                elif days_left <= 3:
                    status = "critical"
                elif days_left <= 7:
                    status = "warning"
                else:
                    status = "ok"

            result.append(
                ExpiringProductSchema(
                    stock_id=r["stock_id"],
                    product_id=r["product_id"],
                    name=r["name"],
                    brand=r["marke"],
                    warehouse_id=r["warehouse_id"],
                    warehouse_name=r["warehouse_name"],
                    best_before=mhd,
                    days_left=days_left,
                    status=status,
                )
            )

    return result
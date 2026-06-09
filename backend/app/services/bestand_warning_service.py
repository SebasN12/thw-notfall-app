import aiomysql

async def get_bestand_warnungen(pool, ortsverband_id):
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            await cur.execute("""
                SELECT
                    p.id AS produkt_id,
                    p.name AS produkt_name,
                    p.marke,
                    p.menge AS unit,
                    COUNT(s.id) AS restmenge,
                    pt.min_quantity AS schwellwert,
                    CONCAT(w.name, ' › ', sh.label, ' › Fach ', ss.position) AS lagerort
                FROM product p
                JOIN stock s ON p.id = s.product_id
                JOIN shelf_slot ss ON s.shelf_slot_id = ss.id
                JOIN shelf sh ON ss.shelf_id = sh.id
                JOIN warehouse w ON sh.warehouse_id = w.id
                LEFT JOIN product_threshold pt ON pt.product_id = p.id
                WHERE w.ortsverband_id = %s
                  AND pt.min_quantity IS NOT NULL
                GROUP BY
                    p.id, p.name, p.marke, p.menge,
                    pt.min_quantity, w.name, sh.label, ss.position
                HAVING COUNT(s.id) < pt.min_quantity
            """, (ortsverband_id,))

            rows = await cur.fetchall()

    warnungen = []

    for r in rows:
        warnungen.append({
            "warnung_id": f"bestand_{r['produkt_id']}",
            "typ": "BESTAND_KRITISCH",
            "produkt_id": r["produkt_id"],
            "produkt_name": r["produkt_name"],
            "marke": r["marke"],
            "lagerort": r["lagerort"],
            "restmenge": float(r["restmenge"]),
            "unit": r["unit"] or "Stk",
            "schwellwert": float(r["schwellwert"]),
        })

    return warnungen
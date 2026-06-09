import aiomysql
from datetime import date, timedelta

async def get_mhd_warnungen(pool, ortsverband_id):
    heute = date.today()
    gelb_grenze = heute + timedelta(days=90)

    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:

            await cur.execute("""
                SELECT
                    MIN(s.id) AS stock_id,
                    p.id AS produkt_id,
                    p.name AS produkt_name,
                    p.marke,
                    p.menge AS unit,
                    s.best_before AS mhd,
                    COUNT(s.id) AS restmenge,
                    CONCAT(w.name, ' › ', sh.label, ' › Fach ', ss.position) AS lagerort
                FROM stock s
                JOIN product p ON s.product_id = p.id
                JOIN shelf_slot ss ON s.shelf_slot_id = ss.id
                JOIN shelf sh ON ss.shelf_id = sh.id
                JOIN warehouse w ON sh.warehouse_id = w.id
                WHERE w.ortsverband_id = %s
                AND s.best_before IS NOT NULL
                AND s.best_before <= %s
                GROUP BY
                    p.id, p.name, p.marke, p.menge,
                    s.best_before,
                    w.name, sh.label, ss.position
                ORDER BY s.best_before ASC
            """, (ortsverband_id, gelb_grenze))

            rows = await cur.fetchall()

    warnungen = []

    for r in rows:
        tage = (r["mhd"] - heute).days

        typ = "MHD_ROT" if tage < 30 else "MHD_GELB"

        warnungen.append({
            "warnung_id": f"mhd_{r['stock_id']}",
            "typ": typ,
            "produkt_id": r["produkt_id"],
            "produkt_name": r["produkt_name"],
            "marke": r["marke"],
            "lagerort": r["lagerort"],
            "restmenge": float(r["restmenge"]),
            "unit": r["unit"] or "Stk",
            "mhd": r["mhd"],
            "tage_bis_ablauf": tage,
        })

    return warnungen
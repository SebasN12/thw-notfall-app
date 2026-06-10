import aiomysql
from datetime import datetime

from backend.app.models.supply_model import (
    SupplyCalculatorResponse,
    ProductGroupRequirement,
    ProductThresholdResponse,
    WarehouseStockResponse,
)


DAILY_KCAL_PER_PERSON = 2200

COVERAGE_GREEN = 1.0
COVERAGE_YELLOW = 0.5


def get_status(coverage_ratio: float) -> str:
    if coverage_ratio >= COVERAGE_GREEN:
        return "GREEN"
    if coverage_ratio >= COVERAGE_YELLOW:
        return "YELLOW"
    return "RED"


def generate_summary(
    num_persons: int,
    duration_days: int,
    total_person_days: float,
    overall_status: str,
) -> str:
    status_text = {
        "GREEN": "ausreichend ✓",
        "YELLOW": "knapp",
        "RED": "kritisch ⚠",
    }

    status_label = status_text.get(overall_status, overall_status)
    requested_person_days = num_persons * duration_days

    if total_person_days >= requested_person_days:
        possible_days = int(total_person_days / num_persons) if num_persons > 0 else 0
        return (
            f"Vorrat ist {status_label}. Mit {int(total_person_days)} Personentagen "
            f"können {num_persons} Personen {possible_days} Tage lang versorgt werden."
        )

    shortfall = requested_person_days - total_person_days

    return (
        f"Vorrat ist {status_label}. Es fehlen ~{int(shortfall)} Personentage "
        f"für die angeforderte Versorgung."
    )


async def get_ortsverband_name(pool: aiomysql.Pool, ortsverband_id: int) -> str | None:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT name FROM ortsverband WHERE id = %s",
                (ortsverband_id,),
            )
            result = await cur.fetchone()

    return result["name"] if result else None


async def get_product_groups_with_thresholds(pool: aiomysql.Pool) -> list[dict]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    eg.id AS erzeugnisgruppe_id,
                    eg.name AS erzeugnisgruppe_name,
                    eg.unit,
                    eg.bemerkung,
                    COALESCE(
                        eg.min_quantity,
                        AVG(pt.min_quantity),
                        0
                    ) AS min_quantity,
                    COALESCE(AVG(p.kcal), 0) AS kcal_per_unit
                FROM erzeugnisgruppe eg
                LEFT JOIN product p
                    ON p.erzeugnisgruppe_id = eg.id
                LEFT JOIN product_threshold pt
                    ON pt.product_id = p.id
                GROUP BY
                    eg.id,
                    eg.name,
                    eg.unit,
                    eg.bemerkung,
                    eg.min_quantity
                ORDER BY eg.name
                """
            )

            return await cur.fetchall()


async def get_current_stocks(pool: aiomysql.Pool, ortsverband_id: int) -> dict[int, float]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    eg.id AS erzeugnisgruppe_id,
                    COUNT(s.id) AS total_quantity
                FROM erzeugnisgruppe eg
                LEFT JOIN product p
                    ON p.erzeugnisgruppe_id = eg.id
                LEFT JOIN stock s
                    ON p.id = s.product_id
                LEFT JOIN shelf_slot ss
                    ON s.shelf_slot_id = ss.id
                LEFT JOIN shelf sh
                    ON ss.shelf_id = sh.id
                LEFT JOIN warehouse w
                    ON sh.warehouse_id = w.id
                WHERE w.ortsverband_id = %s
                GROUP BY eg.id
                """,
                (ortsverband_id,),
            )

            rows = await cur.fetchall()

    stock_dict: dict[int, float] = {}

    for row in rows:
        stock_dict[row["erzeugnisgruppe_id"]] = float(row["total_quantity"] or 0)

    return stock_dict


async def calculate_supply(
    pool: aiomysql.Pool,
    ortsverband_id: int,
    num_persons: int,
    duration_days: int,
) -> SupplyCalculatorResponse:
    ortsverband_name = await get_ortsverband_name(pool, ortsverband_id)

    if not ortsverband_name:
        raise ValueError(f"Ortsverband mit ID {ortsverband_id} nicht gefunden")

    product_groups_data = await get_product_groups_with_thresholds(pool)
    current_stocks = await get_current_stocks(pool, ortsverband_id)

    product_group_results: list[ProductGroupRequirement] = []

    total_kcal_available = 0.0
    total_kcal_required = 0.0

    for group in product_groups_data:
        erzeugnisgruppe_id = group["erzeugnisgruppe_id"]
        erzeugnisgruppe_name = group["erzeugnisgruppe_name"]
        min_quantity = float(group["min_quantity"] or 0)
        unit = group["unit"]
        kcal_per_unit = float(group["kcal_per_unit"] or 0)

        current_stock = current_stocks.get(erzeugnisgruppe_id, 0.0)

        required_amount = min_quantity * num_persons * duration_days

        kcal_required_group = required_amount * kcal_per_unit
        kcal_available_group = current_stock * kcal_per_unit

        total_kcal_required += kcal_required_group
        total_kcal_available += kcal_available_group

        if required_amount > 0:
            coverage_percentage = (current_stock / required_amount) * 100
        else:
            coverage_percentage = 100.0

        coverage_ratio = coverage_percentage / 100
        status = get_status(coverage_ratio)

        product_group_results.append(
            ProductGroupRequirement(
                erzeugnisgruppe_id=erzeugnisgruppe_id,
                erzeugnisgruppe_name=erzeugnisgruppe_name,
                unit=unit,
                min_quantity=round(min_quantity, 2),
                required_amount=round(required_amount, 2),
                current_stock=round(current_stock, 2),
                coverage_percentage=round(coverage_percentage, 1),
                status=status,
                kcal_available=round(kcal_available_group, 2),
                kcal_required=round(kcal_required_group, 2),
            )
        )

    if DAILY_KCAL_PER_PERSON > 0:
        total_person_days = round(total_kcal_available / DAILY_KCAL_PER_PERSON, 2)
    else:
        total_person_days = 0.0

    if total_kcal_required > 0:
        total_coverage_ratio = total_kcal_available / total_kcal_required
    else:
        total_coverage_ratio = 1.0

    overall_status = get_status(total_coverage_ratio)

    summary = generate_summary(
        num_persons=num_persons,
        duration_days=duration_days,
        total_person_days=total_person_days,
        overall_status=overall_status,
    )

    return SupplyCalculatorResponse(
        ortsverband_id=ortsverband_id,
        ortsverband_name=ortsverband_name,
        calculation_date=datetime.now().isoformat(),
        input_persons=num_persons,
        input_duration_days=duration_days,
        product_groups=product_group_results,
        total_kcal_available=round(total_kcal_available, 2),
        total_kcal_required=round(total_kcal_required, 2),
        total_person_days=total_person_days,
        overall_status=overall_status,
        summary=summary,
    )


async def get_product_thresholds(pool: aiomysql.Pool) -> list[ProductThresholdResponse]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    eg.id AS erzeugnisgruppe_id,
                    eg.name AS erzeugnisgruppe_name,
                    COALESCE(
                        eg.min_quantity,
                        AVG(pt.min_quantity),
                        0
                    ) AS min_quantity,
                    eg.unit,
                    eg.bemerkung
                FROM erzeugnisgruppe eg
                LEFT JOIN product p
                    ON p.erzeugnisgruppe_id = eg.id
                LEFT JOIN product_threshold pt
                    ON pt.product_id = p.id
                GROUP BY
                    eg.id,
                    eg.name,
                    eg.unit,
                    eg.bemerkung,
                    eg.min_quantity
                ORDER BY eg.name
                """
            )

            rows = await cur.fetchall()

    return [
        ProductThresholdResponse(
            erzeugnisgruppe_id=row["erzeugnisgruppe_id"],
            erzeugnisgruppe_name=row["erzeugnisgruppe_name"],
            min_quantity=float(row["min_quantity"] or 0),
            unit=row["unit"],
            bemerkung=row.get("bemerkung"),
        )
        for row in rows
    ]

    return [
        ProductThresholdResponse(
            erzeugnisgruppe_id=row["erzeugnisgruppe_id"],
            erzeugnisgruppe_name=row["erzeugnisgruppe_name"],
            min_quantity=float(row["min_quantity"] or 0),
            unit=row["unit"],
            bemerkung=row.get("bemerkung"),
        )
        for row in rows
    ]


async def get_warehouse_stock(
    pool: aiomysql.Pool,
    ortsverband_id: int,
) -> list[WarehouseStockResponse]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                """
                SELECT
                    eg.id AS erzeugnisgruppe_id,
                    eg.name AS erzeugnisgruppe_name,
                    COUNT(s.id) AS current_stock,
                    eg.unit
                FROM erzeugnisgruppe eg
                LEFT JOIN product p
                    ON p.erzeugnisgruppe_id = eg.id
                LEFT JOIN stock s
                    ON p.id = s.product_id
                LEFT JOIN shelf_slot ss
                    ON s.shelf_slot_id = ss.id
                LEFT JOIN shelf sh
                    ON ss.shelf_id = sh.id
                LEFT JOIN warehouse w
                    ON sh.warehouse_id = w.id
                WHERE w.ortsverband_id = %s
                GROUP BY eg.id, eg.name, eg.unit
                ORDER BY eg.name
                """,
                (ortsverband_id,),
            )

            rows = await cur.fetchall()

    return [
        WarehouseStockResponse(
            erzeugnisgruppe_id=row["erzeugnisgruppe_id"],
            erzeugnisgruppe_name=row["erzeugnisgruppe_name"],
            current_stock=float(row["current_stock"] or 0),
            unit=row["unit"],
        )
        for row in rows
    ]
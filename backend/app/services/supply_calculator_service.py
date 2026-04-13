import mysql.connector
from mysql.connector import Error
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from models import (
    SupplyCalculatorResponse,
    ProductGroupRequirement,
    ProductThresholdResponse,
    WarehouseStockResponse,
)


class SupplyCalculatorService:

    # BBK Empfehlung 2023: 2200 kcal pro Person und Tag
    DAILY_KCAL_PER_PERSON = 2200

    # Status-Schwellenwerte
    COVERAGE_GREEN = 1.0  # >= 100%
    COVERAGE_YELLOW = 0.5  # >= 50%
    # RED < 50%

    def __init__(self, db_connection):
        self.db = db_connection

    def calculate_supply(
        self, ortsverband_id: int, num_persons: int, duration_days: int
    ) -> SupplyCalculatorResponse:
       
        ortsverband_name = self._get_ortsverband_name(ortsverband_id)
        if not ortsverband_name:
            raise ValueError(f"Ortsverband mit ID {ortsverband_id} nicht gefunden")

        product_groups_data = self._get_product_groups_with_thresholds()
        current_stocks = self._get_current_stocks(ortsverband_id)

        product_group_results: List[ProductGroupRequirement] = []
        total_kcal_available = 0.0
        total_kcal_required = 0.0

        for group in product_groups_data:
            erzeugnisgruppe_id = group["erzeugnisgruppe_id"]
            erzeugnisgruppe_name = group["erzeugnisgruppe_name"]
            min_quantity = group["min_quantity"]
            unit = group["unit"]
            kcal_per_unit = group.get("kcal_per_unit", 0.0)  # Fallback wenn null

            # Get current stock for this group
            current_stock = current_stocks.get(erzeugnisgruppe_id, 0.0)

            # Formula: Bedarf = min_quantity × Personen × Tage
            required_amount = min_quantity * num_persons * duration_days

            # Calculate kcal
            kcal_required_group = required_amount * kcal_per_unit
            kcal_available_group = current_stock * kcal_per_unit

            total_kcal_required += kcal_required_group
            total_kcal_available += kcal_available_group

            # Calculate coverage percentage
            if required_amount > 0:
                coverage_percentage = (current_stock / required_amount) * 100
            else:
                coverage_percentage = 100.0

            # Determine status
            coverage_ratio = coverage_percentage / 100
            if coverage_ratio >= self.COVERAGE_GREEN:
                status = "GREEN"
            elif coverage_ratio >= self.COVERAGE_YELLOW:
                status = "YELLOW"
            else:
                status = "RED"

            product_group_results.append(
                ProductGroupRequirement(
                    erzeugnisgruppe_id=erzeugnisgruppe_id,
                    erzeugnisgruppe_name=erzeugnisgruppe_name,
                    unit=unit,
                    min_quantity=min_quantity,
                    required_amount=round(required_amount, 2),
                    current_stock=round(current_stock, 2),
                    coverage_percentage=round(coverage_percentage, 1),
                    status=status,
                    kcal_available=round(kcal_available_group, 2),
                    kcal_required=round(kcal_required_group, 2),
                )
            )

      
        if self.DAILY_KCAL_PER_PERSON > 0:
            total_person_days = round(
                total_kcal_available / self.DAILY_KCAL_PER_PERSON, 2
            )
        else:
            total_person_days = 0.0

        if total_kcal_required > 0:
            total_coverage_ratio = total_kcal_available / total_kcal_required
        else:
            total_coverage_ratio = 1.0

        if total_coverage_ratio >= 1.0:
            overall_status = "GREEN"
        elif total_coverage_ratio >= 0.5:
            overall_status = "YELLOW"
        else:
            overall_status = "RED"
            
        summary = self._generate_summary(
            num_persons, duration_days, total_person_days, overall_status
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

    def _get_ortsverband_name(self, ortsverband_id: int) -> Optional[str]:
        try:
            cursor = self.db.cursor(dictionary=True)
            query = "SELECT name FROM ortsverband WHERE id = %s"
            cursor.execute(query, (ortsverband_id,))
            result = cursor.fetchone()
            cursor.close()
            return result["name"] if result else None
        except Error as e:
            raise Error(f"Datenbankfehler beim Abrufen des Ortsverbands: {e}")

    def _get_product_groups_with_thresholds(
        self,
    ) -> List[Dict]:
        
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
            SELECT 
                eg.id as erzeugnisgruppe_id,
                eg.name as erzeugnisgruppe_name,
                eg.unit,
                pt.min_quantity,
                pt.unit as threshold_unit,
                COALESCE(p.kcal, 0) as kcal_per_unit
            FROM erzeugnisgruppe eg
            LEFT JOIN product_threshold pt ON eg.id = pt.erzeugnisgruppe_id
            LEFT JOIN product p ON pt.product_id = p.id
            WHERE pt.min_quantity IS NOT NULL
            ORDER BY eg.name
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            raise Error(
                f"Datenbankfehler beim Abrufen der Erzeugnisgruppen: {e}"
            )

    def _get_current_stocks(self, ortsverband_id: int) -> Dict[int, float]:
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
            SELECT 
                eg.id as erzeugnisgruppe_id,
                COALESCE(SUM(s.quantity), 0) as total_quantity
            FROM erzeugnisgruppe eg
            LEFT JOIN product p ON eg.id = p.erzeugnisgruppe_id
            LEFT JOIN stock s ON p.id = s.product_id
            LEFT JOIN shelf_slot ss ON s.shelf_slot_id = ss.id
            LEFT JOIN shelf sh ON ss.shelf_id = sh.id
            WHERE sh.warehouse_id IN (
                SELECT w.id FROM warehouse w 
                WHERE w.ortsverband_id = %s
            )
            GROUP BY eg.id
            """
            cursor.execute(query, (ortsverband_id,))
            results = cursor.fetchall()
            cursor.close()

            stock_dict = {}
            for row in results:
                stock_dict[row["erzeugnisgruppe_id"]] = row["total_quantity"]

            return stock_dict
        except Error as e:
            raise Error(f"Datenbankfehler beim Abrufen der Bestände: {e}")

    def _generate_summary(
        self, num_persons: int, duration_days: int, total_person_days: float, overall_status: str
    ) -> str:
        status_text = {
            "GREEN": "ausreichend ✓",
            "YELLOW": "knapp",
            "RED": "kritisch ⚠",
        }

        status_label = status_text.get(overall_status, overall_status)

        if total_person_days >= num_persons * duration_days:
            return f"Vorrat ist {status_label}. Mit {int(total_person_days)} Personentagen kann {num_persons} Personen {int(total_person_days / num_persons)} Tage lang versorgt werden."
        else:
            shortfall = num_persons * duration_days - total_person_days
            return f"Vorrat ist {status_label}. Es fehlen ~{int(shortfall)} Personentage für die angeforderte Versorgung."

    def get_product_thresholds(self) -> List[ProductThresholdResponse]:
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
            SELECT 
                eg.id as erzeugnisgruppe_id,
                eg.name as erzeugnisgruppe_name,
                pt.min_quantity,
                eg.unit,
                eg.bemerkung
            FROM erzeugnisgruppe eg
            LEFT JOIN product_threshold pt ON eg.id = pt.erzeugnisgruppe_id
            WHERE pt.min_quantity IS NOT NULL
            ORDER BY eg.name
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            return [
                ProductThresholdResponse(
                    erzeugnisgruppe_id=row["erzeugnisgruppe_id"],
                    erzeugnisgruppe_name=row["erzeugnisgruppe_name"],
                    min_quantity=row["min_quantity"],
                    unit=row["unit"],
                    bemerkung=row.get("bemerkung"),
                )
                for row in results
            ]
        except Error as e:
            raise Error(f"Datenbankfehler beim Abrufen der Schwellwerte: {e}")

    def get_warehouse_stock(
        self, ortsverband_id: int
    ) -> List[WarehouseStockResponse]:
        try:
            cursor = self.db.cursor(dictionary=True)
            query = """
            SELECT 
                eg.id as erzeugnisgruppe_id,
                eg.name as erzeugnisgruppe_name,
                COALESCE(SUM(s.quantity), 0) as current_stock,
                eg.unit
            FROM erzeugnisgruppe eg
            LEFT JOIN product p ON eg.id = p.erzeugnisgruppe_id
            LEFT JOIN stock s ON p.id = s.product_id
            LEFT JOIN shelf_slot ss ON s.shelf_slot_id = ss.id
            LEFT JOIN shelf sh ON ss.shelf_id = sh.id
            WHERE sh.warehouse_id IN (
                SELECT w.id FROM warehouse w 
                WHERE w.ortsverband_id = %s
            )
            GROUP BY eg.id, eg.name, eg.unit
            ORDER BY eg.name
            """
            cursor.execute(query, (ortsverband_id,))
            results = cursor.fetchall()
            cursor.close()

            return [
                WarehouseStockResponse(
                    erzeugnisgruppe_id=row["erzeugnisgruppe_id"],
                    erzeugnisgruppe_name=row["erzeugnisgruppe_name"],
                    current_stock=row["current_stock"],
                    unit=row["unit"],
                )
                for row in results
            ]
        except Error as e:
            raise Error(f"Datenbankfehler beim Abrufen des Lagerstands: {e}")

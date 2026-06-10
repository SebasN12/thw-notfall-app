export interface Ortsverband {
  id: number
  name: string | null
}

export interface LagerListItem {
  id: number
  name: string | null
}

export interface Produkt {
  stock_id: number
  produkt_id: number
  name: string | null
  marke: string | null
  menge: string | null
  erzeugnisgruppe: string | null
  mhd: string | null
  menge_eingelagert: number | null
  menge_geoeffnet: number | null
  barcode: string | null
  naehrwerte: {
    kcal: number | null
    protein: number | null
    fett: number | null
    kohlenhydrate: number | null
  }
}

export interface Lagerfach {
  id: number
  position: string | null
  max_kapazitaet: number | null
  produkte: Produkt[]
}

export interface Regal {
  id: number
  bezeichnung: string | null
  lagerfaecher: Lagerfach[]
}

export interface LagerDetail {
  id: number
  name: string | null
  regale: Regal[]
}

export type AlertType = 'mhd-red' | 'mhd-yellow' | 'stock-low'

export interface InventoryAlert {
  id: string
  type: AlertType
  product: Produkt
  warehouseName: string
  shelfName: string
  slotName: string
  daysUntilExpiry?: number
}

export interface InventoryStats {
  warehouseCount: number
  shelfCount: number
  slotCount: number
  productCount: number
  totalUnits: number
}

export interface ProductLocation {
  product: Produkt
  warehouseName: string
  shelfName: string
  slotName: string
}

export interface CalculatorResultRow {
  category: string
  requiredKg: number
  availableKg: number
  coveragePercent: number
  status: 'green' | 'yellow' | 'red'
}

export interface CalculatorSummary {
  personDaysByCalories: number
  totalAvailableKg: number
}

export type SupplyStatus = 'GREEN' | 'YELLOW' | 'RED'

export interface SupplyCalculatorRequest {
  ortsverband_id: number
  num_persons: number
  duration_days: number
}

export interface SupplyProductGroup {
  erzeugnisgruppe_id: number
  erzeugnisgruppe_name: string
  unit: string | null
  min_quantity: number
  required_amount: number
  current_stock: number
  coverage_percentage: number
  status: SupplyStatus
  kcal_available: number
  kcal_required: number
}

export interface SupplyCalculatorResponse {
  ortsverband_id: number
  ortsverband_name: string
  calculation_date: string
  input_persons: number
  input_duration_days: number
  product_groups: SupplyProductGroup[]
  total_kcal_available: number
  total_kcal_required: number
  total_person_days: number
  overall_status: SupplyStatus
  summary: string
}

export interface BookingPayload {
  productId: number
  amount: number
  reason?: string
}

export interface AddStockPayload extends BookingPayload {}

export interface RemoveStockPayload extends BookingPayload {}

export interface StockDetail {
  stock_id: number
  produkt_id: number
  shelf_slot_id: number
  name: string | null
  marke: string | null
  menge: string | null
  erzeugnisgruppe: string | null
  mhd: string | null
  menge_eingelagert: number
  menge_geoeffnet: number
  barcode: string | null
  naehrwerte: {
    kcal: number | null
    protein: number | null
    fett: number | null
    kohlenhydrate: number | null
  }

  lagerfach_id: number
  lagerfach_position: string | null
  regal_id: number
  regal_bezeichnung: string | null
  warehouse_id: number
  warehouse_name: string | null
}

export interface StockRemoveRequest {
  stock_id: number
  user_id: number
  quantity: number
  reason?: string | null
}

export interface StockAddRequest {
  shelf_slot_id: number
  product_id: number
  user_id: number
  quantity: number
  best_before?: string | null
  stored_at?: string | null
  reason?: string | null
}

export interface StockActionResponse {
  message: string
  stock_id: number
  quantity: number
}
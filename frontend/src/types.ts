export interface Product {
  id: number
  name: string
  brand: string
  packSize: string
  category: string
  menge: number
  weightKg: number
  mhd: string
  barcode: string
  kcal: number
  protein: number
  fat: number
  carbs: number
  threshold: number
}

export interface Slot {
  id: number
  name: string
  products: Product[]
}

export interface Shelf {
  id: number
  name: string
  slots: Slot[]
}

export interface Warehouse {
  id: number
  name: string
  shelves: Shelf[]
}

export type AlertType = 'mhd-red' | 'mhd-yellow' | 'stock-low'

export interface InventoryAlert {
  id: string
  type: AlertType
  product: Product
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
  product: Product
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

export interface BookingPayload {
  productId: number
  amount: number
  reason?: string
}

export interface AddStockPayload extends BookingPayload {}

export interface RemoveStockPayload extends BookingPayload {}
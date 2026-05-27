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

export interface BookingPayload {
  productId: number
  amount: number
  reason?: string
}

export interface AddStockPayload extends BookingPayload {}

export interface RemoveStockPayload extends BookingPayload {}
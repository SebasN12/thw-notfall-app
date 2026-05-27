import { warehouses } from '../data/mockData'
import type {
  AddStockPayload,
  CalculatorResultRow,
  CalculatorSummary,
  InventoryAlert,
  InventoryStats,
  Product,
  ProductLocation,
  RemoveStockPayload,
  Warehouse,
} from '../types'

function delay(ms = 150): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

function cloneDeep<T>(value: T): T {
  return JSON.parse(JSON.stringify(value))
}

function startOfToday(): Date {
  const now = new Date()
  return new Date(now.getFullYear(), now.getMonth(), now.getDate())
}

function diffInDays(targetDate: string): number {
  const today = startOfToday()
  const target = new Date(targetDate)
  const msPerDay = 1000 * 60 * 60 * 24
  return Math.ceil((target.getTime() - today.getTime()) / msPerDay)
}

function getAllProductsWithLocationInternal(): ProductLocation[] {
  const result: ProductLocation[] = []

  for (const warehouse of warehouses) {
    for (const shelf of warehouse.shelves) {
      for (const slot of shelf.slots) {
        for (const product of slot.products) {
          result.push({
            product,
            warehouseName: warehouse.name,
            shelfName: shelf.name,
            slotName: slot.name,
          })
        }
      }
    }
  }

  return result
}

function findProductInternal(productId: number): Product | null {
  for (const warehouse of warehouses) {
    for (const shelf of warehouse.shelves) {
      for (const slot of shelf.slots) {
        const product = slot.products.find((item) => item.id === productId)
        if (product) return product
      }
    }
  }

  return null
}

function findProductByBarcodeInternal(barcode: string): Product | null {
  for (const warehouse of warehouses) {
    for (const shelf of warehouse.shelves) {
      for (const slot of shelf.slots) {
        const product = slot.products.find((item) => item.barcode === barcode)
        if (product) return product
      }
    }
  }

  return null
}

function findSlotInternal(slotId: number) {
  for (const warehouse of warehouses) {
    for (const shelf of warehouse.shelves) {
      for (const slot of shelf.slots) {
        if (slot.id === slotId) {
          return slot
        }
      }
    }
  }
  return null
}

function getInventoryStatsInternal(): InventoryStats {
  let shelfCount = 0
  let slotCount = 0
  let productCount = 0
  let totalUnits = 0

  for (const warehouse of warehouses) {
    shelfCount += warehouse.shelves.length

    for (const shelf of warehouse.shelves) {
      slotCount += shelf.slots.length

      for (const slot of shelf.slots) {
        productCount += slot.products.length

        for (const product of slot.products) {
          totalUnits += product.menge
        }
      }
    }
  }

  return {
    warehouseCount: warehouses.length,
    shelfCount,
    slotCount,
    productCount,
    totalUnits,
  }
}

function getInventoryAlertsInternal(): InventoryAlert[] {
  const alerts: InventoryAlert[] = []

  for (const warehouse of warehouses) {
    for (const shelf of warehouse.shelves) {
      for (const slot of shelf.slots) {
        for (const product of slot.products) {
          const days = diffInDays(product.mhd)

          if (days < 30) {
            alerts.push({
              id: `mhd-red-${product.id}`,
              type: 'mhd-red',
              product,
              warehouseName: warehouse.name,
              shelfName: shelf.name,
              slotName: slot.name,
              daysUntilExpiry: days,
            })
          } else if (days < 90) {
            alerts.push({
              id: `mhd-yellow-${product.id}`,
              type: 'mhd-yellow',
              product,
              warehouseName: warehouse.name,
              shelfName: shelf.name,
              slotName: slot.name,
              daysUntilExpiry: days,
            })
          }

          if (product.menge < product.threshold) {
            alerts.push({
              id: `stock-low-${product.id}`,
              type: 'stock-low',
              product,
              warehouseName: warehouse.name,
              shelfName: shelf.name,
              slotName: slot.name,
            })
          }
        }
      }
    }
  }

  const order = {
    'mhd-red': 0,
    'stock-low': 1,
    'mhd-yellow': 2,
  }

  return alerts.sort((a, b) => order[a.type] - order[b.type])
}

function calculateCoverageInternal(persons: number, days: number): {
  rows: CalculatorResultRow[]
  summary: CalculatorSummary
} {
  const products = getAllProductsWithLocationInternal()

  const requirementGroups = [
    { category: 'Getreideprodukte', minKgPerPersonPerDay: 0.33 },
    { category: 'Getränke', minKgPerPersonPerDay: 2.0 },
    { category: 'Fertiggerichte', minKgPerPersonPerDay: 0.2 },
  ]

  const rows: CalculatorResultRow[] = requirementGroups.map((group) => {
    const requiredKg = group.minKgPerPersonPerDay * persons * days

    const availableKg = products
      .filter((item) => item.product.category === group.category)
      .reduce((sum, item) => sum + item.product.menge * item.product.weightKg, 0)

    const coveragePercent = requiredKg > 0 ? (availableKg / requiredKg) * 100 : 0

    let status: 'green' | 'yellow' | 'red' = 'green'
    if (coveragePercent < 50) {
      status = 'red'
    } else if (coveragePercent < 80) {
      status = 'yellow'
    }

    return {
      category: group.category,
      requiredKg: Math.round(requiredKg * 100) / 100,
      availableKg: Math.round(availableKg * 100) / 100,
      coveragePercent: Math.round(coveragePercent * 100) / 100,
      status,
    }
  })

  const totalAvailableKg = Math.round(
    products.reduce((sum, item) => sum + item.product.menge * item.product.weightKg, 0) * 100,
  ) / 100

  const totalAvailableCalories = products.reduce((sum, item) => {
    return sum + item.product.menge * item.product.weightKg * 1000 * (item.product.kcal / 100)
  }, 0)

  const personDaysByCalories = Math.round((totalAvailableCalories / 2200) * 100) / 100

  return {
    rows,
    summary: {
      totalAvailableKg,
      personDaysByCalories,
    },
  }
}

type CreateProductPayload = Omit<Product, 'id' | 'menge'> & {
  menge: number
  slotId: number
}

export const mockApi = {
  async getWarehouses(): Promise<Warehouse[]> {
    await delay()
    return cloneDeep(warehouses)
  },

  async getProductById(productId: number): Promise<Product | null> {
    await delay()
    const product = findProductInternal(productId)
    return product ? cloneDeep(product) : null
  },

  async findProductByBarcode(barcode: string): Promise<Product | null> {
    await delay()
    const product = findProductByBarcodeInternal(barcode)
    return product ? cloneDeep(product) : null
  },

  async createProductAndStore(payload: CreateProductPayload): Promise<Product | null> {
    await delay()

    const slot = findSlotInternal(payload.slotId)
    if (!slot) return null

    const maxId = Math.max(...getAllProductsWithLocationInternal().map((item) => item.product.id), 0)

    const newProduct: Product = {
      id: maxId + 1,
      name: payload.name,
      brand: payload.brand,
      packSize: payload.packSize,
      category: payload.category,
      menge: payload.menge,
      weightKg: payload.weightKg,
      mhd: payload.mhd,
      barcode: payload.barcode,
      kcal: payload.kcal,
      protein: payload.protein,
      fat: payload.fat,
      carbs: payload.carbs,
      threshold: payload.threshold,
    }

    slot.products.push(newProduct)
    return cloneDeep(newProduct)
  },

  async storeKnownProductInSlot(payload: {
    productId: number
    slotId: number
    menge: number
    mhd?: string
  }): Promise<Product | null> {
    await delay()

    const product = findProductInternal(payload.productId)
    if (!product) return null

    product.menge += payload.menge
    if (payload.mhd) {
      product.mhd = payload.mhd
    }

    return cloneDeep(product)
  },

  async getInventoryStats(): Promise<InventoryStats> {
    await delay()
    return cloneDeep(getInventoryStatsInternal())
  },

  async getInventoryAlerts(): Promise<InventoryAlert[]> {
    await delay()
    return cloneDeep(getInventoryAlertsInternal())
  },

  async calculateCoverage(persons: number, days: number): Promise<{
    rows: CalculatorResultRow[]
    summary: CalculatorSummary
  }> {
    await delay()
    return cloneDeep(calculateCoverageInternal(persons, days))
  },

  async removeStock(payload: RemoveStockPayload): Promise<Product | null> {
    await delay()
    const product = findProductInternal(payload.productId)
    if (!product) return null

    product.menge = Math.max(0, product.menge - payload.amount)
    return cloneDeep(product)
  },

  async addStock(payload: AddStockPayload): Promise<Product | null> {
    await delay()
    const product = findProductInternal(payload.productId)
    if (!product) return null

    product.menge += payload.amount
    return cloneDeep(product)
  },

  async acknowledgeAlert(_alertId: string): Promise<{ success: true }> {
    await delay()
    return { success: true }
  },
}
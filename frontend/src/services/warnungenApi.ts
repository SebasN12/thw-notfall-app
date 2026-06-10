import http from './http'
import type { LagerListItem } from '../types'
import { getWarehouses } from './lagerApi'

export interface ExpiringProduct {
  stock_id: number
  product_id: number
  name: string
  brand: string | null
  warehouse_id: number
  warehouse_name: string
  best_before: string | null
  days_left: number | null
  status: 'expired' | 'critical' | 'warning' | 'ok' | 'unknown'
}

export async function getExpiringProductsByWarehouse(
  warehouseId: number,
  days = 30,
): Promise<ExpiringProduct[]> {
  const response = await http.get<ExpiringProduct[]>(
    `/${warehouseId}/expiring-products`,
    {
      params: {
        expiring_within_days: days,
      },
    },
  )

  return response.data
}

export async function getExpiringProductsByOrtsverband(
  ortsverbandId: number,
  days = 30,
): Promise<ExpiringProduct[]> {
  const warehouses: LagerListItem[] = await getWarehouses(ortsverbandId)

  const results = await Promise.all(
    warehouses.map((warehouse) =>
      getExpiringProductsByWarehouse(warehouse.id, days),
    ),
  )

  return results.flat()
}
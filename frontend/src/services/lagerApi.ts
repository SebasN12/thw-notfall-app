import http from './http'
import type { LagerDetail, LagerListItem, Ortsverband } from '../types'

export async function getOrtsverbaende(): Promise<Ortsverband[]> {
  const response = await http.get<Ortsverband[]>('/ortsverbaende')
  return response.data
}

export async function getWarehouses(ortsverbandId: number): Promise<LagerListItem[]> {
  const response = await http.get<LagerListItem[]>(
    `/ortsverbaende/${ortsverbandId}/warehouses`,
  )

  return response.data
}

export async function getWarehouseDetail(warehouseId: number): Promise<LagerDetail> {
  const response = await http.get<LagerDetail>(`/warehouses/${warehouseId}`)
  return response.data
}
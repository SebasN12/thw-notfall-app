import http from './http'
import type {
  StockActionResponse,
  StockAddRequest,
  StockDetail,
  StockRemoveRequest,
} from '../types'

export async function getStockDetail(stockId: number): Promise<StockDetail> {
  const response = await http.get<StockDetail>(`/stock/${stockId}`)
  return response.data
}

export async function removeStock(
  data: StockRemoveRequest,
): Promise<StockActionResponse> {
  const response = await http.post<StockActionResponse>('/stock/remove', data)
  return response.data
}

export async function addStock(
  data: StockAddRequest,
): Promise<StockActionResponse> {
  const response = await http.post<StockActionResponse>('/stock/add', data)
  return response.data
}
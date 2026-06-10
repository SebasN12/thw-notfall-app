import http from './http'
import type {
  CalculatorResultRow,
  CalculatorSummary,
  SupplyCalculatorRequest,
  SupplyCalculatorResponse,
  SupplyStatus,
} from '../types'

function mapStatus(status: SupplyStatus): 'green' | 'yellow' | 'red' {
  if (status === 'GREEN') return 'green'
  if (status === 'YELLOW') return 'yellow'
  return 'red'
}

export interface CalculatorViewResult {
  rows: CalculatorResultRow[]
  summary: CalculatorSummary
  backendSummary: string
  overallStatus: 'green' | 'yellow' | 'red'
  raw: SupplyCalculatorResponse
}

export async function calculateSupply(
  ortsverbandId: number,
  persons: number,
  days: number,
): Promise<CalculatorViewResult> {
  const payload: SupplyCalculatorRequest = {
    ortsverband_id: ortsverbandId,
    num_persons: persons,
    duration_days: days,
  }

  const response = await http.post<SupplyCalculatorResponse>(
    '/api/v1/supply-calculator/calculate',
    payload,
  )

  const data = response.data

  return {
    rows: data.product_groups.map((group) => ({
      category: group.erzeugnisgruppe_name,
      requiredKg: group.required_amount,
      availableKg: group.current_stock,
      coveragePercent: group.coverage_percentage,
      status: mapStatus(group.status),
    })),

    summary: {
      personDaysByCalories: data.total_person_days,
      totalAvailableKg: data.product_groups.reduce(
        (sum, group) => sum + group.current_stock,
        0,
      ),
    },

    backendSummary: data.summary,
    overallStatus: mapStatus(data.overall_status),
    raw: data,
  }
}
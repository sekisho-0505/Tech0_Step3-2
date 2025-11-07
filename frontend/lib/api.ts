export interface PricePattern {
  margin_rate: number;
  price_per_kg: number;
  profit_per_kg: number;
}

export interface PriceSimulationResponse {
  recommended_price_per_kg: number;
  gross_profit_per_kg: number;
  gross_profit_total: number;
  margin_rate: number;
  price_patterns: PricePattern[];
  guard: {
    min_allowed_price_per_kg: number;
    is_below_min: boolean;
  };
}

export interface BreakEvenResponse {
  year_month: string;
  fixed_costs: number;
  current_revenue: number;
  variable_cost_rate: number;
  gross_margin_rate: number;
  break_even_revenue: number;
  achievement_rate: number;
  delta_revenue: number;
  status: 'safe' | 'warning' | 'danger';
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export async function calculatePriceSimulation(payload: {
  product_name: string;
  unit_cost_per_kg: number;
  target_margin_rate: number;
  quantity_kg?: number | null;
}): Promise<PriceSimulationResponse> {
  const res = await fetch(`${API_BASE_URL}/api/price-simulations/calculate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    throw new Error('価格計算に失敗しました');
  }
  return res.json();
}

export async function getBreakEven(yearMonth: string): Promise<BreakEvenResponse> {
  const res = await fetch(`${API_BASE_URL}/api/break-even/current?year_month=${yearMonth}`);
  if (!res.ok) {
    throw new Error('分岐点情報の取得に失敗しました');
  }
  return res.json();
}

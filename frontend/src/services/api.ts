import axios from 'axios';
import type { ArbitrageOpportunity } from '../types/arbitrage';

const BASE_URL = '/api';

const client = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
});

export interface FetchArbitrageParams {
  min_spread?: number;
  exchanges?: string[];
  sort_by?: 'spread' | 'apr';
  symbol?: string;
}

export async function fetchArbitrageOpportunities(
  params: FetchArbitrageParams = {}
): Promise<ArbitrageOpportunity[]> {
  const queryParams: Record<string, string | number | string[]> = {};

  if (params.min_spread !== undefined && params.min_spread > 0) {
    queryParams.min_spread = params.min_spread;
  }
  if (params.exchanges && params.exchanges.length > 0) {
    queryParams.exchanges = params.exchanges;
  }
  if (params.sort_by) {
    queryParams.sort_by = params.sort_by;
  }
  if (params.symbol) {
    queryParams.symbol = params.symbol.toUpperCase();
  }

  const response = await client.get('/arbitrage-opportunities', {
    params: queryParams,
    // FastAPI expects repeated query params for lists
    paramsSerializer: (p) => {
      const parts: string[] = [];
      Object.entries(p).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach((v) => parts.push(`${key}=${encodeURIComponent(v)}`));
        } else {
          parts.push(`${key}=${encodeURIComponent(String(value))}`);
        }
      });
      return parts.join('&');
    },
  });

  if (!response.data.success) {
    throw new Error(response.data.error || 'Failed to fetch arbitrage data');
  }

  return response.data.data as ArbitrageOpportunity[];
}

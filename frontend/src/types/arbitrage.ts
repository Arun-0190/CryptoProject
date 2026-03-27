// TypeScript types mirroring the backend Pydantic models

export type Confidence = 'High' | 'Medium' | 'Low';
export type Risk = 'Low' | 'Medium' | 'High';
export type ExchangeName = 'Binance' | 'Bybit' | 'OKX' | 'Bitget';
export type SortField = 'funding_diff' | 'apr' | 'long_rate' | 'short_rate' | 'oi';

export interface ArbitrageOpportunity {
  symbol: string;
  long_exchange: ExchangeName;
  short_exchange: ExchangeName;
  long_rate: number;
  short_rate: number;
  funding_diff: number;
  apr: number;
  mark_price: number | null;
  oi: number | null;
  next_funding_time: number | null;
  confidence: Confidence;
  risk: Risk;
}

export interface ArbitrageResponse {
  success: boolean;
  timestamp: number;
  count: number;
  data: ArbitrageOpportunity[];
}

export interface Filters {
  exchange: string;      // 'All' | exchange name
  minSpread: number;
  sortBy: SortField;
  sortDir: 'asc' | 'desc';
  symbol: string;
}

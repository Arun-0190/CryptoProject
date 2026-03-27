import { create } from 'zustand';
import type { ArbitrageOpportunity, Filters, SortField } from '../types/arbitrage';
import { fetchArbitrageOpportunities } from '../services/api';

// --- Exchange allow-list (frontend filter only) ---
// Rows are shown when at least one side trades on an allowed exchange.
// Delta Exchange India, CoinSwitch, CoinDCX are listed for UI completeness;
// actual API data only carries Binance, Bybit, OKX, Bitget.
export const ALLOWED_EXCHANGES = [
  'Binance',
  'Delta Exchange India',
  'CoinSwitch',
  'CoinDCX',
];

/** Keep rows where at least one leg is on an allowed exchange. */
function filterArbitrageData(data: ArbitrageOpportunity[]): ArbitrageOpportunity[] {
  return data.filter(
    (item) =>
      ALLOWED_EXCHANGES.includes(item.long_exchange) ||
      ALLOWED_EXCHANGES.includes(item.short_exchange),
  );
}

/** Merge incoming data into existing array – preserves row identity so React
 * does not unmount/remount rows and avoids table flicker. */
function mergeArbitrageData(
  prev: ArbitrageOpportunity[],
  next: ArbitrageOpportunity[],
): ArbitrageOpportunity[] {
  const map = new Map(prev.map((item) => [`${item.symbol}|${item.long_exchange}|${item.short_exchange}`, item]));
  return next.map((newItem) => {
    const key = `${newItem.symbol}|${newItem.long_exchange}|${newItem.short_exchange}`;
    const old = map.get(key);
    // Spread old then new so all numeric fields update smoothly
    return old ? { ...old, ...newItem } : newItem;
  });
}

interface ArbitrageStore {
  // Data
  opportunities: ArbitrageOpportunity[];
  loading: boolean;
  error: string | null;
  lastUpdated: number | null;

  // UI State
  positionSize: number;
  filters: Filters;

  // Actions
  setPositionSize: (size: number) => void;
  setFilter: <K extends keyof Filters>(key: K, value: Filters[K]) => void;
  resetFilters: () => void;
  fetchData: () => Promise<void>;
}

const DEFAULT_FILTERS: Filters = {
  exchange: 'All',
  minSpread: 0,
  sortBy: 'funding_diff',
  sortDir: 'desc',
  symbol: '',
};

export const useStore = create<ArbitrageStore>((set, get) => ({
  opportunities: [],
  loading: false,
  error: null,
  lastUpdated: null,

  positionSize: 10000,
  filters: { ...DEFAULT_FILTERS },

  setPositionSize: (size) => set({ positionSize: size }),

  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),

  resetFilters: () => set({ filters: { ...DEFAULT_FILTERS } }),

  fetchData: async () => {
    // Only show skeleton spinner on the very first load (empty table)
    set((state) => ({ loading: state.opportunities.length === 0, error: null }));
    try {
      const { filters } = get();

      const apiSortBy = filters.sortBy === 'apr' ? 'apr' : 'spread';
      const exchanges =
        filters.exchange === 'All' ? undefined : [filters.exchange];

      const raw = await fetchArbitrageOpportunities({
        min_spread: filters.minSpread > 0 ? filters.minSpread : undefined,
        exchanges,
        sort_by: apiSortBy,
        symbol: filters.symbol || undefined,
      });

      // Apply frontend allow-list filter
      const data = filterArbitrageData(raw);

      // Client-side sort
      let sorted = [...data];
      if (filters.sortBy !== 'funding_diff' && filters.sortBy !== 'apr') {
        const field = filters.sortBy as SortField;
        sorted = sorted.sort((a, b) => {
          const aVal = (a[field] as number | null) ?? -Infinity;
          const bVal = (b[field] as number | null) ?? -Infinity;
          return filters.sortDir === 'desc' ? bVal - aVal : aVal - bVal;
        });
      } else if (filters.sortDir === 'asc') {
        sorted.reverse();
      }

      // Merge into existing state → no full re-render
      set((state) => ({
        opportunities: mergeArbitrageData(state.opportunities, sorted),
        loading: false,
        lastUpdated: Date.now(),
      }));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      set({ error: message, loading: false });
    }
  },
}));

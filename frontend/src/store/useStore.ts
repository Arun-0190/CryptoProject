import { create } from 'zustand';
import type { ArbitrageOpportunity, Filters, SortField } from '../types/arbitrage';
import { fetchArbitrageOpportunities } from '../services/api';

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
    set({ loading: true, error: null });
    try {
      const { filters } = get();

      const apiSortBy = filters.sortBy === 'apr' ? 'apr' : 'spread';
      const exchanges =
        filters.exchange === 'All' ? undefined : [filters.exchange];

      const data = await fetchArbitrageOpportunities({
        min_spread: filters.minSpread > 0 ? filters.minSpread : undefined,
        exchanges,
        sort_by: apiSortBy,
        symbol: filters.symbol || undefined,
      });

      // Client-side sort for fields not natively supported in API
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

      set({ opportunities: sorted, loading: false, lastUpdated: Date.now() });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      set({ error: message, loading: false });
    }
  },
}));

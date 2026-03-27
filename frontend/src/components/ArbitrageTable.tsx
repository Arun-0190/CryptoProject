import React from 'react';
import { useStore } from '../store/useStore';
import TableRow from './TableRow';
import Loader, { ErrorState, EmptyState } from './Loader';
import type { SortField } from '../types/arbitrage';

const COLUMNS: { label: string; field?: SortField; align?: 'right' }[] = [
  { label: '#' },
  { label: 'Symbol' },
  { label: 'Strategy' },
  { label: 'Long Rate', field: 'long_rate' },
  { label: 'Short Rate', field: 'short_rate' },
  { label: 'Spread', field: 'funding_diff' },
  { label: 'APR', field: 'apr' },
  { label: 'PnL / 8h' },
  { label: 'Annual Rev.' },
  { label: 'Open Interest', field: 'oi' },
  { label: 'Next Funding' },
  { label: 'Confidence' },
  { label: 'Risk' },
  { label: '' },
];

const ArbitrageTable: React.FC = () => {
  const { opportunities, loading, error, positionSize, filters, fetchData, setFilter } = useStore();

  const handleSort = (field: SortField | undefined) => {
    if (!field) return;
    if (filters.sortBy === field) {
      setFilter('sortDir', filters.sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setFilter('sortBy', field);
      setFilter('sortDir', 'desc');
    }
  };

  return (
    <div className="table-container">
      <table className="arb-table">
        <thead>
          <tr>
            {COLUMNS.map((col) => (
              <th
                key={col.label}
                className={filters.sortBy === col.field ? 'sorted' : ''}
                style={{
                  cursor: col.field ? 'pointer' : 'default',
                  textAlign: col.align ?? 'left',
                }}
                onClick={() => col.field && handleSort(col.field)}
              >
                {col.label}
                {col.field && filters.sortBy === col.field && (
                  <span style={{ marginLeft: 4, fontSize: 10 }}>
                    {filters.sortDir === 'desc' ? '▼' : '▲'}
                  </span>
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {loading && <Loader rows={14} />}
          {!loading && error && (
            <ErrorState message={error} onRetry={fetchData} />
          )}
          {!loading && !error && opportunities.length === 0 && <EmptyState />}
          {!loading &&
            !error &&
            opportunities.map((opp, i) => (
              <TableRow
                key={`${opp.symbol}-${opp.long_exchange}-${opp.short_exchange}`}
                opp={opp}
                rank={i + 1}
                positionSize={positionSize}
                isTop={i < 5}
              />
            ))}
        </tbody>
      </table>
    </div>
  );
};

export default ArbitrageTable;

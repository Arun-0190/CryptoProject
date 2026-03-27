import React from 'react';
import { useStore } from '../store/useStore';
import type { SortField } from '../types/arbitrage';

const EXCHANGES = ['All', 'Binance', 'Bybit', 'OKX', 'Bitget'];

const Filters: React.FC = () => {
  const { filters, setFilter, positionSize, setPositionSize, resetFilters } = useStore();

  const handlePositionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value.replace(/[^0-9.]/g, ''));
    if (!isNaN(val) && val > 0) setPositionSize(val);
  };

  const handleSortToggle = (field: SortField) => {
    if (filters.sortBy === field) {
      setFilter('sortDir', filters.sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setFilter('sortBy', field);
      setFilter('sortDir', 'desc');
    }
  };

  return (
    <div
      style={{
        background: 'var(--bg-card)',
        borderBottom: '1px solid var(--border)',
        padding: '0 24px',
      }}
    >
      <div style={{ maxWidth: 1440, margin: '0 auto' }}>
        {/* Exchange filter row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            padding: '12px 0',
            borderBottom: '1px solid var(--border)',
            flexWrap: 'wrap',
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--text-secondary)', marginRight: 4, flexShrink: 0 }}>
            Exchange:
          </span>
          {EXCHANGES.map((ex) => (
            <button
              key={ex}
              className={`filter-btn ${filters.exchange === ex ? 'active' : ''}`}
              onClick={() => setFilter('exchange', ex)}
            >
              {ex}
            </button>
          ))}

          <div style={{ flex: 1 }} />

          {/* Min spread */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', flexShrink: 0 }}>
              Min Spread:
            </span>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'var(--bg-input)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                overflow: 'hidden',
              }}
            >
              <input
                type="number"
                min={0}
                step={0.01}
                value={filters.minSpread}
                onChange={(e) => setFilter('minSpread', parseFloat(e.target.value) || 0)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-primary)',
                  fontSize: 12,
                  width: 60,
                  padding: '5px 8px',
                  outline: 'none',
                }}
              />
              <span style={{ fontSize: 11, color: 'var(--text-muted)', paddingRight: 8 }}>%</span>
            </div>
          </div>

          {/* Symbol search */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              background: 'var(--bg-input)',
              border: '1px solid var(--border)',
              borderRadius: 6,
              padding: '5px 10px',
              gap: 6,
            }}
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <input
              placeholder="Symbol..."
              value={filters.symbol}
              onChange={(e) => setFilter('symbol', e.target.value.toUpperCase())}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--text-primary)',
                fontSize: 12,
                width: 90,
                outline: 'none',
              }}
            />
          </div>

          {/* Reset */}
          {(filters.exchange !== 'All' || filters.minSpread > 0 || filters.symbol) && (
            <button
              onClick={resetFilters}
              style={{
                background: 'transparent',
                border: '1px solid var(--border)',
                borderRadius: 6,
                color: 'var(--text-secondary)',
                fontSize: 11,
                padding: '4px 10px',
                cursor: 'pointer',
              }}
            >
              ✕ Reset
            </button>
          )}
        </div>

        {/* Sort row + position size */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '10px 0',
            flexWrap: 'wrap',
          }}
        >
          <span style={{ fontSize: 12, color: 'var(--text-secondary)' }}>Sort by:</span>
          {(
            [
              { key: 'funding_diff', label: 'Spread' },
              { key: 'apr', label: 'APR' },
              { key: 'oi', label: 'Open Interest' },
            ] as { key: SortField; label: string }[]
          ).map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleSortToggle(key)}
              className={`filter-btn ${filters.sortBy === key ? 'active' : ''}`}
              style={{ display: 'flex', alignItems: 'center', gap: 4 }}
            >
              {label}
              {filters.sortBy === key && (
                <span style={{ fontSize: 10 }}>{filters.sortDir === 'desc' ? '▼' : '▲'}</span>
              )}
            </button>
          ))}

          <div style={{ flex: 1 }} />

          {/* Position size */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontSize: 12, color: 'var(--text-secondary)', flexShrink: 0 }}>
              Position Size:
            </span>
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                background: 'var(--bg-input)',
                border: '1px solid var(--border)',
                borderRadius: 6,
                overflow: 'hidden',
              }}
            >
              <span style={{ fontSize: 12, color: 'var(--text-muted)', paddingLeft: 8 }}>$</span>
              <input
                type="number"
                min={0}
                step={1000}
                value={positionSize}
                onChange={handlePositionChange}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-primary)',
                  fontSize: 13,
                  fontWeight: 600,
                  width: 90,
                  padding: '6px 8px',
                  outline: 'none',
                }}
              />
            </div>
            {[5000, 10000, 50000].map((v) => (
              <button
                key={v}
                onClick={() => setPositionSize(v)}
                className={`filter-btn ${positionSize === v ? 'active' : ''}`}
                style={{ padding: '4px 10px', fontSize: 11 }}
              >
                ${(v / 1000).toFixed(0)}K
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Filters;

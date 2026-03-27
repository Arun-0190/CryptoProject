import React, { useEffect, useRef } from 'react';
import { useStore } from '../store/useStore';
import Filters from '../components/Filters';
import ArbitrageTable from '../components/ArbitrageTable';

const REFRESH_INTERVAL_MS = 60_000; // 60 second live refresh

const Dashboard: React.FC = () => {
  const { fetchData, opportunities, loading, lastUpdated, filters } = useStore();
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Initial fetch + refetch when filters change
  useEffect(() => {
    fetchData();
  }, [filters.exchange, filters.minSpread, filters.sortBy, filters.sortDir, filters.symbol]);

  // Auto-refresh every 60 seconds (no loading spinner on background refresh)
  useEffect(() => {
    intervalRef.current = setInterval(() => {
      fetchData();
    }, REFRESH_INTERVAL_MS);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [fetchData]);

  const secondsAgo = lastUpdated
    ? Math.floor((Date.now() - lastUpdated) / 1000)
    : null;

  return (
    <div style={{ maxWidth: 1440, margin: '0 auto', padding: '24px 24px 0' }}>
      {/* Page header */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          marginBottom: 20,
          flexWrap: 'wrap',
          gap: 12,
        }}
      >
        <div>
          <h1
            style={{
              fontSize: 22,
              fontWeight: 700,
              color: 'white',
              letterSpacing: '-0.02em',
              marginBottom: 4,
            }}
          >
            Funding Rate Arbitrage
          </h1>
          <p style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Real-time cross-exchange funding rate arbitrage opportunities across Binance, Bybit, OKX
            and Bitget.
          </p>
        </div>

        {/* Stats bar */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
              Opportunities
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: 'white' }}>
              {loading ? '—' : opportunities.length}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
              Best APR
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--green)' }}>
              {loading || !opportunities.length
                ? '—'
                : `${Math.max(...opportunities.map((o) => o.apr)).toFixed(1)}%`}
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
              Best Spread
            </div>
            <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--green)' }}>
              {loading || !opportunities.length
                ? '—'
                : `${Math.max(...opportunities.map((o) => o.funding_diff)).toFixed(4)}%`}
            </div>
          </div>

          {/* Live indicator */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 6,
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '8px 14px',
            }}
          >
            <div className="live-dot" />
            <div>
              <div style={{ fontSize: 11, color: 'var(--green)', fontWeight: 600 }}>LIVE</div>
              <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>
                {secondsAgo !== null ? `${secondsAgo}s ago` : 'loading…'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div
        style={{
          background: 'var(--bg-card)',
          borderRadius: '12px 12px 0 0',
          border: '1px solid var(--border)',
          borderBottom: 'none',
          overflow: 'hidden',
        }}
      >
        <Filters />
      </div>

      {/* Table */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border)',
          borderRadius: '0 0 12px 12px',
          overflow: 'hidden',
          marginBottom: 40,
        }}
      >
        <ArbitrageTable />
      </div>
    </div>
  );
};

export default Dashboard;

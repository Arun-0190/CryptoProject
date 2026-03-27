import React, { memo, useEffect, useRef, useState } from 'react';
import type { ArbitrageOpportunity } from '../types/arbitrage';
import { ConfidenceBadge, RiskBadge } from './StatusBadge';
import {
  formatRate,
  formatAPR,
  formatOI,
  formatPrice,
  formatCountdown,
  computePnL,
  computeAnnualRevenue,
  getBaseToken,
} from '../utils/format';

/**
 * Flashes green when `value` changes, then smoothly fades back.
 * Conveys "this number just updated" without full row re-mount.
 */
const AnimatedValue: React.FC<{
  value: string;
  baseColor?: string;
  style?: React.CSSProperties;
}> = ({ value, baseColor = 'inherit', style }) => {
  const [highlight, setHighlight] = useState(false);
  const prevRef = useRef(value);

  useEffect(() => {
    if (prevRef.current !== value) {
      prevRef.current = value;
      setHighlight(true);
      const t = setTimeout(() => setHighlight(false), 500);
      return () => clearTimeout(t);
    }
  }, [value]);

  return (
    <span
      style={{
        color: highlight ? '#0ECB81' : baseColor,
        transition: 'color 0.5s ease',
        fontVariantNumeric: 'tabular-nums',
        ...style,
      }}
    >
      {value}
    </span>
  );
};

interface TableRowProps {
  opp: ArbitrageOpportunity;
  rank: number;
  positionSize: number;
  isTop: boolean;
}

const EXCHANGE_COLORS: Record<string, string> = {
  Binance: '#F0B90B',
  Bybit: '#F7A600',
  OKX: '#1E90FF',
  Bitget: '#00C5C5',
  'Delta Exchange India': '#7C3AED',
  CoinSwitch: '#E63946',
  CoinDCX: '#2563EB',
};

const ExchangeDot: React.FC<{ name: string }> = ({ name }) => (
  <span
    style={{
      display: 'inline-block',
      width: 6,
      height: 6,
      borderRadius: '50%',
      background: EXCHANGE_COLORS[name] ?? '#8A9BB0',
      marginRight: 4,
      verticalAlign: 'middle',
    }}
  />
);

const TableRow: React.FC<TableRowProps> = memo(({ opp, rank, positionSize, isTop }) => {
  const [hovered, setHovered] = useState(false);
  const pnl = computePnL(opp.funding_diff, positionSize);
  const annualRevenue = computeAnnualRevenue(opp.funding_diff, positionSize);
  const baseToken = getBaseToken(opp.symbol);

  const rowStyle: React.CSSProperties = {
    background: isTop
      ? 'rgba(37, 99, 235, 0.035)'
      : hovered
      ? 'var(--bg-card-hover)'
      : 'transparent',
    transition: 'background 0.12s',
    cursor: 'default',
  };

  return (
    <tr
      style={rowStyle}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    >
      {/* Rank */}
      <td style={{ padding: '10px 16px', color: 'var(--text-muted)', fontSize: 12, width: 40 }}>
        {rank}
      </td>

      {/* Symbol */}
      <td style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: '50%',
              background: `linear-gradient(135deg, ${EXCHANGE_COLORS[opp.long_exchange] ?? '#2563EB'}, #7C3AED)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 10,
              fontWeight: 700,
              color: 'white',
              flexShrink: 0,
            }}
          >
            {baseToken.slice(0, 2)}
          </div>
          <div>
            <div style={{ fontWeight: 600, fontSize: 13, color: 'white' }}>{opp.symbol}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
              {formatPrice(opp.mark_price)}
            </div>
          </div>
        </div>
      </td>

      {/* Strategy */}
      <td style={{ padding: '10px 16px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <span className="exchange-badge long">
            <ExchangeDot name={opp.long_exchange} />
            ↑ Long {opp.long_exchange}
          </span>
          <span className="exchange-badge short">
            <ExchangeDot name={opp.short_exchange} />
            ↓ Short {opp.short_exchange}
          </span>
        </div>
      </td>

      {/* Long Rate */}
      <td style={{ padding: '10px 16px' }}>
        <span
          style={{
            color: opp.long_rate < 0 ? 'var(--green)' : opp.long_rate > 0 ? 'var(--red)' : 'var(--text-secondary)',
            fontWeight: 500,
            fontSize: 13,
          }}
        >
          {formatRate(opp.long_rate)}
        </span>
      </td>

      {/* Short Rate */}
      <td style={{ padding: '10px 16px' }}>
        <span
          style={{
            color: opp.short_rate > 0 ? 'var(--green)' : opp.short_rate < 0 ? 'var(--red)' : 'var(--text-secondary)',
            fontWeight: 500,
            fontSize: 13,
          }}
        >
          {formatRate(opp.short_rate)}
        </span>
      </td>

      {/* Spread */}
      <td style={{ padding: '10px 16px' }}>
        <AnimatedValue
          value={formatRate(opp.funding_diff)}
          baseColor="var(--green)"
          style={{ fontWeight: 700, fontSize: 13 }}
        />
      </td>

      {/* APR */}
      <td style={{ padding: '10px 16px' }}>
        <AnimatedValue
          value={formatAPR(opp.apr)}
          baseColor={opp.apr > 100 ? '#0ECB81' : opp.apr > 20 ? '#F0B90B' : 'var(--text-primary)'}
          style={{ fontWeight: 600, fontSize: 13 }}
        />
      </td>

      {/* PnL per period */}
      <td style={{ padding: '10px 16px' }}>
        <AnimatedValue
          value={`+$${pnl.toFixed(2)}`}
          baseColor="var(--green)"
          style={{ fontWeight: 500, fontSize: 13 }}
        />
      </td>

      {/* Annual Revenue */}
      <td style={{ padding: '10px 16px' }}>
        <AnimatedValue
          value={`+$${annualRevenue.toFixed(0)}`}
          baseColor="var(--green)"
          style={{ fontWeight: 500, fontSize: 13 }}
        />
      </td>

      {/* OI */}
      <td style={{ padding: '10px 16px', color: 'var(--text-secondary)', fontSize: 12 }}>
        {formatOI(opp.oi)}
      </td>

      {/* Funding countdown */}
      <td style={{ padding: '10px 16px', color: 'var(--text-muted)', fontSize: 12 }}>
        {formatCountdown(opp.next_funding_time)}
      </td>

      {/* Confidence */}
      <td style={{ padding: '10px 16px' }}>
        <ConfidenceBadge value={opp.confidence} />
      </td>

      {/* Risk */}
      <td style={{ padding: '10px 16px' }}>
        <RiskBadge value={opp.risk} />
      </td>

      {/* Trade button */}
      <td style={{ padding: '10px 16px' }}>
        <button
          style={{
            background: 'transparent',
            border: '1px solid var(--border-light)',
            borderRadius: 6,
            color: '#2563EB',
            fontSize: 11,
            fontWeight: 600,
            padding: '4px 12px',
            cursor: 'pointer',
            transition: 'all 0.15s',
            whiteSpace: 'nowrap',
          }}
          onMouseEnter={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = '#2563EB';
            (e.currentTarget as HTMLButtonElement).style.color = 'white';
            (e.currentTarget as HTMLButtonElement).style.borderColor = '#2563EB';
          }}
          onMouseLeave={(e) => {
            (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
            (e.currentTarget as HTMLButtonElement).style.color = '#2563EB';
            (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-light)';
          }}
        >
          Trade →
        </button>
      </td>
    </tr>
  );
});

TableRow.displayName = 'TableRow';
export default TableRow;

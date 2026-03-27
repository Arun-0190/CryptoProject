/**
 * Number and string formatting utilities for the dashboard.
 */

/** Format a funding rate percentage with sign and fixed decimals */
export function formatRate(rate: number, decimals = 4): string {
  const sign = rate >= 0 ? '+' : '';
  return `${sign}${rate.toFixed(decimals)}%`;
}

/** Format APR */
export function formatAPR(apr: number): string {
  return `${apr.toFixed(2)}%`;
}

/** Format large USD numbers with commas */
export function formatUSD(value: number | null | undefined, decimals = 2): string {
  if (value == null) return '—';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/** Format open interest (compact: M, B) */
export function formatOI(oi: number | null): string {
  if (oi == null) return '—';
  if (oi >= 1_000_000_000) return `$${(oi / 1_000_000_000).toFixed(2)}B`;
  if (oi >= 1_000_000) return `$${(oi / 1_000_000).toFixed(2)}M`;
  if (oi >= 1_000) return `$${(oi / 1_000).toFixed(1)}K`;
  return `$${oi.toFixed(0)}`;
}

/** Compute PnL per funding event for a given position size */
export function computePnL(fundingDiff: number, positionSize: number): number {
  return (fundingDiff / 100) * positionSize;
}

/** Compute annualised revenue (3 fundings/day × 365 days) */
export function computeAnnualRevenue(fundingDiff: number, positionSize: number): number {
  return computePnL(fundingDiff, positionSize) * 3 * 365;
}

/** Format a timestamp (ms) to human-readable countdown */
export function formatCountdown(ms: number | null): string {
  if (!ms) return '—';
  const diff = ms - Date.now();
  if (diff <= 0) return 'Now';
  const h = Math.floor(diff / 3_600_000);
  const m = Math.floor((diff % 3_600_000) / 60_000);
  const s = Math.floor((diff % 60_000) / 1000);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

/** Format mark price */
export function formatPrice(price: number | null): string {
  if (price == null) return '—';
  if (price < 0.001) return `$${price.toFixed(6)}`;
  if (price < 1) return `$${price.toFixed(4)}`;
  if (price < 100) return `$${price.toFixed(2)}`;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(price);
}

/** Derive token name from symbol (BTCUSDT → BTC) */
export function getBaseToken(symbol: string): string {
  return symbol.replace(/USDT$|USD$|BUSD$/, '');
}

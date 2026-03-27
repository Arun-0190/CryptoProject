import React from 'react';
import type { Confidence, Risk } from '../types/arbitrage';

interface ConfidenceBadgeProps {
  value: Confidence;
}

interface RiskBadgeProps {
  value: Risk;
}

const CONFIDENCE_STYLES: Record<Confidence, { bg: string; color: string }> = {
  High: { bg: 'rgba(14, 203, 129, 0.15)', color: '#0ECB81' },
  Medium: { bg: 'rgba(240, 185, 11, 0.15)', color: '#F0B90B' },
  Low: { bg: 'rgba(138, 155, 176, 0.12)', color: '#8A9BB0' },
};

const RISK_STYLES: Record<Risk, { bg: string; color: string }> = {
  Low: { bg: 'rgba(14, 203, 129, 0.12)', color: '#0ECB81' },
  Medium: { bg: 'rgba(240, 185, 11, 0.12)', color: '#F0B90B' },
  High: { bg: 'rgba(246, 70, 93, 0.15)', color: '#F6465D' },
};

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({ value }) => {
  const style = CONFIDENCE_STYLES[value];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: 5,
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        background: style.bg,
        color: style.color,
      }}
    >
      <span
        style={{
          width: 5,
          height: 5,
          borderRadius: '50%',
          background: style.color,
          flexShrink: 0,
        }}
      />
      {value}
    </span>
  );
};

export const RiskBadge: React.FC<RiskBadgeProps> = ({ value }) => {
  const style = RISK_STYLES[value];
  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: 4,
        fontSize: 11,
        fontWeight: 600,
        background: style.bg,
        color: style.color,
      }}
    >
      {value}
    </span>
  );
};

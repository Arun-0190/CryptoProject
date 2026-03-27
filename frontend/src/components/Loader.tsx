import React from 'react';

interface LoaderProps {
  rows?: number;
}

const SkeletonRow: React.FC = () => (
  <tr>
    {Array.from({ length: 9 }).map((_, i) => (
      <td key={i} style={{ padding: '12px 16px' }}>
        <div
          className="skeleton"
          style={{
            height: 14,
            width: i === 0 ? 80 : i === 1 ? 140 : i === 2 ? 100 : 70,
          }}
        />
      </td>
    ))}
  </tr>
);

const Loader: React.FC<LoaderProps> = ({ rows = 12 }) => (
  <>
    {Array.from({ length: rows }).map((_, i) => (
      <SkeletonRow key={i} />
    ))}
  </>
);

export const ErrorState: React.FC<{ message: string; onRetry?: () => void }> = ({
  message,
  onRetry,
}) => (
  <tr>
    <td colSpan={10} style={{ textAlign: 'center', padding: '60px 24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
        <div style={{ fontSize: 32 }}>⚠️</div>
        <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>{message}</div>
        {onRetry && (
          <button
            onClick={onRetry}
            style={{
              marginTop: 8,
              padding: '8px 20px',
              background: '#2563EB',
              border: 'none',
              borderRadius: 8,
              color: 'white',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Retry
          </button>
        )}
      </div>
    </td>
  </tr>
);

export const EmptyState: React.FC = () => (
  <tr>
    <td colSpan={10} style={{ textAlign: 'center', padding: '60px 24px' }}>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
        <div style={{ fontSize: 32 }}>📊</div>
        <div style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          No arbitrage opportunities found matching your filters.
        </div>
      </div>
    </td>
  </tr>
);

export default Loader;

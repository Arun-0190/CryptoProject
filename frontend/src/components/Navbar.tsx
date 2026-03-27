import React from 'react';

const NAV_LINKS = ['Market', 'Exchanges', 'Funding', 'Arbitrage'];

const Navbar: React.FC = () => {
  return (
    <nav
      style={{
        background: '#0D1219',
        borderBottom: '1px solid var(--border)',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      <div
        style={{
          maxWidth: 1440,
          margin: '0 auto',
          padding: '0 24px',
          height: 56,
          display: 'flex',
          alignItems: 'center',
          gap: 32,
        }}
      >
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: 'linear-gradient(135deg, #2563EB, #7C3AED)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 14,
              fontWeight: 800,
              color: 'white',
            }}
          >
            A
          </div>
          <span style={{ fontWeight: 700, fontSize: 16, letterSpacing: '-0.02em', color: 'white' }}>
            arb<span style={{ color: '#2563EB' }}>radar</span>
          </span>
        </div>

        {/* Nav links */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, flex: 1 }}>
          {NAV_LINKS.map((link) => (
            <button
              key={link}
              style={{
                background: 'transparent',
                border: 'none',
                color: link === 'Arbitrage' ? 'white' : 'var(--text-secondary)',
                fontSize: 13,
                fontWeight: link === 'Arbitrage' ? 600 : 400,
                padding: '6px 14px',
                cursor: 'pointer',
                borderRadius: 6,
                transition: 'color 0.15s',
                position: 'relative',
              }}
            >
              {link}
              {link === 'Arbitrage' && (
                <div
                  style={{
                    position: 'absolute',
                    bottom: -1,
                    left: 14,
                    right: 14,
                    height: 2,
                    borderRadius: 2,
                    background: '#2563EB',
                  }}
                />
              )}
            </button>
          ))}
        </div>

        {/* Right side */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Search */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              background: 'var(--bg-input)',
              border: '1px solid var(--border)',
              borderRadius: 8,
              padding: '6px 12px',
              minWidth: 160,
            }}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>Search</span>
          </div>

          {/* Login */}
          <button
            style={{
              background: '#2563EB',
              border: 'none',
              borderRadius: 8,
              color: 'white',
              fontSize: 13,
              fontWeight: 600,
              padding: '7px 18px',
              cursor: 'pointer',
            }}
          >
            Login
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

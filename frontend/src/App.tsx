import React from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';

const App: React.FC = () => {
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg-primary)' }}>
      <Navbar />
      <main>
        <Dashboard />
      </main>
    </div>
  );
};

export default App;

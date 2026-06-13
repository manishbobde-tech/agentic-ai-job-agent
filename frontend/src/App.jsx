import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Briefcase, FileText, Search } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import JobView from './pages/JobView';
import ResumePage from './pages/ResumePage';

function Navbar() {
  const location = useLocation();
  
  const links = [
    { path: '/', label: 'Jobs', icon: Search },
    { path: '/resume', label: 'Resume Matcher', icon: FileText },
  ];

  return (
    <nav style={{
      background: '#18181b',
      borderBottom: '1px solid #3f3f46',
      padding: '0 24px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: '1400px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '64px',
      }}>
        <Link to="/" style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          textDecoration: 'none',
          color: '#e4e4e7',
        }}>
          <Briefcase size={24} color="#6366f1" />
          <span style={{ fontWeight: 700, fontSize: '18px' }}>
            Agentic AI Jobs
          </span>
        </Link>

        <div style={{ display: 'flex', gap: '8px' }}>
          {links.map(({ path, label, icon: Icon }) => {
            const isActive = location.pathname === path;
            return (
              <Link
                key={path}
                to={path}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  padding: '8px 16px',
                  borderRadius: '8px',
                  textDecoration: 'none',
                  color: isActive ? '#fff' : '#a1a1aa',
                  background: isActive ? '#6366f1' : 'transparent',
                  fontSize: '14px',
                  fontWeight: 500,
                  transition: 'all 0.2s',
                }}
              >
                <Icon size={16} />
                {label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

function App() {
  return (
    <Router>
      <Navbar />
      <main style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/job/:index" element={<JobView />} />
          <Route path="/resume" element={<ResumePage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;

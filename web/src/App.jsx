import { BrowserRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { Compass, Search, BookOpen, BarChart2, PenTool, List, Settings } from 'lucide-react';
import CopilotPage from './pages/Copilot';
import SearchPage from './pages/Search';
import KnowledgePage from './pages/Knowledge';
import AnalyticsPage from './pages/Analytics';
import StudioPage from './pages/Studio';
import OrdersPage from './pages/Orders';
import SettingsPage from './pages/Settings';

function App() {
  return (
    <Router>
      <div className="app-container">
        <aside className="sidebar">
          <div className="brand">
            ORNEXA
          </div>
          
          <nav style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            <NavLink to="/orders" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <List size={20} />
              All Orders
            </NavLink>
            <NavLink to="/copilot" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Compass size={20} />
              Copilot
            </NavLink>
            <NavLink to="/search" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Search size={20} />
              Search
            </NavLink>
            <NavLink to="/knowledge" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <BookOpen size={20} />
              Knowledge Explorer
            </NavLink>
            <NavLink to="/studio" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <PenTool size={20} />
              Design Studio
            </NavLink>
            <NavLink to="/analytics" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <BarChart2 size={20} />
              Analytics
            </NavLink>
            <div style={{ margin: "1rem 0", height: "1px", background: "var(--border-subtle)" }}></div>
            <NavLink to="/settings" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Settings size={20} />
              Global Rates
            </NavLink>
          </nav>
        </aside>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/orders" replace />} />
            <Route path="/copilot" element={<CopilotPage />} />
            <Route path="/search" element={<SearchPage />} />
            <Route path="/knowledge" element={<KnowledgePage />} />
            <Route path="/studio" element={<StudioPage />} />
            <Route path="/orders" element={<OrdersPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;

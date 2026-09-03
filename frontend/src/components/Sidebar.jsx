import '../styles/Sidebar.css';
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
function Sidebar({ user, onLogout, activePage, onNavigate }) {

 const [isAdmin, setIsAdmin] = useState(false);
 
  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const response = await apiService.checkAdmin();
        if (response.success) {
          setIsAdmin(response.is_admin);
        }
      } catch (error) {
        console.error('Error checking admin:', error);
      }
    };
    checkAdmin();
  }, []);

  return (
    <aside className="sidebar">
      <nav className="sidebar-nav">
        <button
          className={`nav-item ${activePage === 'dashboard' ? 'active' : ''}`}
          onClick={() => onNavigate('dashboard')}
        >
          <span className="icon">📊</span>
          <span className="label">Dashboard</span>
        </button>

        <button
          className={`nav-item ${activePage === 'tenders' ? 'active' : ''}`}
          onClick={() => onNavigate('tenders')}
        >
          <span className="icon">📋</span>
          <span className="label">Tenders</span>
        </button>

        {/* <button
          className={`nav-item ${activePage === 'agent' ? 'active' : ''}`}
          onClick={() => onNavigate('agent')}
        >
          <span className="icon">🤖</span>
          <span className="label">Agent</span>
        </button> */}
        <button
          className={`nav-item ${activePage === 'it-search' ? 'active' : ''}`}
          onClick={() => onNavigate('it-search')}
        >
          <span className="icon">💻</span>
          <span className="label">IT Search</span>
        </button>


          <button
          className={`nav-item ${activePage === 'notification-settings' ? 'active' : ''}`}
          onClick={() => onNavigate('notification-settings')}
        >
          <span className="icon">🔔</span>
          <span className="label">notifications</span>
        </button>






{isAdmin && (
        <button
          className={`nav-item ${activePage === 'scrape' ? 'active' : ''}`}
          onClick={() => onNavigate('scrape')}
        >
          <span className="icon">🔄</span>
          <span className="label">Scrape Data</span>
        </button>
)}
        {/* <button
          className={`nav-item ${activePage === 'analytics' ? 'active' : ''}`}
          onClick={() => onNavigate('analytics')}
        >
          <span className="icon">📈</span>
          <span className="label">Analytics</span>
        </button> */}
{isAdmin && (
        <button
          className={`nav-item ${activePage === 'scraper-sources' ? 'active' : ''}`}
          onClick={() => onNavigate('scraper-sources')}
        >
          <span className="icon">📜</span>
          <span className="label">Scraper Sources</span>
        </button>)}
        {isAdmin && (
        <button
          className={`nav-item ${activePage === 'add-scraper-source' ? 'active' : ''}`}
          onClick={() => onNavigate('add-scraper-source')}
        >
          <span className="icon">🗂️</span>
          <span className="label">Add Scraper Source</span>
        </button>)}
        {/* <button
          className={`nav-item ${activePage === 'construction-search' ? 'active' : ''}`}
          onClick={() => onNavigate('construction-search')}
        >
          <span className="icon">🏗️</span>
          <span className="label">Construction-Search</span>
        </button> */}
        {/* <button
          className={`nav-item ${activePage === 'admin' ? 'active' : ''}`}
          onClick={() => onNavigate('admin')}
        >
          <span className="icon">👨‍👨</span>
          <span className="label">users</span>
        </button> */}
        {isAdmin && (
        <button 
          className={`nav-item ${activePage === 'admin' ? 'active' : ''}`}
          onClick={() => onNavigate('admin')}
        >
          🛡️ Admin Dashboard
        </button>
      )}

      </nav>
    </aside>
  );
}

export default Sidebar;

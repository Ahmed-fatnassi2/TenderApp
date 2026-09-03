import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/Dashboard.css';

function Dashboard({ onNavigate }) {

  const [stats, setStats] = useState({
    totalTenders: 0,
    backendStatus: 'checking...',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [healthData, countData] = await Promise.all([
          apiService.healthCheck(),
          apiService.getTenderCount(),
        ]);

        setStats({
          totalTenders: countData.total || 0,
          backendStatus: healthData.status || 'unknown',
        });
        setError('');
      } catch (err) {
        setError('Failed to fetch dashboard data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <p>Overview of tender management system</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {loading ? (
        <div className="loading">Loading dashboard...</div>
      ) : (
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📊</div>
            <div className="stat-content">
              <h3>Total Tenders</h3>
              <p className="stat-value">{stats.totalTenders}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🟢</div>
            <div className="stat-content">
              <h3>Backend Status</h3>
              <p className="stat-value">{stats.backendStatus}</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📅</div>
            <div className="stat-content">
              <h3>Last Updated</h3>
              <p className="stat-value">Today</p>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>System Status</h3>
              <p className="stat-value">Working</p>
            </div>
          </div>
        </div>
      )}

      <div className="dashboard-actions">
        <h3>Quick Actions</h3>
        <div className="action-buttons">
<button type="button" className="action-btn primary" onClick={() => onNavigate('tenders')}>
    View All Tenders
  </button>
  <button type="button" className="action-btn secondary" onClick={() => onNavigate('scrape')}>
    Refresh Data
  </button>
  <button type="button" className="action-btn secondary" >
    Export Report
  </button>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

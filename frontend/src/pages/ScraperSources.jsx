// components/ScraperSources.jsx
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import AddScraperSource from './AddScraperSource';

// Styles object
const styles = {
  container: {
    padding: '20px',
    marginLeft: '280px', // Match your sidebar width
    maxWidth: 'calc(100% - 280px)',
    boxSizing: 'border-box',
    minHeight: '100vh'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px',
    paddingBottom: '16px',
    borderBottom: '1px solid #eee'
  },
  headerH2: {
    margin: 0,
    color: '#333'
  },
  addButton: {
    background: '#2196F3',
    color: 'white',
    border: 'none',
    padding: '10px 20px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: '500',
    transition: 'all 0.2s'
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
    gap: '20px'
  },
  card: {
    background: 'white',
    borderRadius: '8px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    border: '1px solid #eee',
    transition: 'all 0.2s'
  },
  cardHover: {
    boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
    transform: 'translateY(-2px)'
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '14px',
    marginBottom: '16px'
  },
  icon: {
    fontSize: '32px',
    width: '48px',
    height: '48px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    background: '#f5f5f5',
    borderRadius: '8px'
  },
  info: {
    flex: 1
  },
  infoH3: {
    margin: 0,
    fontSize: '16px',
    color: '#333'
  },
  sourceName: {
    fontSize: '12px',
    color: '#999',
    fontFamily: 'monospace',
    background: '#f5f5f5',
    padding: '2px 8px',
    borderRadius: '4px',
    display: 'inline-block',
    marginTop: '4px'
  },
  details: {
    fontSize: '14px',
    color: '#555'
  },
  detailRow: {
    margin: '4px 0',
    display: 'flex',
    justifyContent: 'space-between'
  },
  detailStrong: {
    color: '#333'
  },
  actions: {
    display: 'flex',
    gap: '8px',
    marginTop: '16px',
    paddingTop: '16px',
    borderTop: '1px solid #eee'
  },
  scrapeButton: {
    background: '#2196F3',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer',
    flex: 1,
    fontSize: '13px',
    transition: 'all 0.2s'
  },
  scrapeButtonDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed'
  },
  deleteButton: {
    background: '#f44336',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '13px',
    transition: 'all 0.2s'
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    color: '#666'
  },
  emptyState: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#666'
  },
  link: {
    color: '#2196F3',
    textDecoration: 'none',
    wordBreak: 'break-all'
  },
  statusActive: {
    display: 'inline-block',
    padding: '2px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    background: '#e8f5e9',
    color: '#4CAF50'
  },
  statusInactive: {
    display: 'inline-block',
    padding: '2px 12px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: '500',
    background: '#fdecea',
    color: '#f44336'
  }
};

function ScraperSources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState({});
  const [showAddForm, setShowAddForm] = useState(false);

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    setLoading(true);
    try {
      const response = await apiService.request('/scrapers/sources');
      setSources(response.sources || []);
    } catch (error) {
      console.error('Error fetching sources:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleScrape = async (sourceId) => {
    setScraping(prev => ({ ...prev, [sourceId]: true }));
    try {
      const response = await apiService.request(`/scrapers/sources/${sourceId}/scrape`, {
        method: 'POST'
      });
      if (response.success) {
        alert(response.message);
        fetchSources();
      }
    } catch (error) {
      alert('Scrape failed: ' + error.message);
    } finally {
      setScraping(prev => ({ ...prev, [sourceId]: false }));
    }
  };

  const handleDelete = async (sourceId, sourceName) => {
    if (!confirm(`Delete all tenders from "${sourceName}"?`)) return;
    
    try {
      const response = await apiService.request(`/scrapers/sources/${sourceId}`, {
        method: 'DELETE'
      });
      if (response.success) {
        alert(response.message);
        fetchSources();
      }
    } catch (error) {
      alert('Delete failed: ' + error.message);
    }
  };

  const handleAddSuccess = (config) => {
    setShowAddForm(false);
    fetchSources();
    alert(`Source "${config.display_name || config.name}" added successfully!`);
  };

  const handleAddCancel = () => {
    setShowAddForm(false);
  };

  const getSourceIcon = (name) => {
    const icons = {
      'TUNEPS': '🏛️',
      'HAICOP': '📋',
    };
    return icons[name] || '🔌';
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={styles.headerH2}>Scraper Sources</h2>
        <button 
          style={styles.addButton}
          onClick={() => setShowAddForm(true)}
          onMouseOver={(e) => e.target.style.background = '#1976D2'}
          onMouseOut={(e) => e.target.style.background = '#2196F3'}
        >
          ➕ Add New Source
        </button>
      </div>

      {showAddForm && (
        <AddScraperSource 
          onSuccess={handleAddSuccess}
          onCancel={handleAddCancel}
        />
      )}

      {loading ? (
        <div style={styles.loading}>Loading...</div>
      ) : sources.length === 0 ? (
        <div style={styles.emptyState}>
          <p>No scraper sources configured yet.</p>
          <p>Click "Add New Source" to start scraping from different portals.</p>
        </div>
      ) : (
        <div style={styles.grid}>
          {sources.map((source) => (
            <div 
              key={source.id} 
              style={styles.card}
              onMouseOver={(e) => {
                e.currentTarget.style.boxShadow = '0 4px 16px rgba(0,0,0,0.12)';
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              <div style={styles.cardHeader}>
                <div style={styles.icon}>{getSourceIcon(source.name)}</div>
                <div style={styles.info}>
                  <h3 style={styles.infoH3}>{source.display_name}</h3>
                  <span style={styles.sourceName}>{source.name}</span>
                </div>
              </div>

              <div style={styles.details}>
                <p style={styles.detailRow}>
                  <strong style={styles.detailStrong}>Type:</strong> {source.source_type}
                </p>
                <p style={styles.detailRow}>
                  <strong style={styles.detailStrong}>URL:</strong> 
                  <a href={source.base_url} target="_blank" rel="noopener noreferrer" style={styles.link}>
                    {source.base_url}
                  </a>
                </p>
                <p style={styles.detailRow}>
                  <strong style={styles.detailStrong}>Auth:</strong> {source.auth_type}
                </p>
                <p style={styles.detailRow}>
                  <strong style={styles.detailStrong}>Tenders:</strong> {source.total_tenders || 0}
                </p>
                {source.last_scraped && (
                  <p style={styles.detailRow}>
                    <strong style={styles.detailStrong}>Last Scraped:</strong> 
                    {new Date(source.last_scraped).toLocaleString()}
                  </p>
                )}
                <p style={styles.detailRow}>
                  <strong style={styles.detailStrong}>Status:</strong> 
                  <span style={source.is_active ? styles.statusActive : styles.statusInactive}>
                    {source.is_active ? '🟢 Active' : '🔴 Inactive'}
                  </span>
                </p>
              </div>

              <div style={styles.actions}>
                <button 
                  style={{
                    ...styles.scrapeButton,
                    ...(scraping[source.id] || !source.is_active ? styles.scrapeButtonDisabled : {})
                  }}
                  onClick={() => handleScrape(source.id)}
                  disabled={scraping[source.id] || !source.is_active}
                  onMouseOver={(e) => {
                    if (!e.target.disabled) {
                      e.target.style.background = '#1976D2';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!e.target.disabled) {
                      e.target.style.background = '#2196F3';
                    }
                  }}
                >
                  {scraping[source.id] ? '⏳ Scraping...' : '🔄 Scrape Now'}
                </button>
                <button 
                  style={styles.deleteButton}
                  onClick={() => handleDelete(source.id, source.display_name)}
                  onMouseOver={(e) => e.target.style.background = '#d32f2f'}
                  onMouseOut={(e) => e.target.style.background = '#f44336'}
                >
                  🗑️ Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default ScraperSources;
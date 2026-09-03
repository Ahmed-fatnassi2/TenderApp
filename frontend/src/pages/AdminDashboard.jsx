// components/AdminDashboard.jsx - Use localStorage
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '20px',
    marginLeft: '280px',
  },
  header: {
    background: 'linear-gradient(135deg, #1a3a5c, #2d6a8f)',
    color: 'white',
    padding: '30px 40px',
    borderRadius: '12px',
    marginBottom: '30px',
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
    marginBottom: '30px',
  },
  statCard: {
    background: 'white',
    padding: '20px',
    borderRadius: '10px',
    boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
    textAlign: 'center',
  },
  statNumber: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1a3a5c',
  },
  statLabel: {
    fontSize: '14px',
    color: '#6b7b8d',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    background: 'white',
    borderRadius: '10px',
    overflow: 'hidden',
    boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
  },
  th: {
    background: '#f0f2f5',
    padding: '12px 16px',
    textAlign: 'left',
    fontWeight: 600,
    color: '#2c3e50',
  },
  td: {
    padding: '12px 16px',
    borderBottom: '1px solid #e0e6ed',
  },
  button: {
    padding: '6px 14px',
    margin: '2px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '12px',
    fontWeight: 500,
    transition: 'all 0.2s',
  },
  btnDelete: {
    background: '#e74c3c',
    color: 'white',
  },
  btnMakeAdmin: {
    background: '#2d6a8f',
    color: 'white',
  },
  btnRemoveAdmin: {
    background: '#e67e22',
    color: 'white',
  },
  btnToggle: {
    background: '#27ae60',
    color: 'white',
  },
  badge: {
    padding: '3px 10px',
    borderRadius: '12px',
    fontSize: '12px',
    fontWeight: 500,
  },
  badgeAdmin: {
    background: '#e8f4fd',
    color: '#2d6a8f',
  },
  badgeActive: {
    background: '#e8f5e9',
    color: '#27ae60',
  },
  badgeInactive: {
    background: '#fdecea',
    color: '#e74c3c',
  },
  loading: {
    textAlign: 'center',
    padding: '40px',
    fontSize: '18px',
    color: '#6b7b8d',
  },
  errorCard: {
    background: '#fdecea',
    padding: '40px',
    borderRadius: '12px',
    textAlign: 'center',
    color: '#c0392b',
  },
};

function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    checkAdminAndLoad();
  }, []);

  const checkAdminAndLoad = async () => {
    try {
      // Get user from localStorage
      const userData = localStorage.getItem('user');
      console.log('📦 User data from localStorage:', userData);
      
      if (!userData) {
        setError('Not logged in');
        setLoading(false);
        return;
      }
      
      const user = JSON.parse(userData);
      console.log('👤 Current user:', user);
      
      // Check if user is admin from localStorage
      if (user.is_admin === true) {
        console.log('✅ User is admin! Loading dashboard...');
        setIsAdmin(true);
        setCurrentUser(user.username);
        await loadData();
      } else {
        console.log('❌ User is not admin');
        setError('You do not have admin access');
        setLoading(false);
      }
    } catch (err) {
      console.error('Error checking admin:', err);
      setError('Failed to verify admin status');
      setLoading(false);
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      // Load users
      const usersResponse = await apiService.getAdminUsers();
      if (usersResponse.success) {
        setUsers(usersResponse.users);
      }

      // Load stats
      const statsResponse = await apiService.getAdminStats();
      if (statsResponse.success) {
        setStats(statsResponse.stats);
      }
    } catch (err) {
      setError('Failed to load data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!window.confirm(`Are you sure you want to delete user "${username}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await apiService.deleteUser(userId);
      if (response.success) {
        setUsers(users.filter(u => u.id !== userId));
        alert(`User ${username} deleted successfully`);
        const statsResponse = await apiService.getAdminStats();
        if (statsResponse.success) {
          setStats(statsResponse.stats);
        }
      } else {
        alert(response.error || 'Failed to delete user');
      }
    } catch (err) {
      alert('Error deleting user');
      console.error(err);
    }
  };

  const handleMakeAdmin = async (userId) => {
    try {
      const response = await apiService.makeAdmin(userId);
      if (response.success) {
        setUsers(users.map(u => 
          u.id === userId ? { ...u, is_admin: true } : u
        ));
        alert('User is now an admin');
        loadData();
      } else {
        alert(response.error || 'Failed to make admin');
      }
    } catch (err) {
      alert('Error making admin');
    }
  };

  const handleRemoveAdmin = async (userId) => {
    if (!window.confirm('Remove admin privileges from this user?')) {
      return;
    }

    try {
      const response = await apiService.removeAdmin(userId);
      if (response.success) {
        setUsers(users.map(u => 
          u.id === userId ? { ...u, is_admin: false } : u
        ));
        alert('Admin privileges removed');
        loadData();
      } else {
        alert(response.error || 'Failed to remove admin');
      }
    } catch (err) {
      alert('Error removing admin');
    }
  };

  const handleToggleActive = async (userId) => {
    try {
      const response = await apiService.toggleUserActive(userId);
      if (response.success) {
        setUsers(users.map(u => 
          u.id === userId ? { ...u, is_active: !u.is_active } : u
        ));
        loadData();
      } else {
        alert(response.error || 'Failed to toggle user');
      }
    } catch (err) {
      alert('Error toggling user');
    }
  };

  if (!isAdmin && !loading) {
    return (
      <div style={styles.container}>
        <div style={styles.errorCard}>
          <h2>⛔ Access Denied</h2>
          <p>You do not have admin access to this page.</p>
          <p>Please contact your administrator.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return <div style={styles.loading}>Loading admin dashboard...</div>;
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h2 style={{ margin: 0 }}>🛡️ Admin Dashboard</h2>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>
          Welcome, {currentUser}! Manage users and system settings.
        </p>
      </div>

      {stats && (
        <div style={styles.statsGrid}>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>{stats.total_users}</div>
            <div style={styles.statLabel}>Total Users</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>{stats.admin_count}</div>
            <div style={styles.statLabel}>Admins</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>{stats.active_users}</div>
            <div style={styles.statLabel}>Active Users</div>
          </div>
          <div style={styles.statCard}>
            <div style={styles.statNumber}>{stats.total_tenders}</div>
            <div style={styles.statLabel}>Total Tenders</div>
          </div>
        </div>
      )}

      <div style={{ background: 'white', borderRadius: '10px', padding: '20px', boxShadow: '0 2px 10px rgba(0,0,0,0.08)' }}>
        <h3 style={{ margin: '0 0 16px 0' }}>👥 Users</h3>
        
        <div style={{ overflowX: 'auto' }}>
          <table style={styles.table}>
            <thead>
              <tr>
                <th style={styles.th}>ID</th>
                <th style={styles.th}>Username</th>
                <th style={styles.th}>Email</th>
                <th style={styles.th}>Name</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Admin</th>
                <th style={styles.th}>Created</th>
                <th style={styles.th}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td style={styles.td}>{user.id}</td>
                  <td style={styles.td}><strong>{user.username}</strong></td>
                  <td style={styles.td}>{user.email}</td>
                  <td style={styles.td}>{user.first_name} {user.last_name}</td>
                  <td style={styles.td}>
                    <span style={{
                      ...styles.badge,
                      ...(user.is_active ? styles.badgeActive : styles.badgeInactive)
                    }}>
                      {user.is_active ? '🟢 Active' : '🔴 Inactive'}
                    </span>
                  </td>
                  <td style={styles.td}>
                    {user.is_admin ? (
                      <span style={{ ...styles.badge, ...styles.badgeAdmin }}>✅ Admin</span>
                    ) : (
                      <span style={{ color: '#999' }}>User</span>
                    )}
                  </td>
                  <td style={styles.td}>
                    {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </td>
                  <td style={styles.td}>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                      <button
                        style={{ ...styles.button, ...styles.btnToggle }}
                        onClick={() => handleToggleActive(user.id)}
                      >
                        {user.is_active ? '🔴 Deactivate' : '🟢 Activate'}
                      </button>

                      {user.is_admin ? (
                        <button
                          style={{ ...styles.button, ...styles.btnRemoveAdmin }}
                          onClick={() => handleRemoveAdmin(user.id)}
                        >
                          Remove Admin
                        </button>
                      ) : (
                        <button
                          style={{ ...styles.button, ...styles.btnMakeAdmin }}
                          onClick={() => handleMakeAdmin(user.id)}
                        >
                          Make Admin
                        </button>
                      )}

                      <button
                        style={{ ...styles.button, ...styles.btnDelete }}
                        onClick={() => handleDeleteUser(user.id, user.username)}
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {users.length === 0 && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7b8d' }}>
            <p>No users found</p>
          </div>
        )}
      </div>

      {error && (
        <div style={{ ...styles.errorCard, marginTop: '20px' }}>
          ❌ {error}
        </div>
      )}
    </div>
  );
}

export default AdminDashboard;
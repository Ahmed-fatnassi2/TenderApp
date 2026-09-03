// pages/NotificationSettings.jsx
import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/NotificationSettings.css';

function NotificationSettings() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [sendingTest, setSendingTest] = useState(false);
  const [preferences, setPreferences] = useState({
    notifications_enabled: true,
    frequency: 'daily',
    send_time: '08:00',
    custom_prompt: '',
    search_terms: [],
    categories: [],
    min_budget: '',
    max_budget: '',
    regions: [],
    buyers: [],
    sources: []
  });
  const [testResults, setTestResults] = useState(null);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const response = await apiService.getPreferences();
      if (response.success) {
        setPreferences(response.preferences);
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to load preferences' });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setPreferences(prev => ({ ...prev, [field]: value }));
  };

  const handleArrayChange = (field, value) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item);
    setPreferences(prev => ({ ...prev, [field]: items }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await apiService.updatePreferences(preferences);
      if (response.success) {
        setMessage({ type: 'success', text: 'Preferences saved successfully!' });
        setPreferences(response.preferences);
      } else {
        setMessage({ type: 'error', text: response.error || 'Failed to save' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to save' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResults(null);
    setMessage({ type: '', text: '' });

    try {
      const response = await apiService.testPreferences();
      if (response.success) {
        setTestResults(response);
        setMessage({ 
          type: 'success', 
          text: `Found ${response.tenders_found} tenders matching your preferences!` 
        });
      } else {
        setMessage({ type: 'error', text: response.error || 'Test failed' });
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Test failed' });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading preferences...</div>;
  }


const handleTestITNotification = async () => {
  setSendingTest(true);
  try {
    const response = await apiService.testITNotification();
    if (response.success) {
      setMessage({ type: 'success', text: 'Test IT notification sent! Check your email.' });
    } else {
      setMessage({ type: 'error', text: response.message || 'Failed to send test' });
    }
  } catch (err) {
    setMessage({ type: 'error', text: err.message || 'Failed to send test' });
  } finally {
    setSendingTest(false);
  }
};

  return (
    <div className="notification-settings">
      <div className="settings-header">
        <h2>🔔 Notification Settings</h2>
        <p>Configure your personalized tender alerts</p>
      </div>

      {message.text && (
        <div className={`message-banner ${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="settings-form">
        {/* Notification Settings */}
        <div className="settings-section">
          <h3>📧 Email Notifications</h3>
          
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                checked={preferences.notifications_enabled}
                onChange={(e) => handleChange('notifications_enabled', e.target.checked)}
              />
              Enable email notifications
            </label>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Frequency</label>
              <select
                value={preferences.frequency}
                onChange={(e) => handleChange('frequency', e.target.value)}
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="immediate">Immediate</option>
              </select>
            </div>

            <div className="form-group">
              <label>Send Time</label>
              <input
                type="time"
                value={preferences.send_time}
                onChange={(e) => handleChange('send_time', e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Search Preferences */}
        <div className="settings-section">
          <h3>🔍 Search Preferences</h3>
          
          <div className="form-group">
            <label>Custom Prompt</label>
            <textarea
              value={preferences.custom_prompt || ''}
              onChange={(e) => handleChange('custom_prompt', e.target.value)}
              placeholder="e.g., Find IT infrastructure tenders with network equipment"
              rows={3}
            />
            <small>The AI agent will use this prompt to find relevant tenders</small>
          </div>

          {/* <div className="form-group">
            <label>Search Terms</label>
            <input
              type="text"
              value={preferences.search_terms?.join(', ') || ''}
              onChange={(e) => handleArrayChange('search_terms', e.target.value)}
              placeholder="network, infrastructure, software, cloud"
            />
            <small>Comma-separated keywords</small>
          </div> */}

          {/* <div className="form-group">
            <label>Categories</label>
            <input
              type="text"
              value={preferences.categories?.join(', ') || ''}
              onChange={(e) => handleArrayChange('categories', e.target.value)}
              placeholder="IT, Technology, Infrastructure"
            />
            <small>Comma-separated categories</small>
          </div> */}
        </div>

        {/* Filters */}
        <div className="settings-section">
          <h3>🎯 Filters</h3>

          <div className="form-row">
            {/* <div className="form-group">
              <label>Min Budget</label>
              <input
                type="number"
                value={preferences.min_budget || ''}
                onChange={(e) => handleChange('min_budget', e.target.value)}
                placeholder="10000"
              />
            </div> */}
            {/* <div className="form-group">
              <label>Max Budget</label>
              <input
                type="number"
                value={preferences.max_budget || ''}
                onChange={(e) => handleChange('max_budget', e.target.value)}
                placeholder="100000"
              />
            </div> */}
          </div>

          <div className="form-group">
            <label>Regions</label>
            <input
              type="text"
              value={preferences.regions?.join(', ') || ''}
              onChange={(e) => handleArrayChange('regions', e.target.value)}
              placeholder="Tunis, Sfax, Sousse"
            />
          </div>

          <div className="form-group">
            <label>Specific Buyers</label>
            <input
              type="text"
              value={preferences.buyers?.join(', ') || ''}
              onChange={(e) => handleArrayChange('buyers', e.target.value)}
              placeholder="Ministry of IT, Government Agency"
            />
          </div>

          <div className="form-group">
            <label>Sources</label>
            <input
              type="text"
              value={preferences.sources?.join(', ') || ''}
              onChange={(e) => handleArrayChange('sources', e.target.value)}
              placeholder="TUNEPS, HAICOP"
            />
            <small>Comma-separated source names</small>
          </div>
        </div>

        <div className="form-actions">
          {/* <button
            type="button"
            className="test-button"
            onClick={handleTest}
            disabled={testing}
          >
            {testing ? 'Testing...' : '🔍 Test Search'}
          </button> */}
          <button
            type="submit"
            className="save-button"
            disabled={saving}
          >
            {saving ? 'Saving...' : '💾 Save Preferences'}
          </button>

          <button
  type="button"
  className="test-button"
  onClick={handleTestITNotification}
  disabled={sendingTest}
>
  {sendingTest ? 'Sending...' : '📧 Send Test IT Digest'}
</button>
        </div>
      </form>

      {testResults && testResults.tenders && testResults.tenders.length > 0 && (
        <div className="test-results">
          <h4>📊 Test Results</h4>
          <p>Found {testResults.tenders_found} tenders</p>
          <div className="tender-preview">
            {testResults.tenders.map((tender, index) => (
              <div key={index} className="tender-preview-card">
                <h5>{tender.title}</h5>
                <div>Buyer: {tender.buyer}</div>
                <div>Deadline: {tender.deadline}</div>
                <div className="tender-reference">Ref: {tender.reference}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationSettings;
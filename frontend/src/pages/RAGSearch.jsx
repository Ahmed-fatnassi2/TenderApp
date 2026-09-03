import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/RAGSearch.css';

function RAGSearch() {
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [ragStatus, setRagStatus] = useState('checking');
  const [expandedId, setExpandedId] = useState(null);
  const [topK, setTopK] = useState(5);
  const [similarityThreshold, setSimilarityThreshold] = useState(0.75);
  const [isInitializing, setIsInitializing] = useState(false);

  // Check RAG health on component mount
  useEffect(() => {
    checkRagHealth();
  }, []);

  const checkRagHealth = async () => {
    try {
      const healthData = await apiService.getRagHealth();
      setRagStatus(healthData.rag_healthy ? 'connected' : 'disconnected');
    } catch (err) {
      console.error('Error checking RAG health:', err);
      setRagStatus('error');
    }
  };

  const handleInitializeRAG = async () => {
    if (!window.confirm('Initialize RAG with all tenders? This may take a few minutes...')) {
      return;
    }

    try {
      setIsInitializing(true);
      setError('');
      const result = await apiService.initializeRag();
      
      if (result.success) {
        setError(`✓ Successfully indexed ${result.data.successful}/${result.data.total} tenders`);
        setTimeout(() => {
          setError('');
          checkRagHealth();
        }, 3000);
      } else {
        setError(`Error: ${result.error || 'Failed to initialize RAG'}`);
      }
    } catch (err) {
      console.error('RAG initialization failed:', err);
      setError('Failed to initialize RAG. Please check if OpenRAG is running.');
    } finally {
      setIsInitializing(false);
    }
  };

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    if (ragStatus !== 'connected') {
      setError('RAG service is not connected. Please initialize RAG first.');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const results = await apiService.semanticSearch(query, topK);
      
      if (results.success) {
        setSearchResults(results.results || []);
        if (results.results.length === 0) {
          setError('No results found. Try a different search query.');
        }
      } else {
        setError(results.error || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to perform search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="rag-search-container">
      <div className="rag-header">
        <h2>🤖 Semantic Search (RAG)</h2>
        <p>Powered by OpenRAG - Find tenders using natural language</p>
      </div>

      {/* RAG Status Bar */}
      <div className={`rag-status-bar ${ragStatus}`}>
        <div className="status-icon">
          {ragStatus === 'connected' && '✅'}
          {ragStatus === 'disconnected' && '⚠️'}
          {ragStatus === 'checking' && '⏳'}
          {ragStatus === 'error' && '❌'}
        </div>
        <div className="status-text">
          <strong>RAG Status:</strong> {' '}
          {ragStatus === 'connected' && 'Connected - Ready to search'}
          {ragStatus === 'disconnected' && 'Disconnected - Initialize RAG to start searching'}
          {ragStatus === 'checking' && 'Checking connection...'}
          {ragStatus === 'error' && 'Error - Could not connect to RAG service'}
        </div>
        <button 
          className="initialize-btn" 
          onClick={handleInitializeRAG}
          disabled={isInitializing || ragStatus === 'connected'}
          title={ragStatus === 'connected' ? 'RAG already initialized' : 'Initialize RAG with all tenders'}
        >
          {isInitializing ? '⏳ Initializing...' : '🚀 Initialize RAG'}
        </button>
      </div>

      {/* Search Form */}
      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., 'road construction in Tunis' or 'IT infrastructure projects'"
            className="search-input"
            disabled={ragStatus !== 'connected' || loading}
          />
          <button 
            type="submit" 
            className="search-button"
            disabled={ragStatus !== 'connected' || loading}
          >
            {loading ? '🔍 Searching...' : '🔍 Search'}
          </button>
        </div>

        {/* Advanced Options */}
        <div className="advanced-options">
          <div className="option-group">
            <label>
              Top Results (K):
              <input
                type="number"
                min="1"
                max="50"
                value={topK}
                onChange={(e) => setTopK(Math.max(1, parseInt(e.target.value) || 5))}
                className="number-input"
              />
            </label>
          </div>

          <div className="option-group">
            <label>
              Similarity Threshold:
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={similarityThreshold}
                onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                className="slider-input"
              />
              <span className="threshold-value">{similarityThreshold.toFixed(2)}</span>
            </label>
          </div>
        </div>
      </form>

      {/* Error Message */}
      {error && (
        <div className={`message-banner ${error.includes('✓') ? 'success' : 'error'}`}>
          {error}
        </div>
      )}

      {/* Search Results */}
      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Searching through tenders...</p>
        </div>
      ) : searchResults.length > 0 ? (
        <div className="results-container">
          <div className="results-header">
            <h3>Search Results ({searchResults.length})</h3>
            <p className="results-info">Query: "{query}"</p>
          </div>

          <div className="results-list">
            {searchResults.map((result, index) => (
              <div key={index} className="result-card">
                <div className="result-header" onClick={() => toggleExpand(index)}>
                  <div className="result-ranking">#{index + 1}</div>
                  <div className="result-info">
                    <h4>
                      {result.metadata?.title || 'Untitled Tender'}
                      <span className="similarity-score">
                        {(result.score * 100).toFixed(1)}% match
                      </span>
                    </h4>
                    <p className="result-reference">
                      {result.metadata?.reference && `Reference: ${result.metadata.reference}`}
                    </p>
                  </div>
                  <div className="expand-icon">
                    {expandedId === index ? '▼' : '▶'}
                  </div>
                </div>

                {expandedId === index && (
                  <div className="result-expanded">
                    <div className="result-metadata">
                      {result.metadata?.tender_id && (
                        <p><strong>ID:</strong> {result.metadata.tender_id}</p>
                      )}
                      {result.metadata?.source && (
                        <p><strong>Source:</strong> {result.metadata.source}</p>
                      )}
                      {result.metadata?.created_at && (
                        <p><strong>Indexed:</strong> {new Date(result.metadata.created_at).toLocaleString()}</p>
                      )}
                    </div>

                    <div className="result-content">
                      <h5>Content</h5>
                      <div className="content-preview">
                        {result.content || 'No content available'}
                      </div>
                    </div>

                    <div className="result-score-details">
                      <p><strong>Similarity Score:</strong> {result.score.toFixed(4)}</p>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : query && !loading ? (
        <div className="no-results">
          <p>📭 No results found</p>
          <small>Try adjusting your search query or lowering the similarity threshold</small>
        </div>
      ) : null}

      {/* Info Box */}
      <div className="info-box">
        <h4>ℹ️ How to use Semantic Search</h4>
        <ul>
          <li>Describe what you're looking for in natural language</li>
          <li>The system will find semantically similar tenders</li>
          <li>Adjust similarity threshold to fine-tune results</li>
          <li>Initialize RAG on first use to index all tenders</li>
        </ul>
      </div>
    </div>
  );
}

export default RAGSearch;

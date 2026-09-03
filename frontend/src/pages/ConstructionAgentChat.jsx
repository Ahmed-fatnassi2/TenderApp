// // components/ConstructionAgentChat.jsx
// import { useState } from 'react';
// import { apiService } from '../services/api';
// import '../styles/ConstructionAgent.css';

// function ConstructionAgentChat() {
//   const [query, setQuery] = useState('');
//   const [results, setResults] = useState(null);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');

//   const handleSearch = async () => {
//     if (!query.trim()) return;

//     setLoading(true);
//     setError('');
//     setResults(null);

//     try {
//       const response = await apiService.request('/smart-construction/search', {
//         method: 'POST',
//         body: JSON.stringify({
//           query: query,
//           top_k: 10
//         })
//       });

//       console.log('Search response:', response); // Debug log

//       if (response.success) {
//         // Make sure we're using the right data structure
//         const documents = response.documents || [];
//         const totalFound = response.total_found || documents.length;
        
//         // Format documents with proper metadata
//         const formattedDocs = documents.map(doc => {
//           const metadata = doc.metadata || {};
//           return {
//             metadata: {
//               title: metadata.title || 'Untitled',
//               reference: metadata.reference || 'N/A',
//               buyer: metadata.buyer || 'Unknown',
//               deadline: metadata.deadline || 'N/A',
//               source: metadata.source || 'N/A'
//             },
//             content: doc.content || ''
//           };
//         });

//         setResults({
//           success: true,
//           total_found: totalFound,
//           documents: formattedDocs,
//           query: response.query || query
//         });
//       } else {
//         setError(response.error || 'Search failed');
//       }
//     } catch (err) {
//       console.error('Search error:', err);
//       setError(err.message || 'An error occurred');
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="construction-agent">
//       <div className="agent-header">
//         <h2>🏗️ Construction Tender Agent</h2>
//         <p>Find building and infrastructure tenders</p>
//       </div>

//       <div className="search-section">
//         <div className="search-input">
//           <input
//             type="text"
//             placeholder="Search for construction tenders..."
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
//           />
//           <button onClick={handleSearch} disabled={loading}>
//             {loading ? 'Searching...' : 'Search'}
//           </button>
//         </div>
//         {error && <div className="error">{error}</div>}
//       </div>

//       {results && (
//         <div className="results-section">
//           <div className="result-stats">
//             <span>🏗️ Found {results.total_found} construction tenders</span>
//             {results.query && <span className="query-badge">Query: {results.query}</span>}
//           </div>

//           <div className="results-list">
//             {results.documents && results.documents.length > 0 ? (
//               results.documents.map((doc, index) => {
//                 const metadata = doc.metadata || {};
//                 return (
//                   <div key={index} className="result-card">
//                     <div className="result-header">
//                       <span className="result-type">🏗️ Construction</span>
//                       {metadata.source && (
//                         <span className="source-badge">{metadata.source}</span>
//                       )}
//                     </div>
//                     <h3>{metadata.title || 'Untitled'}</h3>
//                     <p><strong>Buyer:</strong> {metadata.buyer || 'Unknown'}</p>
//                     <p><strong>Reference:</strong> {metadata.reference || 'N/A'}</p>
//                     {metadata.deadline && metadata.deadline !== 'N/A' && (
//                       <p><strong>Deadline:</strong> {metadata.deadline}</p>
//                     )}
//                     <div className="result-actions">
//                       <button 
//                         className="btn-view"
//                         onClick={() => alert(`View tender: ${metadata.reference}`)}
//                       >
//                         View Details
//                       </button>
//                       <button 
//                         className="btn-analyze"
//                         onClick={() => alert(`Analyze tender: ${metadata.reference}`)}
//                       >
//                         Analyze
//                       </button>
//                     </div>
//                   </div>
//                 );
//               })
//             ) : (
//               <div className="empty-state">
//                 <span className="icon">🔍</span>
//                 <h3>No tenders found</h3>
//                 <p>Try a different search term</p>
//               </div>
//             )}
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// export default ConstructionAgentChat;





// components/ConstructionAgentChat.jsx - With Inline Styles
import { useState } from 'react';
import { apiService } from '../services/api';

function ConstructionAgentChat() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    setResults(null);

    try {
      // Use the chat endpoint - it already filters correctly!
      const response = await apiService.request('/smart-construction/chat', {
        method: 'POST',
        body: JSON.stringify({ 
          message: `I need ${query} tenders` 
        })
      });

      if (response.success) {
        const responseText = response.response;
        
        // Extract tender information from the formatted response
        const tenders = [];
        const lines = responseText.split('\n');
        let currentTender = null;
        
        for (const line of lines) {
          if (line.match(/^\d+\./)) {
            if (currentTender) {
              tenders.push(currentTender);
            }
            // Extract title (remove number and asterisks)
            let title = line.replace(/^\d+\.\s*/, '').replace(/\*\*/g, '').trim();
            currentTender = {
              title: title || 'Untitled',
              details: []
            };
          } else if (currentTender && line.trim()) {
            currentTender.details.push(line.trim());
          }
        }
        if (currentTender) {
          tenders.push(currentTender);
        }
        
        // If no structured tenders found, try to extract from plain text
        let finalTenders = tenders;
        if (tenders.length === 0 && responseText) {
          // Try to find tender patterns
          const tenderMatches = responseText.match(/[📋🏗️]?\s*([^\n]+?)(?:\s*Reference:|$)/g);
          if (tenderMatches) {
            finalTenders = tenderMatches.map((t, i) => ({
              title: t.replace(/[📋🏗️]\s*/, '').trim() || `Tender ${i + 1}`,
              details: ['See full response for details']
            }));
          } else {
            // Just show the response as a single result
            finalTenders = [{
              title: 'Search Results',
              details: [responseText.substring(0, 500)]
            }];
          }
        }
        
        setResults({
          total_found: finalTenders.length,
          documents: finalTenders.map(t => ({
            metadata: {
              title: t.title || 'Untitled',
              description: t.details.join(' ') || 'No details available'
            }
          })),
          raw_response: responseText
        });
      } else {
        setError(response.error || 'Search failed');
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Inline Styles
  const styles = {
    container: {
      maxWidth: '1000px',
      margin: '0 auto',
      padding: '20px',
      fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif',
      marginLeft: '280px', // Adjust based on your sidebar width
    },
    header: {
      background: 'linear-gradient(135deg, #1a3a5c, #2d6a8f)',
      color: 'white',
      padding: '30px 40px',
      borderRadius: '12px',
      marginBottom: '30px',
      boxShadow: '0 4px 20px rgba(26, 58, 92, 0.3)',
    },
    headerTitle: {
      margin: 0,
      fontSize: '28px',
      fontWeight: 700,
      letterSpacing: '0.5px',
    },
    headerSubtitle: {
      margin: '8px 0 0 0',
      fontSize: '16px',
      opacity: 0.9,
    },
    searchSection: {
      background: 'white',
      padding: '24px 30px',
      borderRadius: '12px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
      marginBottom: '30px',
    },
    searchInput: {
      display: 'flex',
      gap: '12px',
      alignItems: 'center',
    },
    input: {
      flex: 1,
      padding: '14px 20px',
      border: '2px solid #e0e6ed',
      borderRadius: '8px',
      fontSize: '16px',
      outline: 'none',
      background: '#f8fafc',
      transition: 'all 0.3s ease',
    },
    inputFocus: {
      borderColor: '#2d6a8f',
      boxShadow: '0 0 0 3px rgba(45, 106, 143, 0.15)',
      background: 'white',
    },
    button: {
      padding: '14px 32px',
      background: 'linear-gradient(135deg, #2d6a8f, #1a3a5c)',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      fontSize: '16px',
      fontWeight: 600,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      whiteSpace: 'nowrap',
    },
    buttonDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed',
      transform: 'none',
    },
    error: {
      marginTop: '12px',
      padding: '12px 16px',
      background: '#fee9e9',
      borderLeft: '4px solid #e74c3c',
      color: '#c0392b',
      borderRadius: '4px',
      fontSize: '14px',
    },
    resultsSection: {
      background: 'white',
      borderRadius: '12px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.08)',
      padding: '24px 30px',
    },
    resultStats: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingBottom: '16px',
      borderBottom: '2px solid #f0f2f5',
      marginBottom: '20px',
    },
    resultStatsText: {
      fontSize: '16px',
      color: '#2c3e50',
      fontWeight: 500,
    },
    queryBadge: {
      background: '#e8f4fd',
      color: '#2d6a8f',
      padding: '4px 14px',
      borderRadius: '20px',
      fontSize: '13px',
      fontWeight: 500,
    },
    resultsList: {
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
    },
    resultCard: {
      background: '#f8fafc',
      border: '1px solid #e8edf3',
      borderRadius: '10px',
      padding: '20px 24px',
      transition: 'all 0.3s ease',
    },
    resultHeader: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      marginBottom: '10px',
    },
    resultType: {
      background: '#2d6a8f',
      color: 'white',
      padding: '3px 12px',
      borderRadius: '20px',
      fontSize: '12px',
      fontWeight: 600,
    },
    resultTitle: {
      margin: '10px 0 8px 0',
      fontSize: '18px',
      color: '#1a3a5c',
      lineHeight: '1.4',
    },
    resultText: {
      margin: '4px 0',
      fontSize: '14px',
      color: '#4a5b6e',
    },
    resultTextStrong: {
      color: '#2c3e50',
      fontWeight: 600,
    },
    resultActions: {
      display: 'flex',
      gap: '10px',
      marginTop: '12px',
      paddingTop: '12px',
      borderTop: '1px solid #e0e6ed',
    },
    btnView: {
      background: '#e8f4fd',
      color: '#2d6a8f',
      border: 'none',
      padding: '8px 20px',
      borderRadius: '6px',
      fontSize: '13px',
      fontWeight: 500,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
    },
    btnAnalyze: {
      background: '#2d6a8f',
      color: 'white',
      border: 'none',
      padding: '8px 20px',
      borderRadius: '6px',
      fontSize: '13px',
      fontWeight: 500,
      cursor: 'pointer',
      transition: 'all 0.3s ease',
    },
    emptyState: {
      textAlign: 'center',
      padding: '40px 20px',
      color: '#6b7b8d',
    },
    emptyIcon: {
      fontSize: '48px',
      marginBottom: '16px',
      display: 'block',
    },
    emptyTitle: {
      fontSize: '20px',
      color: '#2c3e50',
      margin: '0 0 8px 0',
    },
    emptyText: {
      fontSize: '15px',
      margin: 0,
    },
    rawResponse: {
      marginTop: '16px',
      padding: '16px',
      background: '#f5f7fa',
      borderRadius: '8px',
      fontSize: '14px',
      whiteSpace: 'pre-wrap',
      wordWrap: 'break-word',
      maxHeight: '400px',
      overflowY: 'auto',
    },
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h2 style={styles.headerTitle}>🏗️ Construction Tender Agent</h2>
        <p style={styles.headerSubtitle}>Find building and infrastructure tenders</p>
      </div>

      {/* Search Section */}
      <div style={styles.searchSection}>
        <div style={styles.searchInput}>
          <input
            type="text"
            placeholder="Search for construction tenders (e.g., road construction, school construction)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            style={{
              ...styles.input,
              ...(query ? styles.inputFocus : {})
            }}
            onFocus={(e) => e.target.style.borderColor = '#2d6a8f'}
            onBlur={(e) => e.target.style.borderColor = '#e0e6ed'}
          />
          <button 
            onClick={handleSearch} 
            disabled={loading}
            style={{
              ...styles.button,
              ...(loading ? styles.buttonDisabled : {})
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 4px 15px rgba(45, 106, 143, 0.35)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = 'none';
            }}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
        {error && <div style={styles.error}>❌ {error}</div>}
      </div>

      {/* Results Section */}
      {results && (
        <div style={styles.resultsSection}>
          <div style={styles.resultStats}>
            <span style={styles.resultStatsText}>
              🏗️ Found {results.total_found} construction tenders
            </span>
            {results.query && (
              <span style={styles.queryBadge}>Query: {results.query}</span>
            )}
          </div>

          <div style={styles.resultsList}>
            {results.documents && results.documents.length > 0 ? (
              results.documents.map((doc, index) => {
                const metadata = doc.metadata || {};
                return (
                  <div key={index} style={styles.resultCard}>
                    <div style={styles.resultHeader}>
                      <span style={styles.resultType}>🏗️ Construction</span>
                    </div>
                    <h3 style={styles.resultTitle}>{metadata.title || 'Untitled'}</h3>
                    {metadata.description && (
                      <p style={styles.resultText}>
                        <span style={styles.resultTextStrong}>Details:</span> {metadata.description}
                      </p>
                    )}
                    {metadata.reference && (
                      <p style={styles.resultText}>
                        <span style={styles.resultTextStrong}>Reference:</span> {metadata.reference}
                      </p>
                    )}
                    {metadata.buyer && (
                      <p style={styles.resultText}>
                        <span style={styles.resultTextStrong}>Buyer:</span> {metadata.buyer}
                      </p>
                    )}
                    {metadata.deadline && metadata.deadline !== 'N/A' && (
                      <p style={styles.resultText}>
                        <span style={styles.resultTextStrong}>Deadline:</span> {metadata.deadline}
                      </p>
                    )}
                    {/* <div style={styles.resultActions}>
                      <button 
                        style={styles.btnView}
                        onMouseEnter={(e) => e.target.style.background = '#d0e4f0'}
                        onMouseLeave={(e) => e.target.style.background = '#e8f4fd'}
                        onClick={() => alert(`View details for: ${metadata.title || 'Tender'}`)}
                      >
                        View Details
                      </button>
                      <button 
                        style={styles.btnAnalyze}
                        onMouseEnter={(e) => e.target.style.background = '#1a3a5c'}
                        onMouseLeave={(e) => e.target.style.background = '#2d6a8f'}
                        onClick={() => alert(`Analyze tender: ${metadata.title || 'Tender'}`)}
                      >
                        Analyze
                      </button>
                    </div> */}
                  </div>
                );
              })
            ) : (
              <div style={styles.emptyState}>
                <span style={styles.emptyIcon}>🔍</span>
                <h3 style={styles.emptyTitle}>No tenders found</h3>
                <p style={styles.emptyText}>Try a different search term</p>
              </div>
            )}
          </div>

          {/* Show raw response for debugging */}
          {results.raw_response && (
            <details style={{ marginTop: '20px' }}>
              <summary style={{ cursor: 'pointer', color: '#2d6a8f', fontWeight: 500 }}>
                📄 View Full Response
              </summary>
              <div style={styles.rawResponse}>
                {results.raw_response}
              </div>
            </details>
          )}
        </div>
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          .construction-agent {
            padding: 10px;
            margin-left: 0 !important;
          }
          .search-input {
            flex-direction: column;
          }
          .search-input input,
          .search-input button {
            width: 100%;
          }
          .result-actions {
            flex-direction: column;
          }
          .result-actions button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}

export default ConstructionAgentChat;
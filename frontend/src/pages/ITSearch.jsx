// // // components/ITSearch.jsx

// // import { useState } from 'react';
// // import '../styles/ITSearch.css';

// // function ITSearch() {
// //   const [query, setQuery] = useState('');
// //   const [response, setResponse] = useState('');
// //   const [loading, setLoading] = useState(false);
// //   const [error, setError] = useState('');

// //   const handleSearch = async () => {
// //     if (!query.trim()) return;

// //     try {
// //       setLoading(true);
// //       setError('');
// //       setResponse('');

// //       // Use the search endpoint directly (faster than chat)
// //       const res = await fetch('http://localhost:5000/api/agent/search', {
// //         method: 'POST',
// //         headers: { 'Content-Type': 'application/json' },
// //         body: JSON.stringify({ query })
// //       });

// //       const data = await res.json();
      
// //       if (data.success && data.results) {
// //         // Format results directly
// //         const formattedResults = formatResults(data.results);
// //         setResponse(formattedResults);
// //       } else {
// //         setError(data.error || 'Search failed');
// //       }
// //     } catch (err) {
// //       setError(err.message);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   const formatResults = (results) => {
// //     if (!results || results.length === 0) {
// //       return "No tenders found matching your query.";
// //     }

// //     const itTenders = results.filter(r => r.is_it);
// //     const generalTenders = results.filter(r => !r.is_it);

// //     let output = [];
    
// //     if (itTenders.length > 0) {
// //       output.push(`🔍 Found ${itTenders.length} IT-related tenders:\n`);
// //       itTenders.slice(0, 5).forEach((tender, i) => {
// //         output.push(
// //           `${i + 1}. 📄 ${tender.reference} - ${tender.title}\n` +
// //           `   🏛️ Buyer: ${tender.buyer}\n` +
// //           `   📅 Deadline: ${tender.deadline}\n` +
// //           `   💻 IT Tender\n`
// //         );
// //       });
// //     }

// //     if (generalTenders.length > 0) {
// //       if (itTenders.length > 0) {
// //         output.push(`\n📋 Other relevant tenders:\n`);
// //       }
// //       generalTenders.slice(0, 3).forEach((tender, i) => {
// //         output.push(
// //           `${i + 1}. 📄 ${tender.reference} - ${tender.title}\n` +
// //           `   🏛️ Buyer: ${tender.buyer}\n` +
// //           `   📅 Deadline: ${tender.deadline}\n`
// //         );
// //       });
// //     }

// //     return output.join('\n');
// //   };

// //   const handleKeyPress = (e) => {
// //     if (e.key === 'Enter' && !e.shiftKey) {
// //       e.preventDefault();
// //       handleSearch();
// //     }
// //   };

// //   return (
// //     <div className="it-search-container">
// //       <div className="search-header">
// //         <h2>💻 IT Tender Search</h2>
// //         <p>Find IT-related government tenders - Fast and efficient</p>
// //       </div>

// //       <div className="search-box">
// //         <div className="search-input-wrapper">
// //           <input
// //             type="text"
// //             value={query}
// //             onChange={(e) => setQuery(e.target.value)}
// //             onKeyPress={handleKeyPress}
// //             placeholder="Describe what you're looking for... e.g., 'software development' or 'cybersecurity'"
// //             disabled={loading}
// //             className="search-input"
// //           />
// //           <button 
// //             className="search-button"
// //             onClick={handleSearch} 
// //             disabled={loading || !query.trim()}
// //           >
// //             {loading ? '⏳ Searching...' : '🔍 Search'}
// //           </button>
// //         </div>
        
// //         <div className="suggestions">
// //           <span>Quick searches:</span>
// //           <button onClick={() => setQuery('software development')}>Software</button>
// //           <button onClick={() => setQuery('cybersecurity')}>Security</button>
// //           <button onClick={() => setQuery('network infrastructure')}>Networks</button>
// //           <button onClick={() => setQuery('digital transformation')}>Digital</button>
// //         </div>
// //       </div>

// //       {error && <div className="error">{error}</div>}

// //       {loading && (
// //         <div className="loading">
// //           <div className="spinner"></div>
// //           <p>Searching for tenders...</p>
// //         </div>
// //       )}

// //       {response && (
// //         <div className="response">
// //           <div className="response-content">
// //             {response.split('\n').map((line, index) => {
// //               if (line.startsWith('📄')) {
// //                 return <div key={index} className="tender-item">{line}</div>;
// //               }
// //               if (line.startsWith('💡')) {
// //                 return <div key={index} className="tip">{line}</div>;
// //               }
// //               if (line.trim() === '') {
// //                 return <div key={index} className="separator"></div>;
// //               }
// //               return <div key={index} className="line">{line}</div>;
// //             })}
// //           </div>
// //         </div>
// //       )}
// //     </div>
// //   );
// // }

// // export default ITSearch;

// // components/ITSearch.jsx

// import { useState } from 'react';
// import '../styles/ITSearch.css';

// function ITSearch() {
//   const [query, setQuery] = useState('');
//   const [tenders, setTenders] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState('');
//   const [expandedId, setExpandedId] = useState(null);
//   const [searchPerformed, setSearchPerformed] = useState(false);

//   const handleSearch = async () => {
//     if (!query.trim()) return;

//     try {
//       setLoading(true);
//       setError('');
//       setTenders([]);
//       setSearchPerformed(true);
//       setExpandedId(null);

//       const res = await fetch('http://localhost:5000/api/agent/search', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ query })
//       });

//       const data = await res.json();
      
//       if (data.success && data.results) {
//         setTenders(data.results);
//       } else {
//         setError(data.error || 'Search failed');
//         setTenders([]);
//       }
//     } catch (err) {
//       setError(err.message);
//       setTenders([]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleKeyPress = (e) => {
//     if (e.key === 'Enter' && !e.shiftKey) {
//       e.preventDefault();
//       handleSearch();
//     }
//   };

//   const toggleExpand = (index) => {
//     setExpandedId(expandedId === index ? null : index);
//   };

//   return (
//     <div className="it-search-container">
//       <div className="search-header">
//         <h2>💻 IT Tender Search</h2>
//         <p>Find IT-related government tenders - Fast and efficient</p>
//       </div>

//       <div className="search-box">
//         <div className="search-input-wrapper">
//           <input
//             type="text"
//             value={query}
//             onChange={(e) => setQuery(e.target.value)}
//             onKeyPress={handleKeyPress}
//             placeholder="Describe what you're looking for... e.g., 'software development' or 'cybersecurity'"
//             disabled={loading}
//             className="search-input"
//           />
//           <button 
//             className="search-button"
//             onClick={handleSearch} 
//             disabled={loading || !query.trim()}
//           >
//             {loading ? '⏳ Searching...' : '🔍 Search'}
//           </button>
//         </div>
        
//         <div className="suggestions">
//           <span>Quick searches:</span>
//           <button onClick={() => setQuery('software development')}>Software</button>
//           <button onClick={() => setQuery('cybersecurity')}>Security</button>
//           <button onClick={() => setQuery('network infrastructure')}>Networks</button>
//           <button onClick={() => setQuery('digital transformation')}>Digital</button>
//           <button onClick={() => setQuery('cloud services')}>Cloud</button>
//           <button onClick={() => setQuery('ai machine learning')}>AI/ML</button>
//         </div>
//       </div>

//       {error && <div className="error-banner">{error}</div>}

//       {loading && (
//         <div className="loading">
//           <div className="spinner"></div>
//           <p>Searching for tenders...</p>
//         </div>
//       )}

//       {!loading && searchPerformed && tenders.length === 0 && (
//         <div className="no-results">
//           <p>📋 No tenders found matching your query</p>
//           <small>Try adjusting your search terms or use different keywords</small>
//         </div>
//       )}

//       {!loading && tenders.length > 0 && (
//         <>
//           <div className="results-header">
//             <h3>
//               Found {tenders.length} tenders 
//               {query && <span> for "{query}"</span>}
//               {/* <span className="result-count-badge">
//                 {tenders.filter(t => t.is_it).length} IT-related
//               </span> */}
//             </h3>
//           </div>

//           <div className="tenders-list">
//             {tenders.map((tender, index) => {
//   const isExpanded = expandedId === index;
//   const isIT = tender.is_it;

//   return (
//     <div key={index} className={`tender-card ${isIT ? 'it-tender' : ''}`}>
//       <div className="tender-header">
//         <div className="tender-ref-title">
//           <span className="tender-ref">{tender.reference || 'N/A'}</span>
//           <h3 className="tender-title">{tender.title || 'Untitled'}</h3>
//           {isIT && (
//             <span className={`it-badge ${tender.it_confidence?.toLowerCase() || ''}`}>
//               💻 IT {tender.it_confidence || ''}
//             </span>
//           )}
//           {!isIT && (
//             <span className="general-badge">📄 General</span>
//           )}
//         </div>
//         <button
//           className="expand-btn"
//           onClick={() => toggleExpand(index)}
//         >
//           {isExpanded ? '▼' : '▶'}
//         </button>
//       </div>

//                   <div className="tender-meta">
//                     <div className="meta-item">
//                       <span className="meta-label">Buyer:</span>
//                       <span className="meta-value">{tender.buyer || 'N/A'}</span>
//                     </div>
//                     <div className="meta-item">
//                       <span className="meta-label">Published:</span>
//                       <span className="meta-value">{tender.publication_date || 'N/A'}</span>
//                     </div>
//                     <div className="meta-item">
//                       <span className="meta-label">Deadline:</span>
//                       <span className="meta-value deadline">{tender.deadline || 'N/A'}</span>
//                     </div>
//                   </div>

//                   {isExpanded && (
//         <div className="tender-details">
//           {/* ... existing details ... */}
//           {tender.it_matches && tender.it_matches.length > 0 && (
//             <div className="detail-row">
//               <strong>IT Matches:</strong>
//               <span className="it-matches">{tender.it_matches.join(', ')}</span>
//             </div>
//           )}
//         </div>
//       )}
//     </div>
//   );
// })}
//           </div>
//         </>
//       )}
//     </div>
//   );
// }

// export default ITSearch;



// components/ITSearch.jsx - FIXED VERSION
import { useState } from 'react';
import '../styles/ITSearch.css';

function ITSearch() {
  const [query, setQuery] = useState('');
  const [tenders, setTenders] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [expandedId, setExpandedId] = useState(null);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError('');
      setTenders([]);
      setSearchPerformed(true);
      setExpandedId(null);

      const res = await fetch('http://localhost:5000/api/agent/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });

      const data = await res.json();
      console.log('📡 Search response:', data); // Debug log
      
      if (data.success && data.results) {
        setTenders(data.results);
      } else {
        setError(data.error || 'Search failed');
        setTenders([]);
      }
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message);
      setTenders([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSearch();
    }
  };

  const toggleExpand = (index) => {
    setExpandedId(expandedId === index ? null : index);
  };

const getTenderSourceUrl = (tender) => {
  // Si l'URL est déjà stockée (source_url)
  if (tender.source_url) {
    return tender.source_url;
  }
  
  const source = tender.source || 'TUNEPS';
  const reference = tender.reference;
  
  if (!reference) return null;
  
  // Générer l'URL selon la source
  if (source.toUpperCase() === 'HAICOP') {
    return `https://www.marchespublics.gov.tn/fr/appels-doffres/${reference}`;
  }
  
  if (source.toUpperCase() === 'TUNEPS') {
    // Si on a tender_id, construire l'URL complète
    if (tender.tender_id) {
      return `https://www.tuneps.tn/portail/offres/details/${tender.tender_id}/${reference}`;
    }
    return null;
  }
  
  return null;
};





  return (
    <div className="it-search-container" style={{ marginLeft: '280px', padding: '20px', maxWidth: '1200px' }}>
      <div className="search-header" style={{ background: 'linear-gradient(135deg, #1a3a5c, #2d6a8f)', color: 'white', padding: '30px 40px', borderRadius: '12px', marginBottom: '30px' }}>
        <h2 style={{ margin: 0 }}>💻 IT Tender Search</h2>
        <p style={{ margin: '8px 0 0 0', opacity: 0.9 }}>Find IT-related government tenders - Fast and efficient</p>
      </div>

      <div className="search-box" style={{ background: 'white', padding: '24px 30px', borderRadius: '12px', boxShadow: '0 2px 10px rgba(0,0,0,0.08)', marginBottom: '30px' }}>
        <div className="search-input-wrapper" style={{ display: 'flex', gap: '12px' }}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Describe what you're looking for... e.g., 'software development' or 'cybersecurity'"
            disabled={loading}
            className="search-input"
            style={{ flex: 1, padding: '14px 20px', border: '2px solid #e0e6ed', borderRadius: '8px', fontSize: '16px' }}
          />
          <button 
            className="search-button"
            onClick={handleSearch} 
            disabled={loading || !query.trim()}
            style={{ padding: '14px 32px', background: 'linear-gradient(135deg, #2d6a8f, #1a3a5c)', color: 'white', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 600, cursor: 'pointer' }}
          >
            {loading ? '⏳ Searching...' : '🔍 Search'}
          </button>
        </div>
        
        <div className="suggestions" style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ color: '#6b7b8d', fontSize: '14px' }}>Quick searches:</span>
          <button onClick={() => setQuery('software development')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>Software</button>
          <button onClick={() => setQuery('cybersecurity')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>Security</button>
          <button onClick={() => setQuery('network infrastructure')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>Networks</button>
          {/* <button onClick={() => setQuery('digital transformation')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>Digital</button> */}
          <button onClick={() => setQuery('cloud services')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>Cloud</button>
          <button onClick={() => setQuery('ai machine learning')} style={{ padding: '4px 12px', background: '#f0f2f5', border: '1px solid #e0e6ed', borderRadius: '4px', cursor: 'pointer' }}>AI/ML</button>
        </div>
      </div>

      {error && <div className="error-banner" style={{ background: '#fdecea', padding: '12px 16px', borderRadius: '8px', color: '#c0392b', marginBottom: '16px' }}>❌ {error}</div>}

      {loading && (
        <div className="loading" style={{ textAlign: 'center', padding: '40px' }}>
          <div className="spinner"></div>
          <p>Searching for tenders...</p>
        </div>
      )}

      {!loading && searchPerformed && tenders.length === 0 && (
        <div className="no-results" style={{ textAlign: 'center', padding: '40px', color: '#6b7b8d' }}>
          <p>📋 No tenders found matching your query</p>
          <small>Try adjusting your search terms or use different keywords</small>
        </div>
      )}

      {!loading && tenders.length > 0 && (
        <>
          <div className="results-header" style={{ marginBottom: '16px' }}>
            <h3 style={{ color: '#2c3e50' }}>
              Found {tenders.length} tenders 
              {query && <span> for "<strong>{query}</strong>"</span>}
            </h3>
          </div>

          <div className="tenders-list" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {tenders.map((tender, index) => {
              const isExpanded = expandedId === index;
              const isIT = tender.is_it || false;

              return (
                <div key={index} className={`tender-card ${isIT ? 'it-tender' : ''}`} style={{ 
                  background: 'white', 
                  borderRadius: '10px', 
                  padding: '20px 24px', 
                  boxShadow: '0 2px 10px rgba(0,0,0,0.08)',
                  borderLeft: isIT ? '4px solid #2d6a8f' : '4px solid #e0e6ed'
                }}>
                  <div className="tender-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div className="tender-ref-title" style={{ flex: 1 }}>
                      <span className="tender-ref" style={{ fontSize: '12px', color: '#6b7b8d' }}>{tender.reference || 'N/A'}</span>
                      <h3 className="tender-title" style={{ margin: '4px 0 8px 0', fontSize: '16px', color: '#1a3a5c' }}>{tender.title || 'Untitled'}</h3>
                      {isIT && (
                        <span className={`it-badge ${tender.it_confidence?.toLowerCase() || ''}`} style={{ 
                          background: '#e8f4fd', 
                          color: '#2d6a8f', 
                          padding: '2px 10px', 
                          borderRadius: '12px', 
                          fontSize: '12px', 
                          fontWeight: 500,
                          display: 'inline-block'
                        }}>
                          💻 IT {tender.it_confidence || ''}
                        </span>
                      )}
                      {!isIT && (
                        <span className="general-badge" style={{ 
                          background: '#f0f2f5', 
                          color: '#6b7b8d', 
                          padding: '2px 10px', 
                          borderRadius: '12px', 
                          fontSize: '12px', 
                          fontWeight: 500,
                          display: 'inline-block'
                        }}>
                          📄 General
                        </span>
                      )}
                    </div>
                    {/* <button
                      className="expand-btn"
                      onClick={() => toggleExpand(index)}
                      style={{ background: 'none', border: 'none', fontSize: '18px', cursor: 'pointer', color: '#2d6a8f' }}
                    >
                      {isExpanded ? '▼' : '▶'}
                    </button> */}
                  </div>

                  <div className="tender-meta" style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', marginTop: '8px' }}>
                    <div className="meta-item">
                      <span className="meta-label" style={{ color: '#6b7b8d', fontSize: '13px' }}>Buyer:</span>
                      <span className="meta-value" style={{ color: '#2c3e50', fontSize: '13px', marginLeft: '4px' }}>{tender.buyer || 'N/A'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label" style={{ color: '#6b7b8d', fontSize: '13px' }}>Published:</span>
                      <span className="meta-value" style={{ color: '#2c3e50', fontSize: '13px', marginLeft: '4px' }}>{tender.publication_date || 'N/A'}</span>
                    </div>
                    <div className="meta-item">
                      <span className="meta-label" style={{ color: '#6b7b8d', fontSize: '13px' }}>Deadline:</span>
                      <span className="meta-value deadline" style={{ color: '#e74c3c', fontSize: '13px', fontWeight: 600, marginLeft: '4px' }}>{tender.deadline || 'N/A'}</span>
                    </div>
                  </div>

                  {isExpanded && tender.content && (
                    <div className="tender-details" style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e0e6ed' }}>
                      <div className="detail-row" style={{ fontSize: '14px', color: '#4a5b6e' }}>
                        <p style={{ margin: '8px 0' }}>{tender.content}</p>
                        {tender.it_matches && tender.it_matches.length > 0 && (
                          <div style={{ marginTop: '8px' }}>
                            <strong>IT Matches:</strong>
                            <span className="it-matches" style={{ marginLeft: '8px' }}>{tender.it_matches.join(', ')}</span>
                          </div>
                        )}
                        <div style={{ marginTop: '8px' }}>
                          <strong>Source:</strong>
                          <span style={{ marginLeft: '8px' }}>{tender.source || 'Unknown'}</span>
                        </div>
                      </div>
                    </div>
                  )}
                  {/* ✅ BOUTON VERS LA SOURCE */}
{getTenderSourceUrl(tender) && (
  <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #e0e6ed' }}>
    <a 
      href={getTenderSourceUrl(tender)} 
      target="_blank" 
      rel="noopener noreferrer"
      style={{
        display: 'inline-block',
        padding: '6px 16px',
        background: 'linear-gradient(135deg, #1a237e, #0d47a1)',
        color: 'white',
        border: 'none',
        borderRadius: '4px',
        fontSize: '13px',
        fontWeight: 500,
        textDecoration: 'none',
        cursor: 'pointer',
        transition: 'all 0.3s ease'
      }}
      onMouseEnter={(e) => {
        e.target.style.background = 'linear-gradient(135deg, #0d47a1, #1a237e)';
        e.target.style.transform = 'translateY(-1px)';
        e.target.style.boxShadow = '0 4px 12px rgba(26, 35, 126, 0.3)';
      }}
      onMouseLeave={(e) => {
        e.target.style.background = 'linear-gradient(135deg, #1a237e, #0d47a1)';
        e.target.style.transform = 'translateY(0)';
        e.target.style.boxShadow = 'none';
      }}
    >
      🔗 Voir sur {tender.source || 'TUNEPS'}
    </a>
  </div>
)}
                </div>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}

export default ITSearch;
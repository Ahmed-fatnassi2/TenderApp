// import { useState, useEffect } from 'react';
// import { apiService } from '../services/api';
// import '../styles/Tenders.css';

// function Tenders() {
//   const [allTenders, setAllTenders] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState('');
//   const [searchTerm, setSearchTerm] = useState('');
//   const [isSmartSearch, setIsSmartSearch] = useState(false);
//   const [smartResults, setSmartResults] = useState(null);
//   const [expandedId, setExpandedId] = useState(null);
//   const [currentPage, setCurrentPage] = useState(1);
//   const itemsPerPage = 20;

//   useEffect(() => {
//     fetchTenders();
//   }, []);

//   const fetchTenders = async () => {
//     try {
//       setLoading(true);
//       // Fetch all tenders but with large limit
//       const response = await apiService.getTenders(1, 10000);
//       const tenderData = Array.isArray(response) ? response : response.data || [];
//       setAllTenders(tenderData);
//       setCurrentPage(1);
//       setError('');
//     } catch (err) {
//       setError('Failed to fetch tenders');
//       console.error(err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleDelete = async (tenderId) => {
//     if (!window.confirm('Are you sure you want to delete this tender?')) {
//       return;
//     }

//     try {
//       await apiService.deleteTender(tenderId);
//       setAllTenders(allTenders.filter((t) => t.id !== tenderId));
//     } catch (err) {
//       setError('Failed to delete tender');
//       console.error(err);
//     }
//   };

//   const handleSearch = async (e) => {
//     const term = e.target.value;
//     setSearchTerm(term);
//     setCurrentPage(1);

//     if (isSmartSearch && term.length > 3) {
//       try {
//         setLoading(true);
//         const results = await apiService.semanticSearch(term);
//         setSmartResults(results);
//       } catch (err) {
//         console.error('Smart search failed:', err);
//       } finally {
//         setLoading(false);
//       }
//     } else if (!isSmartSearch) {
//       setSmartResults(null);
//     }
//   };

//   const toggleSmartSearch = () => {
//     setIsSmartSearch(!isSmartSearch);
//     if (isSmartSearch) {
//       setSmartResults(null);
//     }
//   };

//   const filteredTenders = smartResults || allTenders.filter(
//     (tender) =>
//       tender.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
//       tender.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
//       tender.buyer?.toLowerCase().includes(searchTerm.toLowerCase())
//   );

//   // Pagination logic
//   const totalPages = Math.ceil(filteredTenders.length / itemsPerPage);
//   const startIndex = (currentPage - 1) * itemsPerPage;
//   const paginatedTenders = filteredTenders.slice(startIndex, startIndex + itemsPerPage);

//   const handlePreviousPage = () => {
//     if (currentPage > 1) {
//       setCurrentPage(currentPage - 1);
//       window.scrollTo({ top: 0, behavior: 'smooth' });
//     }
//   };

//   const handleNextPage = () => {
//     if (currentPage < totalPages) {
//       setCurrentPage(currentPage + 1);
//       window.scrollTo({ top: 0, behavior: 'smooth' });
//     }
//   };

//   const handlePageClick = (page) => {
//     setCurrentPage(page);
//     window.scrollTo({ top: 0, behavior: 'smooth' });
//   };

//   return (
//     <div className="tenders-container">
//       <div className="tenders-header">
//         <h2>Government Tenders</h2>
//         <p>Total: {filteredTenders.length} tenders {searchTerm ? 'found' : 'available'}</p>
//       </div>

//       <div className="tenders-controls">
//         <div className="search-box">
//           <input
//             type="text"
//             placeholder={isSmartSearch ? "Describe what you're looking for (Smart Search)..." : "Search by title, reference, or buyer..."}
//             value={searchTerm}
//             onChange={handleSearch}
//           />
//           <span className="search-icon">🔍</span>
//         </div>

//         <div className={`smart-search-toggle ${isSmartSearch ? 'active' : ''}`} onClick={toggleSmartSearch}>
//           <div className="toggle-switch">
//             <input type="checkbox" checked={isSmartSearch} readOnly />
//             <span className="slider"></span>
//           </div>
//           <span className="smart-search-label">
//             Smart Search <span className="smart-search-badge">AI</span>
//           </span>
//         </div>
//         <button className="refresh-btn" onClick={fetchTenders} disabled={loading}>
//           {loading ? 'Loading...' : '🔄 Refresh'}
//         </button>
//       </div>

//       {error && <div className="error-banner">{error}</div>}

//       {loading ? (
//         <div className="loading">
//           <div className="spinner"></div>
//           <p>Loading tenders...</p>
//         </div>
//       ) : filteredTenders.length === 0 ? (
//         <div className="no-results">
//           <p>📋 No tenders found</p>
//           <small>Try adjusting your search or refresh the data</small>
//         </div>
//       ) : (
//         <>
//           <div className="tenders-list">
//             {paginatedTenders.map((tender) => (
//               <div key={tender.id} className="tender-card">
//                 <div className="tender-header">
//                   <div className="tender-ref-title">
//                     <span className="tender-ref">{tender.reference}</span>
//                     <h3 className="tender-title">{tender.title}</h3>
//                   </div>
//                   <button
//                     className="expand-btn"
//                     onClick={() =>
//                       setExpandedId(expandedId === tender.id ? null : tender.id)
//                     }
//                   >
//                     {expandedId === tender.id ? '▼' : '▶'}
//                   </button>
//                 </div>

//                 <div className="tender-meta">
//                   <div className="meta-item">
//                     <span className="meta-label">Buyer:</span>
//                     <span className="meta-value">{tender.buyer || 'N/A'}</span>
//                   </div>
//                   <div className="meta-item">
//                     <span className="meta-label">Published:</span>
//                     <span className="meta-value">{tender.publication_date || 'N/A'}</span>
//                   </div>
//                   <div className="meta-item">
//                     <span className="meta-label">Deadline:</span>
//                     <span className="meta-value deadline">{tender.deadline || 'N/A'}</span>
//                   </div>
//                 </div>

//                 {expandedId === tender.id && (
//                   <div className="tender-details">
//                     <div className="detail-row">
//                       <strong>Reference:</strong>
//                       <span>{tender.reference}</span>
//                     </div>
//                     <div className="detail-row">
//                       <strong>Buyer:</strong>
//                       <span>{tender.buyer || 'N/A'}</span>
//                     </div>
//                     <div className="detail-row">
//                       <strong>Publication Date:</strong>
//                       <span>{tender.publication_date || 'N/A'}</span>
//                     </div>
//                     <div className="detail-row">
//                       <strong>Deadline:</strong>
//                       <span>{tender.deadline || 'N/A'}</span>
//                     </div>
//                     <div className="detail-row">
//                       <strong>Source:</strong>
//                       <span>{tender.source || 'Unknown'}</span>
//                     </div>
//                     {tender.scraped_at && (
//                       <div className="detail-row">
//                         <strong>Scraped At:</strong>
//                         <span>{new Date(tender.scraped_at).toLocaleString()}</span>
//                       </div>
//                     )}

//                     <div className="tender-actions">
//                       <button className="action-view">View Details</button>
//                       <button
//                         className="action-delete"
//                         onClick={() => handleDelete(tender.id)}
//                       >
//                         Delete
//                       </button>
//                     </div>
//                   </div>
//                 )}
//               </div>
//             ))}
//           </div>

//           {/* Pagination Controls */}
//           <div className="pagination-container">
//             <button 
//               className="pagination-btn prev-btn" 
//               onClick={handlePreviousPage}
//               disabled={currentPage === 1}
//             >
//               ← Previous
//             </button>
            
//             <div className="pagination-pages">
//               {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
//                 <button
//                   key={page}
//                   className={`pagination-page ${currentPage === page ? 'active' : ''}`}
//                   onClick={() => handlePageClick(page)}
//                 >
//                   {page}
//                 </button>
//               ))}
//             </div>

//             <button 
//               className="pagination-btn next-btn"
//               onClick={handleNextPage}
//               disabled={currentPage === totalPages}
//             >
//               Next →
//             </button>

//             <div className="pagination-info">
//               Page {currentPage} of {totalPages}
//             </div>
//           </div>
//         </>
//       )}
//     </div>
//   );
// }

// export default Tenders;
// components/Tenders.js

// components/Tenders.js

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/Tenders.css';

function Tenders() {
  const [allTenders, setAllTenders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [isSmartSearch, setIsSmartSearch] = useState(false);
  const [smartResults, setSmartResults] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [isIndexing, setIsIndexing] = useState(false);
  const [debugInfo, setDebugInfo] = useState(null);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchTenders();
  }, []);

  const fetchTenders = async () => {
    try {
      setLoading(true);
      const response = await apiService.getTenders(1, 10000);
      const tenderData = Array.isArray(response) ? response : response.data || [];
      setAllTenders(tenderData);
      setCurrentPage(1);
      setError('');
    } catch (err) {
      setError('Failed to fetch tenders');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (tenderId) => {
    if (!window.confirm('Are you sure you want to delete this tender?')) {
      return;
    }

    try {
      await apiService.deleteTender(tenderId);
      setAllTenders(allTenders.filter((t) => t.id !== tenderId));
    } catch (err) {
      setError('Failed to delete tender');
      console.error(err);
    }
  };

  const handleSearch = async (e) => {
    const term = e.target.value;
    setSearchTerm(term);
    setCurrentPage(1);
    setDebugInfo(null);

    // Reset smart results when search is cleared
    if (!term.trim()) {
      console.log('[handleSearch] Search cleared, resetting smartResults');
      setSmartResults(null);
      return;
    }

    console.log(`[handleSearch] isSmartSearch: ${isSmartSearch}, term: "${term}", length: ${term.length}`);

    if (isSmartSearch && term.length > 3) {
      try {
        setLoading(true);
        setError('');
        console.log('[handleSearch] Performing semantic search for:', term);
        const results = await apiService.semanticSearch(term, 5, 0.75); // Using 5 to match WSL test
        console.log('[handleSearch] Semantic search results:', results);
        console.log('[handleSearch] Number of results:', results.length);
        
        // CRITICAL: Set smartResults regardless of whether we got results
        setSmartResults(results);
        
        setDebugInfo({
          resultCount: results.length,
          searchTerm: term,
          timestamp: new Date().toISOString()
        });
        
        console.log(`[handleSearch] smartResults set with ${results.length} items`);
      } catch (err) {
        setError('Smart search failed: ' + err.message);
        console.error('[handleSearch] Smart search failed:', err);
        setSmartResults([]); // Set to empty array on error
      } finally {
        setLoading(false);
      }
    } else if (!isSmartSearch) {
      // If not smart search, clear smart results
      console.log('[handleSearch] Not smart search, clearing smartResults');
      setSmartResults(null);
    }
  };

  // CRITICAL FIX: Determine which tenders to display with debugging
  const getDisplayedTenders = () => {
    console.log('[getDisplayedTenders] isSmartSearch:', isSmartSearch);
    console.log('[getDisplayedTenders] smartResults:', smartResults);
    console.log('[getDisplayedTenders] smartResults type:', typeof smartResults);
    console.log('[getDisplayedTenders] smartResults is array:', Array.isArray(smartResults));
    console.log('[getDisplayedTenders] smartResults length:', smartResults?.length);
    
    // If smart search is active
    if (isSmartSearch) {
      // If smartResults is null, it means no search has been performed yet
      if (smartResults === null) {
        console.log('[getDisplayedTenders] Smart search active but no results yet, returning empty array');
        return [];
      }
      // smartResults is either an array of results or empty array
      console.log(`[getDisplayedTenders] Returning ${smartResults.length} smart results`);
      return smartResults;
    }
    
    // Regular search (non-smart)
    if (!searchTerm.trim()) {
      console.log(`[getDisplayedTenders] Regular search, showing all ${allTenders.length} tenders`);
      return allTenders;
    }
    
    const filtered = allTenders.filter(
      (tender) =>
        tender.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tender.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        tender.buyer?.toLowerCase().includes(searchTerm.toLowerCase())
    );
    console.log(`[getDisplayedTenders] Regular search filtered to ${filtered.length} tenders`);
    return filtered;
  };

  const toggleSmartSearch = () => {
    const newState = !isSmartSearch;
    setIsSmartSearch(newState);
    
    // Clear smart results when toggling off
    if (!newState) {
      setSmartResults(null);
      setDebugInfo(null);
    }
    
    // If turning on and there's a search term, run search
    if (newState && searchTerm.length > 3) {
      handleSearch({ target: { value: searchTerm } });
    }
  };

  const handleIndexAll = async () => {
    if (!window.confirm('This will index all tenders for semantic search. Continue?')) {
      return;
    }

    try {
      setIsIndexing(true);
      setError('');
      const result = await apiService.indexAllTenders();
      console.log('Indexing result:', result);
      alert(`Indexing started: ${result.message || 'Submitted for indexing'}`);
    } catch (err) {
      setError('Failed to index tenders: ' + err.message);
      console.error('Indexing failed:', err);
    } finally {
      setIsIndexing(false);
    }
  };

  // CRITICAL FIX: Determine which tenders to display
  // const getDisplayedTenders = () => {
  //   // If smart search is active and we have results (even empty array)
  //   if (isSmartSearch) {
  //     // If smartResults is null, it means no search has been performed yet
  //     if (smartResults === null) {
  //       return [];
  //     }
  //     // smartResults is either an array of results or empty array
  //     return smartResults;
  //   }
    
  //   // Regular search (non-smart)
  //   if (!searchTerm.trim()) {
  //     return allTenders;
  //   }
    
  //   return allTenders.filter(
  //     (tender) =>
  //       tender.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //       tender.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
  //       tender.buyer?.toLowerCase().includes(searchTerm.toLowerCase())
  //   );
  // };

  const displayedTenders = getDisplayedTenders();
  const totalPages = Math.ceil(displayedTenders.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const paginatedTenders = displayedTenders.slice(startIndex, startIndex + itemsPerPage);

  const handlePreviousPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(currentPage + 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const handlePageClick = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Helper function to display date
  const displayDate = (tender) => {
    if (tender.publication_date_display && tender.publication_date_display !== 'N/A') {
      return tender.publication_date_display;
    }
    if (tender.publication_date && tender.publication_date !== 'N/A') {
      try {
        const date = new Date(tender.publication_date);
        if (!isNaN(date.getTime())) {
          return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          });
        }
      } catch (e) {
        // Ignore
      }
    }
    return 'N/A';
  };

  const displayDeadline = (tender) => {
    if (tender.deadline_display && tender.deadline_display !== 'N/A') {
      return tender.deadline_display;
    }
    if (tender.deadline && tender.deadline !== 'N/A') {
      try {
        const date = new Date(tender.deadline);
        if (!isNaN(date.getTime())) {
          return date.toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
          });
        }
      } catch (e) {
        // Ignore
      }
    }
    return 'N/A';
  };

  // Determine if we should show a message about smart search results
  const getSmartSearchMessage = () => {
    if (!isSmartSearch) return null;
    if (smartResults === null) return 'Enter a search query to use Smart Search';
    if (smartResults.length === 0) return 'No semantically similar tenders found';
    return null;
  };



// Obtenir l'URL du tender sur la source
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
    <div className="tenders-container">
      <div className="tenders-header">
        <h2>Government Tenders</h2>
        <p>
          {isSmartSearch && smartResults !== null ? (
            <>
              Found {smartResults.length} semantically similar tenders 
              {searchTerm && ` for "${searchTerm}"`}
              <span className="smart-search-indicator"> 🤖 AI Search</span>
            </>
          ) : (
            <>
              Total: {displayedTenders.length} tenders{' '}
              {searchTerm ? 'found' : 'available'}
            </>
          )}
        </p>
        {debugInfo && isSmartSearch && (
          <div className="debug-info">
            <small>
              Found {debugInfo.resultCount} results for "{debugInfo.searchTerm}" 
              (at {new Date(debugInfo.timestamp).toLocaleTimeString()})
            </small>
          </div>
        )}
      </div>

      <div className="tenders-controls">
        <div className="search-box">
          <input
            type="text"
            placeholder={
              isSmartSearch 
                ? "Describe what you're looking for (Smart Search)..." 
                : "Search by title, reference, or buyer..."
            }
            value={searchTerm}
            onChange={handleSearch}
          />
          {/* <span className="search-icon">🔍</span> */}
        </div>

        {/* <div className="control-buttons">
          <div className={`smart-search-toggle ${isSmartSearch ? 'active' : ''}`} onClick={toggleSmartSearch}>
            <div className="toggle-switch">
              <input type="checkbox" checked={isSmartSearch} readOnly />
              <span className="slider"></span>
            </div>
            <span className="smart-search-label">
              Smart Search <span className="smart-search-badge">AI</span>
            </span>
          </div>

          <button 
            className="index-btn" 
            onClick={handleIndexAll} 
            disabled={isIndexing || loading}
            title="Index all tenders for semantic search"
          >
            {isIndexing ? '⏳ Indexing...' : '📊 Index All'}
          </button>

          <button className="refresh-btn" onClick={fetchTenders} disabled={loading}>
            {loading ? 'Loading...' : '🔄 Refresh'}
          </button>
        </div> */}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {/* Show smart search info message */}
      {getSmartSearchMessage() && (
        <div className="info-banner">
          {getSmartSearchMessage()}
        </div>
      )}

      {loading ? (
        <div className="loading">
          <div className="spinner"></div>
          <p>Loading tenders...</p>
        </div>
      ) : displayedTenders.length === 0 ? (
        <div className="no-results">
          <p>📋 No tenders found</p>
          <small>
            {isSmartSearch && smartResults !== null 
              ? 'Try a different search query' 
              : searchTerm && !isSmartSearch
              ? 'Try adjusting your search or enable Smart Search'
              : 'Try adjusting your search or refresh the data'}
          </small>
        </div>
      ) : (
        <>
          <div className="tenders-list">
            {paginatedTenders.map((tender, index) => (
              <div key={tender.id || tender.reference || `tender-${index}`} className="tender-card">
                <div className="tender-header">
                  <div className="tender-ref-title">
                    <span className="tender-ref">{tender.reference || 'N/A'}</span>
                    <h3 className="tender-title">{tender.title || 'Untitled'}</h3>
                    {tender.similarity_score > 0 && (
                      <span className="similarity-badge">
                        {Math.round(tender.similarity_score * 100)}% match
                      </span>
                    )}
                  </div>
                  <button
                    className="expand-btn"
                    onClick={() =>
                      setExpandedId(expandedId === tender.id ? null : tender.id)
                    }
                  >
                    {expandedId === tender.id ? '▼' : '▶'}
                  </button>
                </div>

                <div className="tender-meta">
                  <div className="meta-item">
                    <span className="meta-label">Buyer:</span>
                    <span className="meta-value">{tender.buyer || 'N/A'}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Published:</span>
                    <span className="meta-value">{displayDate(tender)}</span>
                  </div>
                  <div className="meta-item">
                    <span className="meta-label">Deadline:</span>
                    <span className="meta-value deadline">{displayDeadline(tender)}</span>
                  </div>
                </div>

                {expandedId === tender.id && (
                  <div className="tender-details">
                    <div className="detail-row">
                      <strong>Reference:</strong>
                      <span>{tender.reference || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <strong>Title:</strong>
                      <span>{tender.title || 'Untitled'}</span>
                    </div>
                    <div className="detail-row">
                      <strong>Buyer:</strong>
                      <span>{tender.buyer || 'N/A'}</span>
                    </div>
                    <div className="detail-row">
                      <strong>Publication Date:</strong>
                      <span>{displayDate(tender)}</span>
                    </div>
                    <div className="detail-row">
                      <strong>Deadline:</strong>
                      <span>{displayDeadline(tender)}</span>
                    </div>
                    <div className="detail-row">
                      <strong>Source:</strong>
                      <span>{tender.source || 'Unknown'}</span>
                    </div>
                    {tender.scraped_at && (
                      <div className="detail-row">
                        <strong>Scraped At:</strong>
                        <span>{new Date(tender.scraped_at).toLocaleString()}</span>
                      </div>
                    )}
                    {tender.similarity_score > 0 && (
                      <div className="detail-row">
                        <strong>Semantic Similarity:</strong>
                        <span className="similarity-score">
                          {Math.round(tender.similarity_score * 100)}%
                        </span>
                      </div>
                    )}
                    {tender.context && (
                      <div className="detail-row">
                        <strong>Context:</strong>
                        <p className="context-text">{tender.context}</p>
                      </div>
                    )}
                    {tender.content && (
                      <div className="detail-row">
                        <strong>Full Content:</strong>
                        <pre className="content-text">{tender.content}</pre>
                      </div>
                    )}

                    {getTenderSourceUrl(tender) && (
  <div className="tender-actions">
    <a 
      href={getTenderSourceUrl(tender)} 
      target="_blank" 
      rel="noopener noreferrer"
      className="btn-source"
    >
      🔗 Voir sur {tender.source || 'TUNEPS'}
    </a>
    <button
      className="action-delete"
      onClick={() => handleDelete(tender.id)}
    >
      Delete
    </button>
  </div>
)}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="pagination-container">
              <button 
                className="pagination-btn prev-btn" 
                onClick={handlePreviousPage}
                disabled={currentPage === 1}
              >
                ← Previous
              </button>
              
              <div className="pagination-pages">
                {Array.from({ length: Math.min(totalPages, 10) }, (_, i) => {
                  let page;
                  if (totalPages <= 10) {
                    page = i + 1;
                  } else if (currentPage <= 6) {
                    page = i + 1;
                  } else if (currentPage >= totalPages - 4) {
                    page = totalPages - 9 + i;
                  } else {
                    page = currentPage - 4 + i;
                  }
                  if (page > 0 && page <= totalPages) {
                    return (
                      <button
                        key={page}
                        className={`pagination-page ${currentPage === page ? 'active' : ''}`}
                        onClick={() => handlePageClick(page)}
                      >
                        {page}
                      </button>
                    );
                  }
                  return null;
                })}
                {totalPages > 10 && currentPage < totalPages - 4 && (
                  <span className="pagination-ellipsis">...</span>
                )}
              </div>

              <button 
                className="pagination-btn next-btn"
                onClick={handleNextPage}
                disabled={currentPage === totalPages}
              >
                Next →
              </button>

              <div className="pagination-info">
                Page {currentPage} of {totalPages}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Tenders;
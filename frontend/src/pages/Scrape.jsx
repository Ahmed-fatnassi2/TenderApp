// // import { useState } from 'react';
// // import { apiService } from '../services/api';
// // import '../styles/Scrape.css';

// // function Scrape() {
// //   const [loading, setLoading] = useState(false);
// //   const [result, setResult] = useState(null);
// //   const [error, setError] = useState('');

// //   const handleScrape = async () => {
// //     if (
// //       !window.confirm(
// //         'This will scrape new tenders from TUNEPS. Continue?'
// //       )
// //     ) {
// //       return;
// //     }

// //     try {
// //       setLoading(true);
// //       setError('');
// //       setResult(null);

// //       const data = await apiService.scrapeTenders();

// //       setResult(data);
// //     } catch (err) {
// //       setError(err.message || 'Failed to scrape tenders');
// //       console.error(err);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   return (
// //     <div className="scrape-container">
// //       <div className="scrape-header">
// //         <h2>Scrape Tenders</h2>
// //         <p>Fetch new government tenders from TUNEPS</p>
// //       </div>

// //       <div className="scrape-card">
// //         <div className="scrape-icon">🔄</div>
// //         <h3>Update Tender Data</h3>
// //         <p>
// //           Click the button below to scrape the latest tenders from the TUNEPS
// //           government portal. This may take a few moments.
// //         </p>

// //         {error && <div className="error-banner">{error}</div>}

// //         {result && (
// //           <div className="success-banner">
// //             <h4>✅ Scrape Completed Successfully!</h4>
// //             <div className="result-details">
// //               <div className="result-item">
// //                 <span className="label">New Tenders Added:</span>
// //                 <span className="value">{result.data?.new || result.new || 0}</span>
// //               </div>
// //               <div className="result-item">
// //                 <span className="label">Duplicates Skipped:</span>
// //                 <span className="value">
// //                   {result.data?.duplicates || result.duplicates || 0}
// //                 </span>
// //               </div>
// //               <div className="result-item">
// //                 <span className="label">Total in Database:</span>
// //                 <span className="value">{result.data?.total || result.total || 0}</span>
// //               </div>
// //             </div>
// //             <p className="result-message">{result.message || 'Data updated successfully!'}</p>
// //           </div>
// //         )}

// //         <button
// //           className="scrape-button"
// //           onClick={handleScrape}
// //           disabled={loading}
// //         >
// //           {loading ? (
// //             <>
// //               <span className="spinner"></span>
// //               Scraping in progress...
// //             </>
// //           ) : (
// //             'Start Scraping'
// //           )}
// //         </button>

// //         <div className="scrape-info">
// //           <h4>ℹ️ Information</h4>
// //           <ul>
// //             <li>Scrapes tenders from TUNEPS (Tunisian government portal)</li>
// //             <li>Only fetches tenders from 2026 with valid deadlines</li>
// //             <li>Automatically skips duplicate entries</li>
// //             <li>New tenders are added to the database</li>
// //             <li>Process may take several minutes depending on data volume</li>
// //           </ul>
// //         </div>
// //       </div>
// //     </div>
// //   );
// // }

// // export default Scrape;




// // components/Scrape.js

// // components/Scrape.jsx - Updated for multi-source scraper
// import { useState, useEffect } from 'react';
// import { apiService } from '../services/api';
// import '../styles/Scrape.css';

// function Scrape() {
//   const [loading, setLoading] = useState(false);
//   const [scrapingAll, setScrapingAll] = useState(false);
//   const [result, setResult] = useState(null);
//   const [error, setError] = useState('');
//   const [sources, setSources] = useState([]);
//   const [selectedSource, setSelectedSource] = useState('');
//   const [sourceResults, setSourceResults] = useState({});

//   // Fetch available sources on component mount
//   useEffect(() => {
//     fetchSources();
//   }, []);

//   const fetchSources = async () => {
//     try {
//       const response = await apiService.getScraperSources();
//       console.log('📡 Sources response:', response);
//       if (response.success && response.sources) {
//         setSources(response.sources);
//         if (response.sources.length > 0) {
//           setSelectedSource(response.sources[0].id);
//         }
//       }
//     } catch (error) {
//       console.error('Error fetching sources:', error);
//       setError('Failed to load scraper sources');
//     }
//   };

//   // Scrape a single source
//   const handleScrapeSource = async () => {
//     if (!selectedSource) {
//       setError('Please select a source to scrape');
//       return;
//     }

//     const source = sources.find(s => s.id === selectedSource);
//     if (!source) {
//       setError('Source not found');
//       return;
//     }

//     if (!window.confirm(`This will scrape new tenders from ${source.display_name}. Continue?`)) {
//       return;
//     }

//     try {
//       setLoading(true);
//       setError('');
//       setResult(null);

//       // Call the source-specific scrape endpoint
//       const data = await apiService.scrapeSource(selectedSource);
      
//       if (data.success) {
//         setResult(data);
//         setSourceResults(prev => ({
//           ...prev,
//           [selectedSource]: data
//         }));
//       } else {
//         setError(data.error || 'Failed to scrape source');
//       }
      
//     } catch (err) {
//       setError(err.message || 'Failed to scrape source');
//       console.error(err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   // Scrape ALL sources
//   const handleScrapeAll = async () => {
//     if (sources.length === 0) {
//       setError('No sources available to scrape');
//       return;
//     }

//     if (!window.confirm(`This will scrape new tenders from ALL ${sources.length} sources. Continue?`)) {
//       return;
//     }

//     try {
//       setScrapingAll(true);
//       setError('');
//       setResult(null);
//       setSourceResults({});

//       const results = {};
//       let totalNew = 0;
//       let totalDuplicates = 0;
//       let successfulSources = 0;
//       let failedSources = 0;

//       for (const source of sources) {
//         try {
//           const data = await apiService.scrapeSource(source.id);
//           results[source.id] = data;
//           setSourceResults(prev => ({ ...prev, [source.id]: data }));
          
//           if (data.success && data.data) {
//             totalNew += data.data.new || 0;
//             totalDuplicates += data.data.duplicates || 0;
//             successfulSources++;
//           } else {
//             failedSources++;
//           }
//         } catch (err) {
//           results[source.id] = { error: err.message };
//           setSourceResults(prev => ({ ...prev, [source.id]: { error: err.message } }));
//           failedSources++;
//         }
//       }

//       // Calculate total tenders
//       let totalTenders = 0;
//       sources.forEach(s => {
//         const result = results[s.id];
//         if (result && result.data) {
//           totalTenders += result.data.total || 0;
//         }
//       });

//       setResult({
//         success: true,
//         message: `Scraped ${totalNew} new tenders from ${successfulSources} sources (${failedSources} failed)`,
//         data: {
//           total_new: totalNew,
//           total_duplicates: totalDuplicates,
//           total_tenders: totalTenders,
//           successful_sources: successfulSources,
//           failed_sources: failedSources,
//           sources: results
//         }
//       });
      
//     } catch (err) {
//       setError(err.message || 'Failed to scrape all sources');
//       console.error(err);
//     } finally {
//       setScrapingAll(false);
//     }
//   };

//   const getSourceName = (sourceId) => {
//     const source = sources.find(s => s.id === sourceId);
//     return source ? source.display_name : 'Unknown';
//   };

//   const getSourceStatus = (sourceId) => {
//     const source = sources.find(s => s.id === sourceId);
//     return source ? source.is_active : false;
//   };
// // components/Scrape.jsx - Updated actions

// // Scrape a single source AND index
// const handleScrapeAndIndexSource = async () => {
//   if (!selectedSource) {
//     setError('Please select a source to scrape');
//     return;
//   }

//   const source = sources.find(s => s.id === selectedSource);
//   if (!source) {
//     setError('Source not found');
//     return;
//   }

//   if (!window.confirm(`This will scrape and index new tenders from ${source.display_name}. Continue?`)) {
//     return;
//   }

//   try {
//     setLoading(true);
//     setError('');
//     setResult(null);

//     // Use the combined endpoint
//     const data = await apiService.scrapeAndIndexSource(selectedSource);
    
//     if (data.success) {
//       setResult(data);
//       setSourceResults(prev => ({
//         ...prev,
//         [selectedSource]: data
//       }));
//     } else {
//       setError(data.error || 'Failed to scrape and index source');
//     }
    
//   } catch (err) {
//     setError(err.message || 'Failed to scrape and index source');
//     console.error(err);
//   } finally {
//     setLoading(false);
//   }
// };

// // Scrape ALL sources AND index
// const handleScrapeAllAndIndex = async () => {
//   if (sources.length === 0) {
//     setError('No sources available to scrape');
//     return;
//   }

//   if (!window.confirm(`This will scrape and index new tenders from ALL ${sources.length} sources. Continue?`)) {
//     return;
//   }

//   try {
//     setScrapingAll(true);
//     setError('');
//     setResult(null);
//     setSourceResults({});

//     // Use the combined endpoint
//     const data = await apiService.scrapeAllAndIndex();
    
//     if (data.success) {
//       setResult(data);
//       // Update source results from response
//       if (data.data && data.data.sources) {
//         const updatedResults = {};
//         Object.entries(data.data.sources).forEach(([id, result]) => {
//           updatedResults[id] = result;
//         });
//         setSourceResults(updatedResults);
//       }
//     } else {
//       setError(data.error || 'Failed to scrape and index all sources');
//     }
    
//   } catch (err) {
//     setError(err.message || 'Failed to scrape and index all sources');
//     console.error(err);
//   } finally {
//     setScrapingAll(false);
//   }
// };
//   return (
//     <div className="scrape-container">
//       <div className="scrape-header">
//         <h2>🔄 Multi-Source Scraper</h2>
//         <p>Fetch new government tenders from multiple sources</p>
//       </div>

//       <div className="scrape-card">
//         <div className="scrape-icon">🔌</div>
//         <h3>Scrape Tenders from All Sources</h3>
//         <p>
//           Select a source below to scrape individually, or click "Scrape All Sources" 
//           to fetch tenders from all configured sources at once.
//         </p>

//         {error && <div className="error-banner">{error}</div>}

//         {/* Source Selection */}
//         {sources.length > 0 && (
//           <div className="source-selection">
//             <label htmlFor="source-select">Select Source:</label>
//             <select
//               id="source-select"
//               value={selectedSource}
//               onChange={(e) => setSelectedSource(Number(e.target.value))}
//               disabled={loading || scrapingAll}
//             >
//               {sources.map((source) => (
//                 <option key={source.id} value={source.id}>
//                   {source.display_name || source.name} 
//                   {source.is_active ? ' 🟢' : ' 🔴'} 
//                   ({source.total_tenders || 0} tenders)
//                 </option>
//               ))}
//             </select>
//           </div>
//         )}

//         <div className="scrape-actions">
//   <button
//     className="scrape-button"
//     onClick={handleScrapeAndIndexSource}
//     disabled={loading || scrapingAll || !selectedSource || sources.length === 0}
//   >
//     {loading ? (
//       <>
//         <span className="spinner"></span>
//         Scraping & Indexing...
//       </>
//     ) : (
//       '🔄 Scrape & Index Selected'
//     )}
//   </button>

//   <button
//     className="scrape-button scrape-all"
//     onClick={handleScrapeAllAndIndex}
//     disabled={loading || scrapingAll || sources.length === 0}
//   >
//     {scrapingAll ? (
//       <>
//         <span className="spinner"></span>
//         Scraping & Indexing all...
//       </>
//     ) : (
//       '⚡ Scrape & Index All Sources'
//     )}
//   </button>
// </div>

//         {/* Results */}
//         {result && (
//           <div className="success-banner">
//             <h4>✅ Operation Completed Successfully!</h4>
            
//             {/* Overall Results */}
//             {result.data && result.data.total_new !== undefined && (
//               <div className="result-section">
//                 <h5>📊 Overall Results</h5>
//                 <div className="result-details">
//                   <div className="result-item">
//                     <span className="label">Total New Tenders:</span>
//                     <span className="value">{result.data.total_new || 0}</span>
//                   </div>
//                   {/* <div className="result-item">
//                     <span className="label">Total Duplicates:</span>
//                     <span className="value">{result.data.total_duplicates || 0}</span>
//                   </div>
//                   <div className="result-item">
//                     <span className="label">Total in Database:</span>
//                     <span className="value">{result.data.total_tenders || 0}</span>
//                   </div> */}
//                   <div className="result-item">
//                     <span className="label">Successful Sources:</span>
//                     <span className="value success">{result.data.successful_sources || 0}</span>
//                   </div>
//                   <div className="result-item">
//                     <span className="label">Failed Sources:</span>
//                     <span className="value failed">{result.data.failed_sources || 0}</span>
//                   </div>
//                 </div>
//               </div>
//             )}

//             {/* Per-Source Results */}
//             {Object.keys(sourceResults).length > 0 && (
//               <div className="result-section">
//                 <h5>📊 Per-Source Results</h5>
//                 {Object.entries(sourceResults).map(([sourceId, sourceResult]) => {
//                   const isActive = getSourceStatus(Number(sourceId));
//                   return (
//                     <div key={sourceId} className="source-result">
//                       <div className="source-result-header">
//                         <strong>
//                           {getSourceName(Number(sourceId))}
//                           {isActive ? ' 🟢' : ' 🔴'}
//                         </strong>
//                         {sourceResult.success ? (
//                           <span className="source-status success">✅ Success</span>
//                         ) : sourceResult.error ? (
//                           <span className="source-status error">❌ Failed</span>
//                         ) : (
//                           <span className="source-status">⏳ Pending</span>
//                         )}
//                       </div>
//                       {sourceResult.success && sourceResult.data && (
//                         <div className="source-result-details">
//                           <span>New: <strong>{sourceResult.data.new || 0}</strong></span>
//                           <span>Duplicates: <strong>{sourceResult.data.duplicates || 0}</strong></span>
//                           <span>Total: <strong>{sourceResult.data.total || 0}</strong></span>
//                         </div>
//                       )}
//                       {sourceResult.error && (
//                         <div className="source-error">❌ {sourceResult.error}</div>
//                       )}
//                     </div>
//                   );
//                 })}
//               </div>
//             )}

//             {/* Single Source Results (backward compatibility) */}
//             {result.data && result.data.total_new === undefined && result.data.new !== undefined && (
//               <div className="result-section">
//                 <h5>📊 Scrape Results</h5>
//                 <div className="result-details">
//                   <div className="result-item">
//                     <span className="label">New Tenders:</span>
//                     <span className="value">{result.data.new || 0}</span>
//                   </div>
//                   <div className="result-item">
//                     <span className="label">Duplicates:</span>
//                     <span className="value">{result.data.duplicates || 0}</span>
//                   </div>
//                   <div className="result-item">
//                     <span className="label">Total in DB:</span>
//                     <span className="value">{result.data.total || 0}</span>
//                   </div>
//                 </div>
//                 {result.data.new_tender_ids && result.data.new_tender_ids.length > 0 && (
//                   <div className="result-item">
//                     <span className="label">New Tender IDs:</span>
//                     <span className="value">{result.data.new_tender_ids.join(', ')}</span>
//                   </div>
//                 )}
//               </div>
//             )}

//             <p className="result-message">{result.message || 'Operation completed successfully!'}</p>
//           </div>
//         )}

//         {/* Available Sources Info */}
//         <div className="scrape-info">
//           <h4>ℹ️ Available Sources</h4>
//           {sources.length === 0 ? (
//             <p className="no-sources">No sources configured. Please add a scraper source first.</p>
//           ) : (
//             <ul>
//               {sources.map((source) => (
//                 <li key={source.id}>
//                   <strong>{source.display_name || source.name}</strong>
//                   {source.is_active ? (
//                     <span className="status-badge active">🟢 Active</span>
//                   ) : (
//                     <span className="status-badge inactive">🔴 Inactive</span>
//                   )}
//                   <span className="source-count">📊 {source.total_tenders || 0} tenders</span>
//                   {source.last_scraped && (
//                     <span className="source-last-scraped">
//                       🕐 Last: {new Date(source.last_scraped).toLocaleDateString()}
//                     </span>
//                   )}
//                 </li>
//               ))}
//             </ul>
//           )}
//           <p className="info-note">
//             💡 Tenders are automatically deduplicated across all sources.
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default Scrape;




// components/Scrape.jsx - Fixed version

import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import '../styles/Scrape.css';

function Scrape() {
  // ===== ALL STATE DECLARATIONS =====
  const [loading, setLoading] = useState(false);
  const [scrapingAll, setScrapingAll] = useState(false);
  const [checkingExpired, setCheckingExpired] = useState(false);
  const [deletingExpired, setDeletingExpired] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [sources, setSources] = useState([]);
  const [selectedSource, setSelectedSource] = useState('');
  const [sourceResults, setSourceResults] = useState({});
  const [expiredResult, setExpiredResult] = useState(null);

  // Fetch available sources on component mount
  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await apiService.getScraperSources();
      console.log('📡 Sources response:', response);
      if (response.success && response.sources) {
        setSources(response.sources);
        if (response.sources.length > 0) {
          setSelectedSource(response.sources[0].id);
        }
      }
    } catch (error) {
      console.error('Error fetching sources:', error);
      setError('Failed to load scraper sources');
    }
  };

  // Check for expired deadlines
  const handleCheckExpiredDeadlines = async () => {
    if (!window.confirm('This will check all tenders and show those with passed deadlines. Continue?')) {
      return;
    }

    try {
      setCheckingExpired(true);
      setError('');
      setExpiredResult(null);

      const data = await apiService.checkExpiredDeadlines();
      
      if (data.success) {
        setExpiredResult(data.data);
        setResult({
          success: true,
          message: data.message,
          data: data.data
        });
        
        // Show notification
        if (data.data.expired_count > 0) {
          alert(`📋 Found ${data.data.expired_count} expired tenders. Click "Delete Expired" to remove them.`);
        } else {
          alert('✅ No expired tenders found. All deadlines are in the future.');
        }
      } else {
        setError(data.error || 'Failed to check expired deadlines');
      }
      
    } catch (err) {
      setError(err.message || 'Failed to check expired deadlines');
      console.error(err);
    } finally {
      setCheckingExpired(false);
    }
  };

  // Delete expired tenders
  const handleDeleteExpired = async () => {
    // First check if there are expired tenders
    if (!expiredResult || expiredResult.expired_count === 0) {
      alert('ℹ️ No expired tenders found. Run "Check Expired Deadlines" first.');
      return;
    }

    if (!window.confirm(`⚠️ This will DELETE ${expiredResult.expired_count} expired tenders permanently. This action cannot be undone. Continue?`)) {
      return;
    }

    try {
      setDeletingExpired(true);
      setError('');

      const data = await apiService.deleteExpiredTenders();
      
      if (data.success) {
        setResult({
          success: true,
          message: data.message,
          data: data.data
        });
        
        // Clear expired result since they're deleted
        setExpiredResult(null);
        
        alert(`✅ Successfully deleted ${data.data.deleted_count} expired tenders.`);
      } else {
        setError(data.error || 'Failed to delete expired tenders');
      }
      
    } catch (err) {
      setError(err.message || 'Failed to delete expired tenders');
      console.error(err);
    } finally {
      setDeletingExpired(false);
    }
  };

  // Scrape a single source
  const handleScrapeSource = async () => {
    if (!selectedSource) {
      setError('Please select a source to scrape');
      return;
    }

    const source = sources.find(s => s.id === selectedSource);
    if (!source) {
      setError('Source not found');
      return;
    }

    if (!window.confirm(`This will scrape new tenders from ${source.display_name}. Continue?`)) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      setResult(null);

      const data = await apiService.scrapeSource(selectedSource);
      
      if (data.success) {
        setResult(data);
        setSourceResults(prev => ({
          ...prev,
          [selectedSource]: data
        }));
      } else {
        setError(data.error || 'Failed to scrape source');
      }
      
    } catch (err) {
      setError(err.message || 'Failed to scrape source');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Scrape a single source AND index
  const handleScrapeAndIndexSource = async () => {
    if (!selectedSource) {
      setError('Please select a source to scrape');
      return;
    }

    const source = sources.find(s => s.id === selectedSource);
    if (!source) {
      setError('Source not found');
      return;
    }

    if (!window.confirm(`This will scrape and index new tenders from ${source.display_name}. Continue?`)) {
      return;
    }

    try {
      setLoading(true);
      setError('');
      setResult(null);

      const data = await apiService.scrapeAndIndexSource(selectedSource);
      
      if (data.success) {
        setResult(data);
        setSourceResults(prev => ({
          ...prev,
          [selectedSource]: data
        }));
      } else {
        setError(data.error || 'Failed to scrape and index source');
      }
      
    } catch (err) {
      setError(err.message || 'Failed to scrape and index source');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Scrape ALL sources AND index
  const handleScrapeAllAndIndex = async () => {
    if (sources.length === 0) {
      setError('No sources available to scrape');
      return;
    }

    if (!window.confirm(`This will scrape and index new tenders from ALL ${sources.length} sources. Continue?`)) {
      return;
    }

    try {
      setScrapingAll(true);
      setError('');
      setResult(null);
      setSourceResults({});

      const data = await apiService.scrapeAllAndIndex();
      
      if (data.success) {
        setResult(data);
        if (data.data && data.data.sources) {
          const updatedResults = {};
          Object.entries(data.data.sources).forEach(([id, result]) => {
            updatedResults[id] = result;
          });
          setSourceResults(updatedResults);
        }
      } else {
        setError(data.error || 'Failed to scrape and index all sources');
      }
      
    } catch (err) {
      setError(err.message || 'Failed to scrape and index all sources');
      console.error(err);
    } finally {
      setScrapingAll(false);
    }
  };

  const getSourceName = (sourceId) => {
    const source = sources.find(s => s.id === sourceId);
    return source ? source.display_name : 'Unknown';
  };

  const getSourceStatus = (sourceId) => {
    const source = sources.find(s => s.id === sourceId);
    return source ? source.is_active : false;
  };

  return (
    <div className="scrape-container">
      <div className="scrape-header">
        <h2>🔄 Multi-Source Scraper</h2>
        <p>Fetch new government tenders from multiple sources</p>
      </div>

      <div className="scrape-card">
        <div className="scrape-icon">🔌</div>
        <h3>Scrape Tenders from All Sources</h3>
        <p>
          Select a source below to scrape individually, or click "Scrape All Sources" 
          to fetch tenders from all configured sources at once.
        </p>

        {error && <div className="error-banner">{error}</div>}

        {/* Source Selection */}
        {sources.length > 0 && (
          <div className="source-selection">
            <label htmlFor="source-select">Select Source:</label>
            <select
              id="source-select"
              value={selectedSource}
              onChange={(e) => setSelectedSource(Number(e.target.value))}
              disabled={loading || scrapingAll || checkingExpired || deletingExpired}
            >
              {sources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.display_name || source.name} 
                  {source.is_active ? ' 🟢' : ' 🔴'} 
                  ({source.total_tenders || 0} tenders)
                </option>
              ))}
            </select>
          </div>
        )}

        <div className="scrape-actions">
          <button
            className="scrape-button"
            onClick={handleScrapeAndIndexSource}
            disabled={loading || scrapingAll || checkingExpired || deletingExpired || !selectedSource || sources.length === 0}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Scraping & Indexing...
              </>
            ) : (
              '🔄 Scrape & Index Selected'
            )}
          </button>

          <button
            className="scrape-button scrape-all"
            onClick={handleScrapeAllAndIndex}
            disabled={loading || scrapingAll || checkingExpired || deletingExpired || sources.length === 0}
          >
            {scrapingAll ? (
              <>
                <span className="spinner"></span>
                Scraping & Indexing all...
              </>
            ) : (
              '⚡ Scrape & Index All Sources'
            )}
          </button>

          {/* Check Expired Deadlines Button */}
          <button
            className="scrape-button check-expired"
            onClick={handleCheckExpiredDeadlines}
            disabled={loading || scrapingAll || checkingExpired || deletingExpired}
          >
            {checkingExpired ? (
              <>
                <span className="spinner"></span>
                Checking...
              </>
            ) : (
              '🔍 Check Expired'
            )}
          </button>

          {/* Delete Expired Button */}
          <button
            className="scrape-button delete-expired"
            onClick={handleDeleteExpired}
            disabled={loading || scrapingAll || checkingExpired || deletingExpired || !expiredResult || expiredResult.expired_count === 0}
          >
            {deletingExpired ? (
              <>
                <span className="spinner"></span>
                Deleting...
              </>
            ) : (
              `🗑️ Delete Expired${expiredResult ? ` (${expiredResult.expired_count})` : ''}`
            )}
          </button>
        </div>

        {/* Results */}
        {result && (
          <div className="success-banner">
            <h4>✅ Operation Completed Successfully!</h4>
            
            {/* Check Expired Results */}
            {result.data && result.data.expired_count !== undefined && (
              <div className="result-section">
                <h5>⏰ Expired Deadlines Check</h5>
                <div className="result-details">
                  <div className="result-item">
                    <span className="label">Total Checked:</span>
                    <span className="value">{result.data.total_checked || 0}</span>
                  </div>
                  <div className="result-item">
                    <span className="label">Expired Found:</span>
                    <span className="value" style={{ color: result.data.expired_count > 0 ? '#dc3545' : '#28a745' }}>
                      {result.data.expired_count || 0}
                    </span>
                  </div>
                </div>
                
                {result.data.expired_tenders && result.data.expired_tenders.length > 0 && (
                  <div className="expired-tenders-list">
                    <h6>📋 Expired Tenders:</h6>
                    <ul>
                      {result.data.expired_tenders.map(tender => (
                        <li key={tender.id}>
                          <span className="expired-ref">{tender.reference}</span>
                          <span className="expired-title">{tender.title}</span>
                          <span className="expired-deadline">⏰ {tender.deadline}</span>
                        </li>
                      ))}
                    </ul>
                    {result.data.expired_count > 20 && (
                      <p className="more-hint">... and {result.data.expired_count - 20} more expired tenders</p>
                    )}
                  </div>
                )}
              </div>
            )}

            {result.data && result.data.deleted_count !== undefined && (
  <div className="result-section">
    <h5>🗑️ Deleted Expired Tenders</h5>
    <div className="result-details">
      <div className="result-item">
        <span className="label">Total Deleted from Database:</span>
        <span className="value" style={{ color: result.data.deleted_count > 0 ? '#28a745' : '#6c757d' }}>
          {result.data.deleted_count || 0}
        </span>
      </div>
      
      {/* Show OpenRAG deletion results */}
      {result.data.openrag_deletion && (
        <>
          <div className="result-item">
            <span className="label">Deleted from Vector DB (OpenRAG):</span>
            <span className="value" style={{ color: result.data.openrag_deletion.successful > 0 ? '#28a745' : '#6c757d' }}>
              {result.data.openrag_deletion.successful || 0}
            </span>
          </div>
          {result.data.openrag_deletion.failed > 0 && (
            <div className="result-item">
              <span className="label">Failed to delete from Vector DB:</span>
              <span className="value" style={{ color: '#dc3545' }}>
                {result.data.openrag_deletion.failed}
              </span>
            </div>
          )}
        </>
      )}
    </div>
    
    {result.data.deleted_tenders && result.data.deleted_tenders.length > 0 && (
      <div className="deleted-tenders-list">
        <h6>📋 Deleted Tenders:</h6>
        <ul>
          {result.data.deleted_tenders.map(tender => (
            <li key={tender.id}>
              <span className="deleted-ref">{tender.reference}</span>
              <span className="deleted-title">{tender.title}</span>
              <span className="deleted-deadline">⏰ {tender.deadline}</span>
            </li>
          ))}
        </ul>
        {result.data.deleted_count > 20 && (
          <p className="more-hint">... and {result.data.deleted_count - 20} more deleted tenders</p>
        )}
      </div>
    )}
  </div>
)}

            {/* Overall Results */}
            {result.data && result.data.total_new !== undefined && (
              <div className="result-section">
                <h5>📊 Overall Results</h5>
                <div className="result-details">
                  <div className="result-item">
                    <span className="label">Total New Tenders:</span>
                    <span className="value">{result.data.total_new || 0}</span>
                  </div>
                  <div className="result-item">
                    <span className="label">Successful Sources:</span>
                    <span className="value success">{result.data.successful_sources || 0}</span>
                  </div>
                  <div className="result-item">
                    <span className="label">Failed Sources:</span>
                    <span className="value failed">{result.data.failed_sources || 0}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Per-Source Results */}
            {Object.keys(sourceResults).length > 0 && (
              <div className="result-section">
                <h5>📊 Per-Source Results</h5>
                {Object.entries(sourceResults).map(([sourceId, sourceResult]) => {
                  const isActive = getSourceStatus(Number(sourceId));
                  return (
                    <div key={sourceId} className="source-result">
                      <div className="source-result-header">
                        <strong>
                          {getSourceName(Number(sourceId))}
                          {isActive ? ' 🟢' : ' 🔴'}
                        </strong>
                        {sourceResult.success ? (
                          <span className="source-status success">✅ Success</span>
                        ) : sourceResult.error ? (
                          <span className="source-status error">❌ Failed</span>
                        ) : (
                          <span className="source-status">⏳ Pending</span>
                        )}
                      </div>
                      {sourceResult.success && sourceResult.data && (
                        <div className="source-result-details">
                          <span>New: <strong>{sourceResult.data.new || 0}</strong></span>
                          <span>Duplicates: <strong>{sourceResult.data.duplicates || 0}</strong></span>
                          <span>Total: <strong>{sourceResult.data.total || 0}</strong></span>
                        </div>
                      )}
                      {sourceResult.error && (
                        <div className="source-error">❌ {sourceResult.error}</div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}

            {/* Single Source Results (backward compatibility) */}
            {result.data && result.data.total_new === undefined && result.data.new !== undefined && (
              <div className="result-section">
                <h5>📊 Scrape Results</h5>
                <div className="result-details">
                  <div className="result-item">
                    <span className="label">New Tenders:</span>
                    <span className="value">{result.data.new || 0}</span>
                  </div>
                  <div className="result-item">
                    <span className="label">Duplicates:</span>
                    <span className="value">{result.data.duplicates || 0}</span>
                  </div>
                  <div className="result-item">
                    <span className="label">Total in DB:</span>
                    <span className="value">{result.data.total || 0}</span>
                  </div>
                </div>
                {result.data.new_tender_ids && result.data.new_tender_ids.length > 0 && (
                  <div className="result-item">
                    <span className="label">New Tender IDs:</span>
                    <span className="value">{result.data.new_tender_ids.join(', ')}</span>
                  </div>
                )}
              </div>
            )}

            <p className="result-message">{result.message || 'Operation completed successfully!'}</p>
          </div>
        )}

        {/* Available Sources Info */}
        <div className="scrape-info">
          <h4>ℹ️ Available Sources</h4>
          {sources.length === 0 ? (
            <p className="no-sources">No sources configured. Please add a scraper source first.</p>
          ) : (
            <ul>
              {sources.map((source) => (
                <li key={source.id}>
                  <strong>{source.display_name || source.name}</strong>
                  {source.is_active ? (
                    <span className="status-badge active">🟢 Active</span>
                  ) : (
                    <span className="status-badge inactive">🔴 Inactive</span>
                  )}
                  <span className="source-count">📊 {source.total_tenders || 0} tenders</span>
                  {source.last_scraped && (
                    <span className="source-last-scraped">
                      🕐 Last: {new Date(source.last_scraped).toLocaleDateString()}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          )}
          <p className="info-note">
            💡 Tenders are automatically deduplicated across all sources.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Scrape;
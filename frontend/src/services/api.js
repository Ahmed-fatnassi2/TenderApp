// // const API_BASE_URL = 'http://localhost:5000/api';

// // export const apiService = {
// //   // Health check
// //   async healthCheck() {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/health`);
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Health check failed:', error);
// //       throw error;
// //     }
// //   },

// //   // Get all tenders with optional pagination
// //   async getTenders(page = 1, per_page = 100) {
// //     try {
// //       const params = new URLSearchParams({
// //         page: page,
// //         per_page: per_page
// //       });
// //       const response = await fetch(`${API_BASE_URL}/tenders?${params}`);
// //       if (!response.ok) throw new Error('Failed to fetch tenders');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error fetching tenders:', error);
// //       throw error;
// //     }
// //   },

// //   // Get tender by reference
// //   async getTenderByReference(reference) {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/tenders/${reference}`);
// //       if (!response.ok) throw new Error('Failed to fetch tender');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error fetching tender:', error);
// //       throw error;
// //     }
// //   },

// //   // Trigger scrape
// //   async scrapeTenders() {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/tenders/scrape`, {
// //         method: 'POST',
// //       });
// //       if (!response.ok) throw new Error('Failed to scrape tenders');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error scraping tenders:', error);
// //       throw error;
// //     }
// //   },

// //   // Get tender count
// //   async getTenderCount() {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/tenders/count`);
// //       if (!response.ok) throw new Error('Failed to get tender count');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error fetching tender count:', error);
// //       throw error;
// //     }
// //   },

// //   // Delete tender
// //   async deleteTender(tenderId) {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/tenders/${tenderId}`, {
// //         method: 'DELETE',
// //       });
// //       if (!response.ok) throw new Error('Failed to delete tender');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error deleting tender:', error);
// //       throw error;
// //     }
// //   },

// //   // RAG Methods
// //   async getRagHealth() {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/rag/health`);
// //       return await response.json();
// //     } catch (error) {
// //       console.error('RAG health check failed:', error);
// //       return { rag_healthy: false };
// //     }
// //   },

// //   async initializeRag() {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/rag/initialize`, {
// //         method: 'POST',
// //       });
// //       return await response.json();
// //     } catch (error) {
// //       console.error('RAG initialization failed:', error);
// //       throw error;
// //     }
// //   },

// //   async semanticSearch(query, topK = 10) {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/rag/search/semantic`, {
// //         method: 'POST',
// //         headers: { 'Content-Type': 'application/json' },
// //         body: JSON.stringify({ query, top_k: topK }),
// //       });
// //       if (!response.ok) throw new Error('Semantic search failed');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error in semantic search:', error);
// //       throw error;
// //     }
// //   },

// //   async chatWithRag(message, history = []) {
// //     try {
// //       const response = await fetch(`${API_BASE_URL}/rag/chat`, {
// //         method: 'POST',
// //         headers: { 'Content-Type': 'application/json' },
// //         body: JSON.stringify({ message, history }),
// //       });
// //       if (!response.ok) throw new Error('RAG chat failed');
// //       return await response.json();
// //     } catch (error) {
// //       console.error('Error in RAG chat:', error);
// //       throw error;
// //     }
// //   },
// // };
// // services/api.js

// // services/api.js

// // services/api.js

// const API_BASE_URL = 'http://localhost:5000/api';

// export const apiService = {
//   async request(endpoint, options = {}) {
//     const response = await fetch(`${API_BASE_URL}${endpoint}`, {
//       ...options,
//       credentials: 'include',
//       headers: {
//         'Content-Type': 'application/json',
//         ...options.headers,
//       },
//     });

//     if (!response.ok) {
//       const errorData = await response.json().catch(() => ({}));
//       throw new Error(errorData.error || 'Request failed');
//     }

//     return response.json();
//   },

//   async register(userData) {
//     return this.request('/auth/register', {
//       method: 'POST',
//       body: JSON.stringify(userData),
//     });
//   },

//   async login(credentials) {
//     return this.request('/auth/login', {
//       method: 'POST',
//       body: JSON.stringify(credentials),
//     });
//   },

//   async logout() {
//     return this.request('/auth/logout', {
//       method: 'POST',
//     });
//   },

//   async getCurrentUser() {
//     return this.request('/auth/current-user');
//   },
//   // Health check
//   async healthCheck() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/health`);
//       return await response.json();
//     } catch (error) {
//       console.error('Health check failed:', error);
//       throw error;
//     }
//   },

//   // Get all tenders with optional pagination
//   async getTenders(page = 1, per_page = 100) {
//     try {
//       const params = new URLSearchParams({
//         page: page,
//         per_page: per_page
//       });
//       const response = await fetch(`${API_BASE_URL}/tenders?${params}`);
//       if (!response.ok) throw new Error('Failed to fetch tenders');
//       return await response.json();
//     } catch (error) {
//       console.error('Error fetching tenders:', error);
//       throw error;
//     }
//   },

//   // Get tender by reference
//   async getTenderByReference(reference) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/tenders/${reference}`);
//       if (!response.ok) throw new Error('Failed to fetch tender');
//       return await response.json();
//     } catch (error) {
//       console.error('Error fetching tender:', error);
//       throw error;
//     }
//   },

//   // Trigger scrape
//   async scrapeTenders() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/tenders/scrape`, {
//         method: 'POST',
//       });
//       if (!response.ok) throw new Error('Failed to scrape tenders');
//       return await response.json();
//     } catch (error) {
//       console.error('Error scraping tenders:', error);
//       throw error;
//     }
//   },

//   // Get tender count
//   async getTenderCount() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/tenders/count`);
//       if (!response.ok) throw new Error('Failed to get tender count');
//       return await response.json();
//     } catch (error) {
//       console.error('Error fetching tender count:', error);
//       throw error;
//     }
//   },

//   // Delete tender
//   async deleteTender(tenderId) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/tenders/${tenderId}`, {
//         method: 'DELETE',
//       });
//       if (!response.ok) throw new Error('Failed to delete tender');
//       return await response.json();
//     } catch (error) {
//       console.error('Error deleting tender:', error);
//       throw error;
//     }
//   },

//   // OpenRAG Methods
//   async getOpenRagHealth() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/openrag/health`);
//       return await response.json();
//     } catch (error) {
//       console.error('OpenRAG health check failed:', error);
//       return { success: false, healthy: false };
//     }
//   },

//   // Semantic search using OpenRAG - MATCHING YOUR WSL TEST EXACTLY
//   async semanticSearch(query, topK = 5, threshold = 0.75) {
//     try {
//       console.log(`[semanticSearch] Calling API with query: "${query}", top_k: ${topK}`);
      
//       const response = await fetch(`${API_BASE_URL}/openrag/search`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ 
//           query, 
//           top_k: topK,  // Changed default to 5 to match your WSL test
//           similarity_threshold: threshold,
//           partition: 'tenders'
//         }),
//       });
      
//       if (!response.ok) {
//         console.error(`[semanticSearch] HTTP error: ${response.status}`);
//         throw new Error(`Semantic search failed: ${response.status}`);
//       }
      
//       const result = await response.json();
//       console.log('[semanticSearch] Raw OpenRAG response:', JSON.stringify(result, null, 2));
      
//       // Check if we have documents
//       if (result.documents && Array.isArray(result.documents)) {
//         console.log(`[semanticSearch] Found ${result.documents.length} documents`);
        
//         // Transform documents to match tender format
//         const tenders = result.documents.map((doc, index) => {
//           const metadata = doc.metadata || {};
          
//           // Extract all data from metadata or content
//           let title = metadata.title || 'Untitled';
//           if (title === 'Untitled' && doc.content) {
//             const titleMatch = doc.content.match(/Title:\s*([^\n]+)/);
//             if (titleMatch) {
//               title = titleMatch[1].trim();
//             }
//           }
          
//           let reference = metadata.reference || 'N/A';
//           if (reference === 'N/A' && doc.content) {
//             const refMatch = doc.content.match(/Reference:\s*([^\n]+)/);
//             if (refMatch) {
//               reference = refMatch[1].trim();
//             }
//           }
          
//           let buyer = metadata.buyer || 'N/A';
//           if (buyer === 'N/A' && doc.content) {
//             const buyerMatch = doc.content.match(/Buyer:\s*([^\n]+)/);
//             if (buyerMatch) {
//               buyer = buyerMatch[1].trim();
//             }
//           }
          
//           let publicationDate = metadata.publication_date || 'N/A';
//           if (publicationDate === 'N/A' && doc.content) {
//             const dateMatch = doc.content.match(/Publication Date:\s*([^\n]+)/);
//             if (dateMatch) {
//               publicationDate = dateMatch[1].trim();
//             }
//           }
          
//           let deadline = metadata.deadline || 'N/A';
//           if (deadline === 'N/A' && doc.content) {
//             const deadlineMatch = doc.content.match(/Deadline:\s*([^\n]+)/);
//             if (deadlineMatch) {
//               deadline = deadlineMatch[1].trim();
//             }
//           }
          
//           let source = metadata.source || 'OpenRAG';
//           if (source === 'OpenRAG' && doc.content) {
//             const sourceMatch = doc.content.match(/Source:\s*([^\n]+)/);
//             if (sourceMatch) {
//               source = sourceMatch[1].trim();
//             }
//           }
          
//           // Format dates for display
//           const formatDate = (dateStr) => {
//             if (!dateStr || dateStr === 'N/A') return 'N/A';
//             try {
//               const date = new Date(dateStr);
//               if (isNaN(date.getTime())) return dateStr;
//               return date.toLocaleDateString('fr-FR', {
//                 year: 'numeric',
//                 month: 'short',
//                 day: 'numeric'
//               });
//             } catch (e) {
//               return dateStr;
//             }
//           };
          
//           const tender = {
//             id: metadata.tender_id || metadata._id || `result-${index}`,
//             reference: reference,
//             title: title,
//             buyer: buyer,
//             publication_date: publicationDate,
//             publication_date_display: formatDate(publicationDate),
//             deadline: deadline,
//             deadline_display: formatDate(deadline),
//             source: source,
//             scraped_at: metadata.indexed_at || null,
//             similarity_score: metadata.similarity || 0.75,
//             content: doc.content || '',
//             context: metadata.context || '',
//             _original: doc,
//             _metadata: metadata,
//             // Add a flag to identify this as a smart search result
//             _isSmartResult: true
//           };
          
//           console.log(`[semanticSearch] Processed tender ${index + 1}:`, tender);
//           return tender;
//         });
        
//         console.log(`[semanticSearch] Returning ${tenders.length} processed tenders`);
//         return tenders;
//       }
      
//       console.warn('[semanticSearch] No documents found in response');
//       return [];
      
//     } catch (error) {
//       console.error('[semanticSearch] Error:', error);
//       throw error;
//     }
//   },

//   // Index a single tender
//   async indexTender(tenderId) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/openrag/index-tender`, {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ tender_id: tenderId }),
//       });
//       if (!response.ok) throw new Error('Failed to index tender');
//       return await response.json();
//     } catch (error) {
//       console.error('Error indexing tender:', error);
//       throw error;
//     }
//   },

//   // Index all tenders
//   async indexAllTenders() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/openrag/index-all`, {
//         method: 'POST',
//       });
//       if (!response.ok) throw new Error('Failed to index all tenders');
//       return await response.json();
//     } catch (error) {
//       console.error('Error indexing all tenders:', error);
//       throw error;
//     }
//   },

//   // Check batch status
//   async getBatchStatus(taskId) {
//     try {
//       const response = await fetch(`${API_BASE_URL}/openrag/batch-status/${taskId}`);
//       if (!response.ok) throw new Error('Failed to get batch status');
//       return await response.json();
//     } catch (error) {
//       console.error('Error getting batch status:', error);
//       throw error;
//     }
//   },



  

//   // Scrape and index in one call (new combined endpoint)
//   async scrapeAndIndexTenders() {
//     try {
//       const response = await fetch(`${API_BASE_URL}/openrag/scrape-and-index`, {
//         method: 'POST',
//       });
//       if (!response.ok) throw new Error('Failed to scrape and index tenders');
//       return await response.json();
//     } catch (error) {
//       console.error('Error scraping and indexing tenders:', error);
//       throw error;
//     }
//   },
// };



// services/api.js
const API_BASE_URL = 'http://localhost:5000/api';

export const apiService = {
  // async request(endpoint, options = {}) {
  //   try {
  //     console.log(`📡 Making request to: ${API_BASE_URL}${endpoint}`);
      
  //     // For auth endpoints, use 'omit' credentials to avoid preflight issues
  //     const isAuthEndpoint = endpoint.includes('/auth/');
      
  //     const response = await fetch(`${API_BASE_URL}${endpoint}`, {
  //       ...options,
  //       credentials: isAuthEndpoint ? 'omit' : 'include',
  //       headers: {
  //         'Content-Type': 'application/json',
  //         ...options.headers,
  //       },
  //     });

  //     console.log(`✅ Response status: ${response.status}`);

  //     // Try to parse JSON response
  //     let data;
  //     const contentType = response.headers.get('content-type');
  //     if (contentType && contentType.includes('application/json')) {
  //       data = await response.json();
  //     } else {
  //       const text = await response.text();
  //       throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
  //     }

  //     if (!response.ok) {
  //       throw new Error(data.error || `Request failed with status ${response.status}`);
  //     }

  //     return data;
  //   } catch (error) {
  //     console.error('❌ API Request failed:', error);
      
  //     if (error.message === 'Failed to fetch') {
  //       throw new Error('Cannot connect to server. Please make sure the backend is running on port 5000.');
  //     }
      
  //     throw error;
  //   }
  // },
  // services/api.js - Update the request method
async request(endpoint, options = {}) {
  try {
    console.log(`📡 Making request to: ${API_BASE_URL}${endpoint}`);
    
    // ✅ Get user from localStorage
    const userData = localStorage.getItem('user');
    let userId = null;
    if (userData) {
      try {
        const user = JSON.parse(userData);
        userId = user.id;
        console.log(`👤 User ID from localStorage: ${userId}`);
      } catch (e) {
        console.warn('Could not parse user data:', e);
      }
    }
    
    // ✅ Build headers with X-User-ID
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    
    // ✅ Add X-User-ID header if user is logged in
    if (userId) {
      headers['X-User-ID'] = String(userId);
      console.log(`🔑 Added X-User-ID header: ${userId}`);
    }
    
    // ✅ For auth endpoints, don't send the header (they use credentials)
    const isAuthEndpoint = endpoint.includes('/auth/');
    const isOIDCEndpoint = endpoint.includes('/oidc/');
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      credentials: (isAuthEndpoint || isOIDCEndpoint) ? 'include' : 'omit',
      headers: headers,
    });

    console.log(`✅ Response status: ${response.status}`);

    // Handle 401 Unauthorized
    if (response.status === 401) {
      // Don't clear user data for auth endpoints
      if (!isAuthEndpoint && !isOIDCEndpoint) {
        // Clear invalid user data
        localStorage.removeItem('user');
        throw new Error('Not authenticated');
      }
      throw new Error('Authentication failed');
    }

    // Try to parse JSON response
    let data;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      const text = await response.text();
      throw new Error(`Server returned non-JSON response: ${text.substring(0, 100)}`);
    }

    if (!response.ok) {
      throw new Error(data.error || `Request failed with status ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error('❌ API Request failed:', error);
    
    if (error.message === 'Failed to fetch') {
      throw new Error('Cannot connect to server. Please make sure the backend is running on port 5000.');
    }
    
    throw error;
  }
},




  async register(userData) {
    console.log('📝 Registering user:', { username: userData.username, email: userData.email });
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async login(credentials) {
    console.log('🔑 Logging in:', { email: credentials.email });
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  async logout() {
  // Call the regular logout endpoint
  const response = await this.request('/auth/logout', {
    method: 'POST'
  });
  
  // Also call OIDC logout if needed (optional, this will clear OIDC session)
  try {
    await fetch(`http://localhost:5000/auth/oidc/logout`, {
      credentials: 'include'
    });
  } catch (e) {
    // Ignore - OIDC session might not exist
  }
  
  return response;
},

  async getCurrentUser() {
    return this.request('/auth/current-user', {
      credentials: 'include',
    });
  },

  // Health check
  async healthCheck() {
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        credentials: 'omit',
      });
      if (!response.ok) throw new Error('Health check failed');
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  },

  // Tender methods
  async getTenders(page = 1, per_page = 100) {
    try {
      const params = new URLSearchParams({
        page: page,
        per_page: per_page
      });
      const response = await fetch(`${API_BASE_URL}/tenders?${params}`);
      if (!response.ok) throw new Error('Failed to fetch tenders');
      return await response.json();
    } catch (error) {
      console.error('Error fetching tenders:', error);
      throw error;
    }
  },

  async getTenderByReference(reference) {
    try {
      const response = await fetch(`${API_BASE_URL}/tenders/${reference}`);
      if (!response.ok) throw new Error('Failed to fetch tender');
      return await response.json();
    } catch (error) {
      console.error('Error fetching tender:', error);
      throw error;
    }
  },

  async scrapeTenders() {
    try {
      const response = await fetch(`${API_BASE_URL}/tenders/scrape`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to scrape tenders');
      return await response.json();
    } catch (error) {
      console.error('Error scraping tenders:', error);
      throw error;
    }
  },

  async getTenderCount() {
    try {
      const response = await fetch(`${API_BASE_URL}/tenders/count`);
      if (!response.ok) throw new Error('Failed to get tender count');
      return await response.json();
    } catch (error) {
      console.error('Error fetching tender count:', error);
      throw error;
    }
  },

  async deleteTender(tenderId) {
    try {
      const response = await fetch(`${API_BASE_URL}/tenders/${tenderId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete tender');
      return await response.json();
    } catch (error) {
      console.error('Error deleting tender:', error);
      throw error;
    }
  },

  // OpenRAG Methods
  async getOpenRagHealth() {
    try {
      const response = await fetch(`${API_BASE_URL}/openrag/health`);
      return await response.json();
    } catch (error) {
      console.error('OpenRAG health check failed:', error);
      return { success: false, healthy: false };
    }
  },

  async semanticSearch(query, topK = 5, threshold = 0.75) {
    try {
      console.log(`[semanticSearch] Calling API with query: "${query}", top_k: ${topK}`);
      
      const response = await fetch(`${API_BASE_URL}/openrag/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          query, 
          top_k: topK,
          similarity_threshold: threshold,
          partition: 'tenders'
        }),
      });
      
      if (!response.ok) {
        console.error(`[semanticSearch] HTTP error: ${response.status}`);
        throw new Error(`Semantic search failed: ${response.status}`);
      }
      
      const result = await response.json();
      console.log('[semanticSearch] Raw OpenRAG response:', JSON.stringify(result, null, 2));
      
      if (result.documents && Array.isArray(result.documents)) {
        console.log(`[semanticSearch] Found ${result.documents.length} documents`);
        return result.documents;
      }
      
      console.warn('[semanticSearch] No documents found in response');
      return [];
      
    } catch (error) {
      console.error('[semanticSearch] Error:', error);
      throw error;
    }
  },

  // Scrape and index in one call (new combined endpoint)
  async scrapeAndIndexTenders() {
    try {
      const response = await fetch(`${API_BASE_URL}/openrag/scrape-and-index`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to scrape and index tenders');
      return await response.json();
    } catch (error) {
      console.error('Error scraping and indexing tenders:', error);
      throw error;
    }
  },



async getScraperSources() {
  return this.request('/scrapers/sources');
},

async createScraperSource(data) {
  return this.request('/scrapers/sources', {
    method: 'POST',
    body: JSON.stringify(data)
  });
},

async testScraperSource(data) {
  return this.request('/scrapers/test', {
    method: 'POST',
    body: JSON.stringify(data)
  });
},

async scrapeSource(sourceId) {
  return this.request(`/scrapers/sources/${sourceId}/scrape`, {
    method: 'POST'
  });
},

async deleteSource(sourceId) {
  return this.request(`/scrapers/sources/${sourceId}`, {
    method: 'DELETE'
  });
},




async scrapeAndIndexSource(sourceId) {
  return this.request(`/scrapers/sources/${sourceId}/scrape-and-index`, {
    method: 'POST'
  });
},

// Scrape all sources and index new tenders
async scrapeAllAndIndex() {
  return this.request('/scrapers/scrape-all-and-index', {
    method: 'POST'
  });
},

// Index all tenders (existing method)
async indexAllTenders() {
  try {
    const response = await fetch(`${API_BASE_URL}/openrag/index-all`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to index all tenders');
    return await response.json();
  } catch (error) {
    console.error('Error indexing all tenders:', error);
    throw error;
  }
},




// async checkAdmin() {
//     try {
//       const userData = localStorage.getItem('user');
//       if (!userData) {
//         return this.request('/admin/check');
//       }
//       const user = JSON.parse(userData);
//       // Use 'id' from localStorage (not 'user_id')
//       return this.request(`/admin/check?user_id=${user.id}`);
//     } catch (error) {
//       console.error('Error in checkAdmin:', error);
//       return this.request('/admin/check');
//     }
//   },

  async checkAdmin() {
  try {
    const userData = localStorage.getItem('user');
    if (!userData) {
      return this.request('/admin/check');
    }
    const user = JSON.parse(userData);
    // ✅ Use the request method which will add X-User-ID header
    return this.request(`/admin/check?user_id=${user.id}`);
  } catch (error) {
    console.error('Error in checkAdmin:', error);
    return this.request('/admin/check');
  }
},



  async getAdminUsers() {
    const userData = localStorage.getItem('user');
    if (!userData) {
      console.error('❌ No user data found in localStorage');
      throw new Error('Not authenticated');
    }
    const user = JSON.parse(userData);
    console.log('👤 Admin user ID:', user.id); // Debug
    return this.request(`/admin/users?user_id=${user.id}`);
  },

  async deleteUser(userId) {
    const userData = localStorage.getItem('user');
    const user = userData ? JSON.parse(userData) : null;
    const adminId = user ? user.id : null;
    return this.request(`/admin/users/${userId}?admin_id=${adminId}`, {
      method: 'DELETE'
    });
  },

  async makeAdmin(userId) {
    const userData = localStorage.getItem('user');
    const user = userData ? JSON.parse(userData) : null;
    const adminId = user ? user.id : null;
    return this.request(`/admin/users/${userId}/make-admin?admin_id=${adminId}`, {
      method: 'POST'
    });
  },

  async removeAdmin(userId) {
    const userData = localStorage.getItem('user');
    const user = userData ? JSON.parse(userData) : null;
    const adminId = user ? user.id : null;
    return this.request(`/admin/users/${userId}/remove-admin?admin_id=${adminId}`, {
      method: 'POST'
    });
  },

  async toggleUserActive(userId) {
    const userData = localStorage.getItem('user');
    const user = userData ? JSON.parse(userData) : null;
    const adminId = user ? user.id : null;
    return this.request(`/admin/users/${userId}/toggle-active?admin_id=${adminId}`, {
      method: 'POST'
    });
  },

  async getAdminStats() {
    const userData = localStorage.getItem('user');
    const user = userData ? JSON.parse(userData) : null;
    const adminId = user ? user.id : null;
    return this.request(`/admin/stats?admin_id=${adminId}`);
  },




  // ===== CHECK EXPIRED DEADLINES =====
  async checkExpiredDeadlines() {
    try {
      console.log('🔍 Checking expired deadlines...');
      const response = await fetch(`${API_BASE_URL}/scrapers/check-expired-deadlines`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      });
      
      if (!response.ok) {
        let errorMsg = 'Failed to check expired deadlines';
        try {
          const errorData = await response.json();
          errorMsg = errorData.error || errorMsg;
        } catch (e) {
          // If response is not JSON, use status text
          errorMsg = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }
      
      const data = await response.json();
      console.log('✅ Expired deadlines check complete:', data);
      return data;
    } catch (error) {
      console.error('❌ Error checking expired deadlines:', error);
      throw error;
    }
  },

async deleteExpiredTenders() {
  try {
    console.log('🗑️ Deleting expired tenders...');
    const response = await fetch(`${API_BASE_URL}/scrapers/delete-expired`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include'
    });
    
    if (!response.ok) {
      let errorMsg = 'Failed to delete expired tenders';
      try {
        const errorData = await response.json();
        errorMsg = errorData.error || errorMsg;
      } catch (e) {
        errorMsg = `Server error: ${response.status} ${response.statusText}`;
      }
      throw new Error(errorMsg);
    }
    
    const data = await response.json();
    console.log('✅ Expired tenders deleted:', data);
    return data;
  } catch (error) {
    console.error('❌ Error deleting expired tenders:', error);
    throw error;
  }
},

async testITNotification() {
  return this.request('/it-notifications/send-test', {
    method: 'POST'
  });
},


// Redirect to Google OIDC login
googleLogin() {
  // Use the full URL without /api prefix
  window.location.href = `http://localhost:5000/auth/oidc/login?provider=google`;
},

// Check if user is authenticated via OIDC
async checkOIDCAuth() {
  try {
    // Use full URL without /api
    const response = await fetch(`http://localhost:5000/auth/oidc/status`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      return { authenticated: false };
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error checking OIDC auth:', error);
    return { authenticated: false };
  }
},

// Get current user from OIDC session
async getOIDCUser() {
  try {
    // Use full URL without /api
    const response = await fetch(`http://localhost:5000/auth/oidc/user`, {
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      return null;
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error getting OIDC user:', error);
    return null;
  }
},

// OIDC Logout
oidcLogout() {
  window.location.href = `http://localhost:5000/auth/oidc/logout`;
},

// Check if user is logged in via OIDC or email/password
async checkAuth() {
  // First check OIDC session
  try {
    const oidcStatus = await this.checkOIDCAuth();
    if (oidcStatus && oidcStatus.authenticated) {
      const user = await this.getOIDCUser();
      if (user && user.id) {
        localStorage.setItem('user', JSON.stringify(user));
        return user;
      }
    }
  } catch (error) {
    console.error('Error checking OIDC auth:', error);
  }
  
  // Then check localStorage for email/password auth
  const userData = localStorage.getItem('user');
  if (userData) {
    try {
      return JSON.parse(userData);
    } catch {
      return null;
    }
  }
  
  return null;
},


// Get user preferences
async getPreferences() {
  return this.request('/preferences/', {
    method: 'GET'
  });
},

// Update user preferences
async updatePreferences(data) {
  return this.request('/preferences/', {
    method: 'PUT',
    body: JSON.stringify(data)
  });
},

// Test preferences
async testPreferences() {
  return this.request('/preferences/test', {
    method: 'POST'
  });
},





};




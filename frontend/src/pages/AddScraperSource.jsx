// // components/AddScraperSource.jsx
// import { useState } from 'react';
// import { apiService } from '../services/api';
// import '../styles/AddScraperSource.css';

// function AddScraperSource({ onSuccess, onCancel }) {
//   const [loading, setLoading] = useState(false);
//   const [testing, setTesting] = useState(false);
//   const [testResult, setTestResult] = useState(null);
//   const [error, setError] = useState(null);
  
//   const [formData, setFormData] = useState({
//     name: '',
//     display_name: '',
//     source_type: 'api',
//     base_url: '',
//     headers: {},
//     auth_type: 'none',
//     auth_config: {},
//     parser_config: {
//       data_path: '',
//       item_selector: '',
//       field_mapping: {
//         reference: '',
//         title: '',
//         buyer: '',
//         publication_date: '',
//         deadline: ''
//       }
//     }
//   });

//   const handleChange = (e) => {
//     const { name, value } = e.target;
//     setFormData(prev => ({ ...prev, [name]: value }));
//   };

//   const handleParserChange = (field, value) => {
//     setFormData(prev => ({
//       ...prev,
//       parser_config: {
//         ...prev.parser_config,
//         field_mapping: {
//           ...prev.parser_config.field_mapping,
//           [field]: value
//         }
//       }
//     }));
//   };

//   const handleHeadersChange = (value) => {
//     try {
//       const headers = JSON.parse(value);
//       setFormData(prev => ({ ...prev, headers }));
//     } catch (e) {
//       // Invalid JSON - ignore
//     }
//   };

//   const handleAuthConfigChange = (field, value) => {
//     setFormData(prev => ({
//       ...prev,
//       auth_config: {
//         ...prev.auth_config,
//         [field]: value
//       }
//     }));
//   };

//   const handleTest = async () => {
//     setTesting(true);
//     setTestResult(null);
//     setError(null);
    
//     try {
//       const result = await apiService.request('/scrapers/test', {
//         method: 'POST',
//         body: JSON.stringify(formData)
//       });
//       setTestResult(result);
//     } catch (err) {
//       setError(err.message);
//     } finally {
//       setTesting(false);
//     }
//   };

// const handleSubmit = async () => {
//   setLoading(true);
//   setError(null);
  
//   try {
//     const result = await apiService.request('/scrapers/sources', {
//       method: 'POST',
//       body: JSON.stringify(formData)
//     });
    
//     if (result.success) {
//       // Check if onSuccess exists and is a function
//       if (onSuccess && typeof onSuccess === 'function') {
//         onSuccess(result.config);
//       } else {
//         // Fallback: close the form and refresh
//         console.warn('onSuccess is not a function, using fallback');
//         if (onCancel && typeof onCancel === 'function') {
//           onCancel();
//         }
//         // Refresh the page to show the new source
//         window.location.reload();
//       }
//     } else {
//       setError(result.error);
//     }
//   } catch (err) {
//     setError(err.message);
//   } finally {
//     setLoading(false);
//   }
// };

//   return (
//     <div className="add-scraper-source">
//       <div className="header">
//         <h3>Add New Scraper Source</h3>
//         <button onClick={onCancel} className="close-btn">×</button>
//       </div>

//       <div className="form">
//         {/* Basic Info */}
//         <div className="form-section">
//           <h4>Basic Information</h4>
          
//           <div className="form-group">
//             <label>Source Name (unique identifier)</label>
//             <input
//               type="text"
//               name="name"
//               placeholder="e.g., HAICOP"
//               value={formData.name}
//               onChange={handleChange}
//               required
//             />
//             <small>This will be used as the source identifier</small>
//           </div>

//           <div className="form-group">
//             <label>Display Name</label>
//             <input
//               type="text"
//               name="display_name"
//               placeholder="e.g., HAICOP - High Commission for Public Procurement"
//               value={formData.display_name}
//               onChange={handleChange}
//               required
//             />
//           </div>

//           <div className="form-group">
//             <label>Source Type</label>
//             <select
//               name="source_type"
//               value={formData.source_type}
//               onChange={handleChange}
//             >
//               <option value="api">API (JSON)</option>
//               <option value="html">HTML Page</option>
//             </select>
//           </div>

//           <div className="form-group">
//             <label>Base URL</label>
//             <input
//               type="url"
//               name="base_url"
//               placeholder="https://example.com/api/tenders"
//               value={formData.base_url}
//               onChange={handleChange}
//               required
//             />
//           </div>
//         </div>

//         {/* Authentication */}
//         <div className="form-section">
//           <h4>Authentication</h4>
          
//           <div className="form-group">
//             <label>Auth Type</label>
//             <select
//               name="auth_type"
//               value={formData.auth_type}
//               onChange={handleChange}
//             >
//               <option value="none">None</option>
//               <option value="bearer">Bearer Token</option>
//               <option value="api_key">API Key</option>
//               <option value="basic">Basic Auth</option>
//             </select>
//           </div>

//           {formData.auth_type === 'bearer' && (
//             <div className="form-group">
//               <label>Bearer Token</label>
//               <input
//                 type="text"
//                 placeholder="Enter your bearer token"
//                 onChange={(e) => handleAuthConfigChange('token', e.target.value)}
//               />
//             </div>
//           )}

//           {formData.auth_type === 'api_key' && (
//             <>
//               <div className="form-group">
//                 <label>API Key Name</label>
//                 <input
//                   type="text"
//                   placeholder="X-API-Key"
//                   onChange={(e) => handleAuthConfigChange('key_name', e.target.value)}
//                 />
//               </div>
//               <div className="form-group">
//                 <label>API Key Value</label>
//                 <input
//                   type="text"
//                   placeholder="Your API key"
//                   onChange={(e) => handleAuthConfigChange('api_key', e.target.value)}
//                 />
//               </div>
//             </>
//           )}

//           {formData.auth_type === 'basic' && (
//             <>
//               <div className="form-group">
//                 <label>Username</label>
//                 <input
//                   type="text"
//                   placeholder="Username"
//                   onChange={(e) => handleAuthConfigChange('username', e.target.value)}
//                 />
//               </div>
//               <div className="form-group">
//                 <label>Password</label>
//                 <input
//                   type="password"
//                   placeholder="Password"
//                   onChange={(e) => handleAuthConfigChange('password', e.target.value)}
//                 />
//               </div>
//             </>
//           )}
//         </div>

//         {/* Headers */}
//         <div className="form-section">
//           <h4>Custom Headers (Optional)</h4>
//           <div className="form-group">
//             <label>Headers (JSON)</label>
//             <textarea
//               rows="3"
//               placeholder='{"User-Agent": "Mozilla/5.0"}'
//               onChange={(e) => handleHeadersChange(e.target.value)}
//             />
//           </div>
//         </div>

//         {/* Parser Configuration */}
//         <div className="form-section">
//           <h4>Parser Configuration</h4>
//           <p className="help-text">
//             {formData.source_type === 'api' 
//               ? 'Use dot notation for JSON paths (e.g., data.tenders)' 
//               : 'Use CSS selectors for HTML (e.g., .tender-row)'}
//           </p>

//           <div className="form-group">
//             <label>
//               {formData.source_type === 'api' ? 'Data Path' : 'Item Selector'}
//             </label>
//             <input
//               type="text"
//               placeholder={formData.source_type === 'api' ? 'data.tenders' : '.tender-row'}
//               onChange={(e) => setFormData(prev => ({
//                 ...prev,
//                 parser_config: {
//                   ...prev.parser_config,
//                   [formData.source_type === 'api' ? 'data_path' : 'item_selector']: e.target.value
//                 }
//               }))}
//             />
//           </div>

//           <div className="field-mapping">
//             <h5>Field Mapping</h5>
//             <div className="form-row">
//               <div className="form-group">
//                 <label>Reference</label>
//                 <input
//                   type="text"
//                   placeholder={formData.source_type === 'api' ? 'reference' : '.ref'}
//                   onChange={(e) => handleParserChange('reference', e.target.value)}
//                 />
//               </div>
//               <div className="form-group">
//                 <label>Title</label>
//                 <input
//                   type="text"
//                   placeholder={formData.source_type === 'api' ? 'title' : '.title'}
//                   onChange={(e) => handleParserChange('title', e.target.value)}
//                 />
//               </div>
//             </div>
//             <div className="form-row">
//               <div className="form-group">
//                 <label>Buyer</label>
//                 <input
//                   type="text"
//                   placeholder={formData.source_type === 'api' ? 'buyer.name' : '.buyer'}
//                   onChange={(e) => handleParserChange('buyer', e.target.value)}
//                 />
//               </div>
//               <div className="form-group">
//                 <label>Deadline</label>
//                 <input
//                   type="text"
//                   placeholder={formData.source_type === 'api' ? 'deadline' : '.deadline'}
//                   onChange={(e) => handleParserChange('deadline', e.target.value)}
//                 />
//               </div>
//             </div>
//             <div className="form-row">
//               <div className="form-group">
//                 <label>Publication Date</label>
//                 <input
//                   type="text"
//                   placeholder={formData.source_type === 'api' ? 'published' : '.date'}
//                   onChange={(e) => handleParserChange('publication_date', e.target.value)}
//                 />
//               </div>
//             </div>
//           </div>
//         </div>

//         {/* Actions */}
//         <div className="actions">
//           <button 
//             className="btn-secondary" 
//             onClick={handleTest} 
//             disabled={testing}
//           >
//             {testing ? 'Testing...' : '🔍 Test Configuration'}
//           </button>
//           <button 
//             className="btn-primary" 
//             onClick={handleSubmit} 
//             disabled={loading}
//           >
//             {loading ? 'Adding...' : '➕ Add Source'}
//           </button>
//         </div>

//         {/* Test Results */}
//         {testResult && (
//           <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
//             <h4>{testResult.success ? '✅ Test Successful' : '❌ Test Failed'}</h4>
//             <p>{testResult.message}</p>
//             {testResult.sample && (
//               <div className="sample">
//                 <h5>Sample Tenders:</h5>
//                 <pre>{JSON.stringify(testResult.sample, null, 2)}</pre>
//               </div>
//             )}
//           </div>
//         )}

//         {error && (
//           <div className="error-message">
//             ❌ {error}
//           </div>
//         )}
//       </div>
//     </div>
//   );
// }

// export default AddScraperSource;




// components/AddScraperSource.jsx
import { useState } from 'react';
import { apiService } from '../services/api';
import '../styles/AddScraperSource.css';

function AddScraperSource({ onSuccess, onCancel }) {
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [error, setError] = useState(null);
  
  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    source_type: 'api',
    base_url: '',
    headers: {},
    auth_type: 'none',
    auth_config: {},
    parser_config: {
      data_path: '',
      item_selector: '',
      field_mapping: {
        reference: '',
        title: '',
        buyer: '',
        publication_date: '',
        deadline: '',
        tender_id: ''  // ← NOUVEAU
      },
      url_template: ''  // ← NOUVEAU
    }
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleParserChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      parser_config: {
        ...prev.parser_config,
        field_mapping: {
          ...prev.parser_config.field_mapping,
          [field]: value
        }
      }
    }));
  };

  const handleParserConfigChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      parser_config: {
        ...prev.parser_config,
        [field]: value
      }
    }));
  };

  const handleHeadersChange = (value) => {
    try {
      const headers = JSON.parse(value);
      setFormData(prev => ({ ...prev, headers }));
    } catch (e) {
      // Invalid JSON - ignore
    }
  };

  const handleAuthConfigChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      auth_config: {
        ...prev.auth_config,
        [field]: value
      }
    }));
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);
    setError(null);
    
    try {
      const result = await apiService.request('/scrapers/test', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      setTestResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiService.request('/scrapers/sources', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      if (result.success) {
        if (onSuccess && typeof onSuccess === 'function') {
          onSuccess(result.config);
        } else {
          console.warn('onSuccess is not a function, using fallback');
          if (onCancel && typeof onCancel === 'function') {
            onCancel();
          }
          window.location.reload();
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="add-scraper-source">
      <div className="header">
        <h3>Add New Scraper Source</h3>
        <button onClick={onCancel} className="close-btn">×</button>
      </div>

      <div className="form">
        {/* Basic Info */}
        <div className="form-section">
          <h4>Basic Information</h4>
          
          <div className="form-group">
            <label>Source Name (unique identifier)</label>
            <input
              type="text"
              name="name"
              placeholder="e.g., HAICOP"
              value={formData.name}
              onChange={handleChange}
              required
            />
            <small>This will be used as the source identifier</small>
          </div>

          <div className="form-group">
            <label>Display Name</label>
            <input
              type="text"
              name="display_name"
              placeholder="e.g., HAICOP - High Commission for Public Procurement"
              value={formData.display_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label>Source Type</label>
            <select
              name="source_type"
              value={formData.source_type}
              onChange={handleChange}
            >
              <option value="api">API (JSON)</option>
              <option value="html">HTML Page</option>
            </select>
          </div>

          <div className="form-group">
            <label>Base URL</label>
            <input
              type="url"
              name="base_url"
              placeholder="https://example.com/api/tenders"
              value={formData.base_url}
              onChange={handleChange}
              required
            />
          </div>
        </div>

        {/* Authentication */}
        <div className="form-section">
          <h4>Authentication</h4>
          
          <div className="form-group">
            <label>Auth Type</label>
            <select
              name="auth_type"
              value={formData.auth_type}
              onChange={handleChange}
            >
              <option value="none">None</option>
              <option value="bearer">Bearer Token</option>
              <option value="api_key">API Key</option>
              <option value="basic">Basic Auth</option>
            </select>
          </div>

          {formData.auth_type === 'bearer' && (
            <div className="form-group">
              <label>Bearer Token</label>
              <input
                type="text"
                placeholder="Enter your bearer token"
                onChange={(e) => handleAuthConfigChange('token', e.target.value)}
              />
            </div>
          )}

          {formData.auth_type === 'api_key' && (
            <>
              <div className="form-group">
                <label>API Key Name</label>
                <input
                  type="text"
                  placeholder="X-API-Key"
                  onChange={(e) => handleAuthConfigChange('key_name', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>API Key Value</label>
                <input
                  type="text"
                  placeholder="Your API key"
                  onChange={(e) => handleAuthConfigChange('api_key', e.target.value)}
                />
              </div>
            </>
          )}

          {formData.auth_type === 'basic' && (
            <>
              <div className="form-group">
                <label>Username</label>
                <input
                  type="text"
                  placeholder="Username"
                  onChange={(e) => handleAuthConfigChange('username', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Password</label>
                <input
                  type="password"
                  placeholder="Password"
                  onChange={(e) => handleAuthConfigChange('password', e.target.value)}
                />
              </div>
            </>
          )}
        </div>

        {/* Headers */}
        <div className="form-section">
          <h4>Custom Headers (Optional)</h4>
          <div className="form-group">
            <label>Headers (JSON)</label>
            <textarea
              rows="3"
              placeholder='{"User-Agent": "Mozilla/5.0"}'
              onChange={(e) => handleHeadersChange(e.target.value)}
            />
          </div>
        </div>

        {/* Parser Configuration */}
        <div className="form-section">
          <h4>Parser Configuration</h4>
          <p className="help-text">
            {formData.source_type === 'api' 
              ? 'Use dot notation for JSON paths (e.g., data.tenders)' 
              : 'Use CSS selectors for HTML (e.g., .tender-row)'}
          </p>

          <div className="form-group">
            <label>
              {formData.source_type === 'api' ? 'Data Path' : 'Item Selector'}
            </label>
            <input
              type="text"
              placeholder={formData.source_type === 'api' ? 'data.tenders' : '.tender-row'}
              onChange={(e) => handleParserConfigChange(
                formData.source_type === 'api' ? 'data_path' : 'item_selector',
                e.target.value
              )}
            />
          </div>

          <div className="field-mapping">
            <h5>Field Mapping</h5>
            <div className="form-row">
              <div className="form-group">
                <label>Reference</label>
                <input
                  type="text"
                  placeholder={formData.source_type === 'api' ? 'reference' : '.ref'}
                  onChange={(e) => handleParserChange('reference', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  placeholder={formData.source_type === 'api' ? 'title' : '.title'}
                  onChange={(e) => handleParserChange('title', e.target.value)}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Buyer</label>
                <input
                  type="text"
                  placeholder={formData.source_type === 'api' ? 'buyer.name' : '.buyer'}
                  onChange={(e) => handleParserChange('buyer', e.target.value)}
                />
              </div>
              <div className="form-group">
                <label>Deadline</label>
                <input
                  type="text"
                  placeholder={formData.source_type === 'api' ? 'deadline' : '.deadline'}
                  onChange={(e) => handleParserChange('deadline', e.target.value)}
                />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Publication Date</label>
                <input
                  type="text"
                  placeholder={formData.source_type === 'api' ? 'published' : '.date'}
                  onChange={(e) => handleParserChange('publication_date', e.target.value)}
                />
              </div>
            </div>
          </div>
        </div>

        {/* 🔗 URL Configuration - NOUVEAU */}
        <div className="form-section">
          <h4>🔗 URL Configuration</h4>
          <div className="form-group">
            <label>Template URL</label>
            <input
              type="text"
              placeholder="https://example.com/tenders/{tender_id}/{reference}"
              value={formData.parser_config.url_template}
              onChange={(e) => handleParserConfigChange('url_template', e.target.value)}
            />
            <small>Use {'{tender_id}'} and {'{reference}'} as variables</small>
          </div>
          <div className="form-group">
            <label>Champ ID Tender</label>
            <input
              type="text"
              placeholder="epBidMasterId"
              value={formData.parser_config.field_mapping.tender_id}
              onChange={(e) => handleParserChange('tender_id', e.target.value)}
            />
            <small>Le nom du champ dans l'API qui contient l'ID unique</small>
          </div>
        </div>

        {/* Actions */}
        <div className="actions">
          <button 
            className="btn-secondary" 
            onClick={handleTest} 
            disabled={testing}
          >
            {testing ? 'Testing...' : '🔍 Test Configuration'}
          </button>
          <button 
            className="btn-primary" 
            onClick={handleSubmit} 
            disabled={loading}
          >
            {loading ? 'Adding...' : '➕ Add Source'}
          </button>
        </div>

        {/* Test Results */}
        {testResult && (
          <div className={`test-result ${testResult.success ? 'success' : 'error'}`}>
            <h4>{testResult.success ? '✅ Test Successful' : '❌ Test Failed'}</h4>
            <p>{testResult.message}</p>
            {testResult.sample && (
              <div className="sample">
                <h5>Sample Tenders:</h5>
                <pre>{JSON.stringify(testResult.sample, null, 2)}</pre>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="error-message">
            ❌ {error}
          </div>
        )}
      </div>
    </div>
  );
}

export default AddScraperSource;
# OpenRAG Integration Guide for TenderApp

## Part 1: How OpenRAG Works

### 🎯 What is RAG?

**Retrieval-Augmented Generation** combines:
1. **Retrieval** - Finding relevant documents from a knowledge base
2. **Augmentation** - Using those documents to provide context
3. **Generation** - Using that context in an LLM to answer questions

For your TenderApp: Users can ask natural questions like "Show me tenders related to software development for healthcare" and RAG will find relevant tenders even if the exact keywords don't match.

---

### 📚 OpenRAG Architecture

OpenRAG is built on 4 core components:

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenRAG Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INGESTION LAYER                                         │
│     ├─ File Upload (PDF, DOCX, Images, Audio, etc)         │
│     ├─ Multiple Loaders convert to Markdown                │
│     └─ Document Serialization                              │
│                                                              │
│  2. PROCESSING LAYER                                       │
│     ├─ Chunking (split large docs into semantic chunks)    │
│     ├─ Embedding (convert text to vectors using VLM)       │
│     └─ Metadata Extraction (title, source, page, etc)      │
│                                                              │
│  3. STORAGE LAYER                                          │
│     ├─ Milvus (Vector Database - semantic search)          │
│     ├─ PostgreSQL (Metadata & User Management)             │
│     └─ Hybrid Search (BM25 sparse + Dense vectors)         │
│                                                              │
│  4. RETRIEVAL & GENERATION LAYER                           │
│     ├─ Semantic Search (find similar documents)            │
│     ├─ Reranking (score results by relevance)              │
│     ├─ Context Formatting (prepare for LLM)                │
│     ├─ LLM Generation (use OpenAI-compatible API)          │
│     └─ Source Attribution (cite where info came from)      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### 🔄 Document Processing Flow (In Detail)

#### Step 1: Upload & Serialization
```
User uploads PDF/DOCX → Appropriate Loader (MarkerLoader, DocxLoader) 
    → Converts to Markdown
    → Image extraction & VLM-powered captions
    → Returns normalized Document object
```

**For TenderApp**: Your tender data is already structured. You can:
- Export tender details to Markdown format
- Create embeddings from tender title + description + requirements

#### Step 2: Chunking
```
Full Document (e.g., 10 pages) 
    → Chunk into 512-token pieces
    → Add contextual metadata (source, chunk_id, page_num)
    → Preserve semantic relationships between chunks
```

**Why chunking?** 
- Vector databases work better with moderate-sized chunks
- Allows retrieval of specific information, not entire documents
- Improves relevance by targeting specific sections

#### Step 3: Embedding
```
Each chunk of text → Embedder (Jina v3 embeddings)
    → 1024-dimensional vector
    → Stored in Milvus for fast similarity search
```

**Key insight**: Similar tenders will have similar vectors, enabling semantic search.

#### Step 4: Storage with Hybrid Search
```
Milvus supports TWO search types:
1. DENSE (semantic): "Show tenders about software"
2. SPARSE (BM25): Keyword-based search using TF-IDF
3. HYBRID: Combine both for best results

Example:
- Dense: "healthcare project" matches "medical system" (semantic similarity)
- Sparse: "healthcare project" matches documents with "healthcare" keyword
- Result: Best of both worlds
```

#### Step 5: Retrieval Pipeline
```
User Query: "I need a tender for developing a mobile app"

→ Convert query to vector (using same embedder)
→ Search Milvus (hybrid search)
    ├─ Find 50 similar tenders
    ├─ Get top candidates
    └─ Re-rank using CrossEncoder (Alibaba reranker)
→ Select top-K results (e.g., 5-10 tenders)
→ Format context for LLM

Result: 
[
  {tender_id: 123, title: "Mobile App Dev...", score: 0.95},
  {tender_id: 456, title: "App Development...", score: 0.87},
  ...
]
```

#### Step 6: LLM Generation with Source Citation
```
System Prompt + Retrieved Context + User Question
    → OpenAI-compatible LLM
    → Response with [Source: 1, 3] citations
    → Filter to only cited sources
    → Return response + source metadata

Example Response:
"The best match is tender #123 (Healthcare Mobile App) 
 which requires 6 months timeline and $50K budget. 
 Another option is tender #456 (General App Dev).
 [Sources: 1, 3]"
```

---

### 🏗️ Technical Architecture Details

#### Ray Distributed Computing
```
OpenRAG uses Ray for horizontal scaling:

Master Node (API Server)
    ↓
    ├─ Indexer Actor (document processing)
    ├─ Vectordb Actor (Milvus operations)
    ├─ TaskStateManager (tracks ingestion progress)
    └─ Multiple Worker Nodes (load balancing)

Benefits:
- Process 1000s of documents in parallel
- Distribute embeddings across GPUs
- Scale to multiple machines
```

#### Multi-Tenancy & Partitions
```
Partition = Isolated document collection (like a namespace)

User A's Partitions
├─ "Public Tenders" (500 documents)
├─ "Private Projects" (100 documents)
└─ "Favorites" (20 documents)

User B's Partitions
├─ "Government" (1000 documents)
└─ "Private Sector" (500 documents)

Benefits:
- Users only see their own documents
- Role-based access (owner/editor/viewer)
- Organize by project, category, or team
```

#### Authentication & RBAC
```
Token-Based Auth:
1. User provides API token
2. Token hashed with SHA-256
3. Looked up in PostgreSQL
4. User permissions loaded
5. Access to partitions enforced

Roles:
- Viewer: Read-only access
- Editor: Can upload/modify documents
- Owner: Full control + can manage members
- Admin: System-wide access
```

---

### 🔌 APIs Provided by OpenRAG

```
1. INDEXER ENDPOINTS
   POST /indexer/add_file
   GET  /indexer/status/{task_id}
   DELETE /indexer/partition/{partition_id}

2. SEARCH ENDPOINTS
   POST /search/semantic
   POST /search/hybrid
   POST /search/rerank

3. OPENAI-COMPATIBLE
   POST /v1/chat/completions  ← Can use with LangChain, OpenWebUI
   GET  /v1/models

4. PARTITION MANAGEMENT
   POST /partition/create
   GET  /partition/list
   POST /partition/invite_user

5. USER MANAGEMENT
   POST /user/create
   GET  /user/profile
   POST /user/token/generate
```

---

## Part 2: How to Implement RAG for TenderApp

### 📋 Architecture: Integration with Your Flask Backend

```
Your TenderApp
├─ Frontend (React)
│  └─ Advanced Search Component
│     └─ Calls: /api/tenders/search/advanced (NEW)
│
├─ Backend (Flask) ← YOU ARE HERE
│  └─ /api/tenders/search/advanced
│     └─ Calls OpenRAG API
│
└─ OpenRAG (Separate Service)
   ├─ /indexer/add_file (index tender documents)
   ├─ /search/semantic (retrieve similar tenders)
   └─ /v1/chat/completions (generate answers)
```

### 🚀 Step-by-Step Implementation

#### STEP 1: Setup OpenRAG Services

**Option A: Docker Compose (Recommended)**

OpenRAG requires several services. Modify your docker-compose.yaml:

```yaml
version: '3.8'

services:
  # Existing PostgreSQL for TenderApp
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: tender_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: Postgrespwd12345.
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # NEW: Milvus Vector Database
  milvus:
    image: milvusdb/milvus:v0.4.0
    environment:
      COMMON_STORAGETYPE: local
    ports:
      - "19530:19530"
      - "9091:9091"
    volumes:
      - milvus_data:/var/lib/milvus

  # NEW: VLLM (embedding & LLM inference)
  vllm:
    image: vllm/vllm-openai:latest
    command: --model jinaai/jina-embeddings-v3 --tensor-parallel-size 1 --gpu-memory-utilization 0.9
    environment:
      - HF_MODEL_ID=jinaai/jina-embeddings-v3
      - HF_TOKEN=${HUGGINGFACE_TOKEN}
    ports:
      - "8000:8000"
    volumes:
      - vllm_cache:/root/.cache/huggingface

  # NEW: OpenRAG API
  openrag:
    build:
      context: ./openrag-main/openrag-main
      dockerfile: Dockerfile
    environment:
      BASE_URL: "http://vllm:8000/v1"
      MODEL: "gpt-3.5-turbo"
      API_KEY: ${OPENAI_API_KEY}
      VDB_HOST: milvus
      VDB_PORT: 19530
      POSTGRES_HOST: postgres
      POSTGRES_PASSWORD: Postgrespwd12345.
      EMBEDDER_BASE_URL: "http://vllm:8000/v1"
      RERANKER_BASE_URL: "http://reranker:7997"
    ports:
      - "8001:8000"
    depends_on:
      - milvus
      - vllm
      - postgres
    volumes:
      - ./openrag-main/openrag-main/conf:/app/conf

  # NEW: Reranker service
  reranker:
    image: michaelfeil/infinity:latest
    command: v2 --model-name-or-path Alibaba-NLP/gte-multilingual-reranker-base
    environment:
      - DEVICE=cpu
    ports:
      - "7997:7997"

volumes:
  postgres_data:
  milvus_data:
  vllm_cache:
```

**Start services:**
```bash
docker compose up -d milvus vllm reranker openrag postgres
```

---

#### STEP 2: Create Tender Embeddings

Create a new script: `backend/services/rag_service.py`

```python
import requests
from typing import List, Dict
from datetime import datetime
import json

class TenderRAGService:
    """Integrate tenders with OpenRAG"""
    
    def __init__(self, openrag_base_url: str = "http://localhost:8001"):
        self.openrag_base_url = openrag_base_url
        self.headers = {
            "Authorization": f"Bearer {os.getenv('OPENRAG_TOKEN', 'default_token')}",
            "Content-Type": "application/json"
        }
    
    def initialize_tender_partition(self, partition_name: str = "tenders"):
        """Create a partition for all tenders"""
        response = requests.post(
            f"{self.openrag_base_url}/partition/create",
            json={"name": partition_name, "description": "Government Tenders"},
            headers=self.headers
        )
        return response.json()
    
    def convert_tender_to_document(self, tender: Dict) -> str:
        """Convert tender to markdown for embedding"""
        doc = f"""# {tender.get('title', 'N/A')}

## Reference
{tender.get('reference', 'N/A')}

## Buyer
{tender.get('buyer', 'N/A')}

## Description
{tender.get('description', '')}

## Requirements
{tender.get('requirements', '')}

## Deadline
{tender.get('deadline', 'N/A')}

## Budget
{tender.get('budget', 'N/A')}

## Type
{tender.get('type', 'N/A')}

## Status
{tender.get('status', 'N/A')}
"""
        return doc
    
    def index_all_tenders(self, tenders: List[Dict]) -> Dict:
        """Index all tenders into OpenRAG"""
        indexed = 0
        failed = 0
        
        for tender in tenders:
            try:
                # Convert to markdown
                doc_content = self.convert_tender_to_document(tender)
                
                # Prepare file data (simulate file upload)
                files = {
                    'file': (
                        f"tender_{tender['id']}.md",
                        doc_content,
                        'text/markdown'
                    )
                }
                
                # Upload to OpenRAG
                response = requests.post(
                    f"{self.openrag_base_url}/indexer/add_file",
                    files=files,
                    headers={
                        "Authorization": self.headers["Authorization"]
                    },
                    data={
                        "partition": "tenders",
                        "metadata": json.dumps({
                            "tender_id": tender['id'],
                            "title": tender.get('title', ''),
                            "buyer": tender.get('buyer', '')
                        })
                    }
                )
                
                if response.status_code == 200:
                    indexed += 1
                else:
                    failed += 1
                    print(f"Failed to index tender {tender['id']}: {response.text}")
            
            except Exception as e:
                failed += 1
                print(f"Error indexing tender: {e}")
        
        return {
            "indexed": indexed,
            "failed": failed,
            "total": len(tenders)
        }
    
    def search_tenders_rag(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search tenders using semantic similarity"""
        response = requests.post(
            f"{self.openrag_base_url}/search/semantic",
            json={
                "query": query,
                "top_k": top_k,
                "partition": "tenders"
            },
            headers=self.headers
        )
        
        results = response.json().get('results', [])
        return results
    
    def search_with_rag_chat(self, query: str) -> Dict:
        """Use RAG with LLM for intelligent search"""
        response = requests.post(
            f"{self.openrag_base_url}/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 1000,
                "partition": "tenders",
                "include_sources": True
            },
            headers=self.headers
        )
        
        result = response.json()
        return {
            "answer": result.get('choices', [{}])[0].get('message', {}).get('content'),
            "sources": json.loads(result.get('extra', '{}').get('sources', '[]'))
        }
```

---

#### STEP 3: Add Backend Endpoints

In `backend/app.py`, add new routes:

```python
from services.rag_service import TenderRAGService

# Initialize RAG service
rag_service = TenderRAGService(os.getenv('OPENRAG_URL', 'http://localhost:8001'))

@app.route('/api/tenders/rag/initialize', methods=['POST'])
def initialize_rag():
    """Initialize RAG with all current tenders"""
    try:
        tenders = Tender.query.all()
        tender_dicts = [t.to_dict() for t in tenders]
        
        result = rag_service.index_all_tenders(tender_dicts)
        
        return jsonify({
            'success': True,
            'message': f"Indexed {result['indexed']} tenders",
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenders/search/semantic', methods=['POST'])
def search_tenders_semantic():
    """Semantic search for tenders"""
    try:
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', 5)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        results = rag_service.search_tenders_rag(query, top_k)
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenders/search/rag', methods=['POST'])
def search_tenders_with_rag():
    """Advanced RAG search with LLM-generated answers"""
    try:
        data = request.get_json()
        query = data.get('query')
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        result = rag_service.search_with_rag_chat(query)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'sources': result['sources']
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenders/rag/index-new', methods=['POST'])
def index_new_tender():
    """Index a newly scraped tender"""
    try:
        tender_id = request.get_json().get('tender_id')
        tender = Tender.query.get(tender_id)
        
        if not tender:
            return jsonify({'success': False, 'error': 'Tender not found'}), 404
        
        rag_service.index_all_tenders([tender.to_dict()])
        
        return jsonify({'success': True, 'message': 'Tender indexed'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
```

---

#### STEP 4: Create Frontend Search Component

Create `frontend/src/components/RAGSearch.jsx`:

```jsx
import React, { useState } from 'react';
import '../styles/RAGSearch.css';

export default function RAGSearch() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [activeTab, setActiveTab] = useState('semantic'); // semantic or rag

  const handleSemanticSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/tenders/search/semantic', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, top_k: 5 })
      });
      
      const data = await response.json();
      if (data.success) {
        setSources(data.results);
        setAnswer(`Found ${data.results.length} relevant tenders`);
      }
    } catch (error) {
      console.error('Search error:', error);
      setAnswer('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRAGSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const response = await fetch('/api/tenders/search/rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      
      const data = await response.json();
      if (data.success) {
        setAnswer(data.answer);
        setSources(data.sources);
      }
    } catch (error) {
      console.error('RAG search error:', error);
      setAnswer('RAG search failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="rag-search-container">
      <h2>Advanced Tender Search</h2>
      
      <div className="search-input-group">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about tenders... e.g., 'Software development tenders for healthcare'"
          className="search-input"
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              activeTab === 'semantic' ? handleSemanticSearch() : handleRAGSearch();
            }
          }}
        />
        
        <div className="search-tabs">
          <button
            className={`tab-btn ${activeTab === 'semantic' ? 'active' : ''}`}
            onClick={() => setActiveTab('semantic')}
          >
            🔍 Semantic Search
          </button>
          <button
            className={`tab-btn ${activeTab === 'rag' ? 'active' : ''}`}
            onClick={() => setActiveTab('rag')}
          >
            ✨ RAG Search
          </button>
        </div>
        
        <button
          onClick={activeTab === 'semantic' ? handleSemanticSearch : handleRAGSearch}
          disabled={loading}
          className="search-btn"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {answer && (
        <div className="search-results">
          <div className="answer-section">
            <h3>Answer:</h3>
            <p>{answer}</p>
          </div>
          
          {sources.length > 0 && (
            <div className="sources-section">
              <h3>📚 Related Tenders:</h3>
              {sources.map((source, idx) => (
                <div key={idx} className="source-card">
                  <div className="source-title">{source.title || source.name}</div>
                  <div className="source-score">Match: {(source.score * 100).toFixed(0)}%</div>
                  <div className="source-meta">{source.metadata}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

Create `frontend/src/styles/RAGSearch.css`:

```css
.rag-search-container {
  background: linear-gradient(135deg, #ffffff 0%, rgba(249, 250, 251, 0.5) 100%);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.rag-search-container h2 {
  color: var(--dark-red, #7f1d1d);
  margin-bottom: 16px;
  font-size: 20px;
  font-weight: 600;
}

.search-input-group {
  display: flex;
  gap: 12px;
  flex-direction: column;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-red, #dc2626);
  box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1);
}

.search-tabs {
  display: flex;
  gap: 8px;
  margin: 12px 0;
}

.tab-btn {
  padding: 8px 16px;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
  font-weight: 500;
}

.tab-btn.active {
  border-color: var(--primary-red, #dc2626);
  background: var(--primary-red, #dc2626);
  color: white;
}

.search-btn {
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--primary-red, #dc2626) 0%, #991b1b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.search-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.search-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.search-results {
  margin-top: 24px;
  animation: slideDown 0.3s ease;
}

.answer-section {
  background: white;
  border-left: 4px solid var(--primary-red, #dc2626);
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 16px;
}

.answer-section h3 {
  color: var(--primary-red, #dc2626);
  font-size: 14px;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.answer-section p {
  color: #374151;
  font-size: 14px;
  line-height: 1.6;
}

.sources-section h3 {
  color: var(--primary-red, #dc2626);
  font-size: 14px;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.source-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  transition: all 0.3s ease;
}

.source-card:hover {
  border-color: var(--primary-red, #dc2626);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.1);
}

.source-title {
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.source-score {
  display: inline-block;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: var(--primary-red, #dc2626);
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 8px;
}

.source-meta {
  font-size: 12px;
  color: #6b7280;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 768px) {
  .search-tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    width: 100%;
  }
}
```

---

#### STEP 5: Update Frontend to Use RAG Search

Add to your Tenders page or create a dedicated search page:

```jsx
// In frontend/src/pages/Tenders.jsx or new page

import RAGSearch from '../components/RAGSearch';

export default function TendersPage() {
  return (
    <>
      <RAGSearch />
      {/* Existing tenders list below */}
    </>
  );
}
```

---

### 📝 Environment Variables

Create/update `.env`:

```bash
# OpenRAG Configuration
OPENRAG_URL=http://localhost:8001
OPENRAG_TOKEN=your_rag_token_here
OPENAI_API_KEY=sk-...

# For GPU support
CUDA_VISIBLE_DEVICES=0

# Hugging Face (for embeddings)
HUGGINGFACE_TOKEN=hf_...
```

---

### 🚀 Complete Implementation Checklist

- [ ] Deploy OpenRAG services (Milvus, VLLM, Reranker, OpenRAG)
- [ ] Create `backend/services/rag_service.py`
- [ ] Add backend routes in `app.py`
- [ ] Create frontend `RAGSearch.jsx` component
- [ ] Add `RAGSearch.css`
- [ ] Initialize tenders in RAG: `POST /api/tenders/rag/initialize`
- [ ] Test semantic search: `POST /api/tenders/search/semantic`
- [ ] Test RAG search: `POST /api/tenders/search/rag`
- [ ] Add RAG search to frontend pages
- [ ] Modify scraper to auto-index new tenders

---

### 🔧 Advanced Features (Optional)

#### 1. Auto-Index New Tenders
```python
# In services/scraper.py after saving new tender
if rag_service:
    rag_service.index_all_tenders([tender.to_dict()])
```

#### 2. Filters with RAG
```python
# Search within specific buyer/type
def search_filtered(query, buyer=None, tender_type=None):
    # Add metadata filters to search
    return rag_service.search_tenders_rag(
        query,
        filters={"buyer": buyer, "type": tender_type}
    )
```

#### 3. Multi-Partition Support
```python
# Organize by categories
partitions = {
    "government": "Government tenders",
    "private": "Private sector tenders",
    "tech": "Technology tenders"
}

# Search across partitions
search_multi_partition(query, partitions=["tech", "government"])
```

---

## Summary: RAG Benefits for TenderApp

| Feature | Before | With RAG |
|---------|--------|----------|
| **Search** | Exact keyword match | Semantic similarity + LLM understanding |
| **Example** | "software" → only matches "software" | "software" → matches "app development", "coding project" |
| **Accuracy** | Manual filtering needed | Automatic ranking by relevance |
| **Scale** | 100s of tenders | 100,000s of tenders efficiently |
| **User Experience** | Browse & scan | Ask questions naturally |

**RAG transforms TenderApp from a database browser into an intelligent tender advisor!**

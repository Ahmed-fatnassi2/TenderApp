# OpenRAG Backend & Frontend Integration Guide

## Architecture Overview

The TenderApp now has a complete RAG (Retrieval-Augmented Generation) integration that enables semantic search of tender documents using OpenRAG, Milvus, and Ollama.

### Components:
- **Backend (Flask)**: REST API at `http://localhost:5000`
- **OpenRAG**: RAG service at `http://localhost:8081`
- **Milvus**: Vector database at `http://localhost:19530`
- **Ollama**: Embedding model server at `http://localhost:11434`
- **PostgreSQL**: Relational database at `localhost:5432`
- **Frontend (React+Vite)**: At `http://localhost:5173`

## Backend API Endpoints

### Health & Status
```
GET /api/health
- Check basic backend health
- Returns: {'status': 'healthy', 'database': 'PostgreSQL', 'message': '...'}

GET /api/rag/health
- Check OpenRAG service health
- Returns: {'rag_healthy': bool, 'status': 'connected'|'disconnected', 'backend': 'OpenRAG', 'url': '...'}
```

### Tender Management
```
GET /api/tenders
- Get all tenders with pagination
- Query params: page=1, per_page=100
- Returns: {'success': true, 'data': [...], 'pagination': {...}}

GET /api/tenders/count
- Get total tender count
- Returns: {'total': number}

GET /api/tenders/<reference>
- Get tender by reference
- Returns: tender object

POST /api/tenders/scrape
- Scrape new tenders from TUNEPS
- Returns: {'success': true, 'message': '...', 'data': {...}}

DELETE /api/tenders/<tender_id>
- Delete a tender
- Returns: {'message': 'Tender deleted'}
```

### RAG/OpenRAG Integration
```
POST /api/rag/initialize
- Index all tenders into OpenRAG
- Returns: {'success': bool, 'message': '...', 'data': {'total': num, 'successful': num, 'failed': num, 'errors': [...]}}
- Note: This can take several minutes for 1,000+ tenders

POST /api/rag/search/semantic
- Perform semantic search on indexed tenders
- Body: {'query': 'search text', 'top_k': 5, 'similarity_threshold': 0.75}
- Returns: {'success': true, 'query': '...', 'total': num, 'results': [...]}

POST /api/rag/index-tender
- Index a single tender to OpenRAG
- Body: {'tender_id': number}
- Returns: {'success': true, 'tender_id': num, 'file_id': '...'}

GET /api/openrag/health
- Check RAG service health (via blueprint route)
- Returns: {'success': true, 'healthy': bool, 'status': 'connected'|'disconnected'}

POST /api/openrag/search
- Alternative semantic search endpoint (via blueprint route)
- Body: {'query': 'text', 'top_k': 5, 'partition': 'tenders', 'similarity_threshold': 0.75}
- Returns: search results

POST /api/openrag/index-all
- Alternative batch indexing endpoint (via blueprint route)
- Returns: {'success': bool, 'message': '...', 'data': {...}}
```

## OpenRAGClient Class

The `backend/services/openrag_client.py` provides a Python wrapper for the OpenRAG API:

```python
from services.openrag_client import OpenRAGClient

client = OpenRAGClient(base_url="http://localhost:8081", auth_token="sk-openrag-dev")

# Health check
is_healthy = client.health_check()

# Create partition
client.create_partition("tenders")

# Upload single tender
result = client.upload_tender(tender_id, tender_data_dict)

# Batch upload
results = client.index_tenders_batch(tenders_list)

# Semantic search
search_results = client.search("road construction", top_k=5, partition_name="tenders")
```

## Frontend Components

### RAG Search Page (`frontend/src/pages/RAGSearch.jsx`)

Main interface for semantic search functionality:

**Features:**
- Real-time RAG health status
- One-click RAG initialization (indexes all tenders)
- Semantic search with natural language queries
- Adjustable search parameters (top_k, similarity threshold)
- Expandable result cards with metadata and similarity scores
- Responsive design for mobile and desktop

**Usage:**
1. Navigate to the "RAG Search" page from the sidebar
2. Click "Initialize RAG" on first use (indexes all tenders)
3. Enter a natural language query (e.g., "road construction projects")
4. Adjust top_k and similarity threshold if needed
5. Review results with similarity scores
6. Click results to expand and see full content

### Updated Tenders Page

The existing Tenders page now supports "Smart Search" toggle:
- Toggle between traditional text search and semantic search
- Semantic search uses the RAG endpoints automatically

### API Service (`frontend/src/services/api.js`)

JavaScript client for backend endpoints:

```javascript
import { apiService } from '../services/api';

// Health checks
await apiService.healthCheck();
await apiService.getRagHealth();

// Tenders
await apiService.getTenders(page, per_page);
await apiService.getTenderCount();
await apiService.deleteTender(tenderId);
await apiService.scrapeTenders();

// RAG Operations
await apiService.initializeRag();              // Index all tenders
await apiService.semanticSearch(query, topK); // Search indexed tenders
```

## Running the Full Stack

### 1. Start Docker Services
```bash
cd c:\ahmed\5eme\stage d'ete\tenderapp
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Milvus (port 19530)
- Ollama (port 11434)
- OpenRAG (port 8081, external 8080 mapped but disabled)

### 2. Start Flask Backend
```bash
cd backend
# Activate virtual environment
python -m venv venv
source venv/Scripts/activate  # or: venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run Flask app
python app.py
```
Backend runs on `http://localhost:5000`

### 3. Start Frontend (React)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on `http://localhost:5173`

### 4. Initialize RAG (First Time)
1. Open frontend in browser: `http://localhost:5173`
2. Navigate to "RAG Search" page
3. Click "Initialize RAG" button
4. Wait for indexing to complete (5-15 minutes for 1,026 tenders)
5. Start searching!

## Configuration

### Backend Environment Variables (`.env`)
```
DATABASE_URL=postgresql://postgres:Postgrespwd12345.@localhost:5432/tender_db
SECRET_KEY=dev-key
OPENRAG_TOKEN=sk-openrag-dev
OPENRAG_URL=http://localhost:8081
```

### OpenRAG Configuration (`.env` in openrag-main)
```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=Postgrespwd12345.
POSTGRES_DB=tender_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

EMBEDDING_MODEL=mxbai-embed-large
OLLAMA_BASE_URL=http://localhost:11434/v1

AUTH_TOKEN=sk-openrag-dev
```

## Troubleshooting

### RAG Health Check Fails
1. Verify Docker containers are running: `docker ps`
2. Check OpenRAG logs: `docker logs openrag-main-openrag-1`
3. Verify PostgreSQL credentials in `.env`
4. Check port 8081 is accessible: `curl http://localhost:8081/health_check`

### Semantic Search Returns No Results
1. Ensure RAG is initialized (click "Initialize RAG" button)
2. Check indexing completed successfully in backend logs
3. Try lowering the similarity_threshold slider
4. Verify Milvus is healthy: `curl http://localhost:19530/health`

### Indexing Takes Too Long
- This is normal for 1,000+ documents (estimated 5-15 minutes)
- Check backend logs for progress
- Ensure sufficient disk space for vector indices
- Consider batch indexing smaller groups first

### Port Conflicts
- If port 8081 is in use, modify docker-compose.yaml
- If port 5000 is in use, modify `app.py` run command
- If port 5173 is in use, modify `frontend/vite.config.js`

## Performance Optimization

1. **Batch Indexing**: Use `/api/rag/initialize` for all tenders at once
2. **Caching**: Frontend caches tender list to reduce API calls
3. **Pagination**: Use pagination on `/api/tenders` endpoint for large datasets
4. **Embedding Model**: mxbai-embed-large is efficient for semantic search
5. **Vector Index**: Milvus uses IVF_FLAT with IP metric for fast similarity search

## Future Enhancements

- [ ] Chat interface with RAG context
- [ ] Custom prompt engineering for response generation
- [ ] Integration with Deepseek API for LLM responses
- [ ] Advanced filtering by date, budget, category
- [ ] Saved searches and favorites
- [ ] Export search results
- [ ] Real-time indexing on new tender scrape
- [ ] RAG performance analytics

## Development Notes

- All backend code is in `backend/` with SQLAlchemy ORM
- Frontend uses React with Vite for hot module replacement
- OpenRAG handles embedding and vector search
- Milvus stores embeddings and supports hybrid search
- PostgreSQL stores original tender data and metadata

## Testing Checklist

- [ ] Backend `/api/health` returns 200
- [ ] `/api/rag/health` returns connected
- [ ] Can fetch tenders via `/api/tenders`
- [ ] Scrape endpoint adds new tenders
- [ ] Can initialize RAG via `/api/rag/initialize`
- [ ] Semantic search works with `/api/rag/search/semantic`
- [ ] Frontend loads and authenticates
- [ ] RAG Search page displays and initializes
- [ ] Smart search toggle works in Tenders page
- [ ] Results display with similarity scores

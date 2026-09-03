# OpenRAG Project Structure Guide

Complete breakdown of the OpenRAG codebase with all major folders, files, and their purposes.

---

## 📁 Top-Level Directory Structure

```
openrag-main/
├── .github/                    # GitHub CI/CD workflows
├── ansible/                    # Infrastructure as Code for deployment
├── automatic-evaluation-pipeline/  # Testing & evaluation tools
├── benchmarks/                 # Performance benchmarks
├── charts/                     # Kubernetes Helm charts
├── conf/                       # Configuration files (YAML)
├── docs/                       # Documentation & website
├── extern/                     # External dependencies
├── i8n/                        # Internationalization/localization
├── model_weights/              # Pre-downloaded model weights
├── openrag/                    # ⭐ MAIN APPLICATION (Python package)
├── openrag_metrics/            # Metrics & evaluation
├── prompts/                    # LLM prompt templates
├── quick_start/                # Quick start examples
├── tests/                      # Integration tests
├── utility/                    # Utility scripts
├── vdb/                        # Vector database configs
├── pyproject.toml             # Python dependencies
├── docker-compose.yaml        # Docker services
└── Dockerfile                 # Container image
```

---

## 🎯 Core Application: `/openrag/` (Main Code)

This is where all the RAG logic lives. Structure:

```
openrag/
├── api.py                      # ⭐ ENTRY POINT - FastAPI app initialization
├── config.py                   # Configuration loader
├── dependencies.py             # Dependency injection
│
├── components/                 # Core RAG components
│   ├── __init__.py
│   ├── auth/                   # Authentication & authorization
│   ├── indexer/                # Document ingestion pipeline
│   ├── pipeline.py             # RAG orchestration pipeline
│   ├── prompts/                # LLM system prompts
│   ├── reranker/               # Result re-ranking
│   └── websearch/              # Web search integration
│
├── routers/                    # FastAPI API endpoints
│   ├── auth.py                 # User authentication
│   ├── indexer.py              # /indexer/* endpoints
│   ├── search.py               # /search/* endpoints
│   ├── openai.py               # /v1/chat/completions (OpenAI-compatible)
│   ├── partition.py            # Partition management
│   ├── users.py                # User management
│   ├── workspaces.py           # Workspace CRUD
│   ├── queue.py                # Task queue status
│   ├── monitoring.py           # Health & metrics
│   ├── tools.py                # Tool execution
│   ├── download.py             # File downloads
│   ├── extract.py              # Text extraction
│   └── utils.py                # Auth helpers
│
├── models/                     # Data models (Pydantic schemas)
│   ├── user.py
│   ├── partition.py
│   ├── document.py
│   └── ...
│
├── config/                     # Configuration modules
│   └── config.py
│
├── utils/                      # Utilities
│   ├── logger.py               # Logging setup
│   ├── exceptions.py           # Custom exceptions
│   ├── dependencies.py         # FastAPI dependencies
│   └── ...
│
├── public/                     # Static files & web UI
│   └── (HTML, CSS, JS)
│
├── scripts/                    # Standalone scripts
│   └── ...
│
└── tests/                      # Unit tests
    └── test_*.py
```

---

## 🔧 Component Deep Dive: `/openrag/components/`

### 1. **Indexer** (`components/indexer/`) - Document Ingestion Pipeline

The heart of document processing. Converts files → vectors → database storage.

```
indexer/
├── __init__.py
├── indexer.py                  # ⭐ Main Indexer actor (Ray distributed)
├── chunker/                    # Document splitting
│   ├── __init__.py
│   ├── base.py                 # BaseChunker abstract class
│   ├── semantic_chunker.py     # Semantic-aware splitting
│   ├── recursive_chunker.py    # Recursive splitting strategy
│   └── test_chunking.py
│
├── embeddings/                 # Vector generation
│   ├── __init__.py
│   ├── embedder.py             # Main embedder (uses VLLM/OpenAI)
│   └── test_embeddings.py
│
├── loaders/                    # File format converters → Markdown
│   ├── base.py                 # BaseLoader abstract class
│   ├── txt_loader.py           # .txt files
│   ├── markdown_loader.py      # .md files
│   ├── pdf_loaders/
│   │   ├── marker_loader.py    # Advanced PDF (OCR, tables)
│   │   └── pypdf_loader.py
│   ├── docx_loader.py          # .docx files
│   ├── pptx_loader.py          # .pptx files
│   ├── audio_loader.py         # .wav, .mp3, .mp4 (Whisper transcription)
│   ├── image_loader.py         # .png, .jpg (Vision LLM captions)
│   ├── eml_loader.py           # Email files
│   ├── web_loader.py           # Web URLs
│   └── __init__.py
│
├── vectordb/                   # Vector database operations
│   ├── base.py                 # BaseVectorDB interface
│   ├── milvus.py               # Milvus implementation
│   ├── qdrant.py               # Qdrant implementation (alternative)
│   ├── vectordb.py             # Main VectorDB actor
│   ├── utils.py                # Database schema, migrations
│   └── test_vectordb.py
│
├── utils.py                    # Serialization & helpers
├── constants.py                # File type mappings
└── test_indexer.py
```

**Key Classes:**
- `Indexer` (Ray Actor): Main entry point for document processing
- `Document`: Normalized representation of any file
- `Chunker`: Splits documents into processable pieces
- `Embedder`: Converts text to vectors
- `VectorDB`: Interface to Milvus/Qdrant

**Flow:**
```
File Upload → Loader (serialize to markdown) 
→ Chunker (split into pieces) 
→ Embedder (generate vectors) 
→ VectorDB (store in Milvus)
```

---

### 2. **Pipeline** (`components/pipeline.py`) - RAG Orchestration

Orchestrates the retrieval + generation process.

```python
class RagPipeline:
    # Takes query → retrieves docs → formats for LLM → calls LLM → returns answer
    
    async def run(query: str) -> str:
        # 1. Convert query to vectors
        # 2. Search VectorDB for similar documents
        # 3. Re-rank results
        # 4. Format context
        # 5. Send to LLM with prompt
        # 6. Extract sources from response
        # 7. Return answer + citations
```

**Key Methods:**
- `format_context()`: Prepare documents for LLM
- `extract_and_strip_sources_block()`: Parse [Sources: 1, 2, 3]
- `filter_sources_by_citations()`: Only return cited sources

---

### 3. **Reranker** (`components/reranker/`) - Result Scoring

Re-scores search results using cross-encoder models.

```
reranker/
├── base.py                     # BaseReranker abstract class
├── infinity.py                 # Infinity backend (Alibaba reranker)
├── openai.py                   # OpenAI reranking
└── factory.py                  # Factory pattern for creation
```

**Purpose:** 
- Initial search finds 50 candidates (semantic search)
- Reranker scores all 50, returns top 10
- Improves relevance significantly

---

### 4. **Auth** (`components/auth/`) - Security & Access Control

```
auth/
├── middleware.py               # Token validation middleware
├── rbac.py                     # Role-Based Access Control
└── models.py                   # User/role/partition schemas
```

**Features:**
- Token-based authentication (SHA-256 hashed)
- Role hierarchy: viewer → editor → owner → admin
- Partition-based access control

---

### 5. **Prompts** (`components/prompts/`) - LLM Instructions

```python
# Example prompt templates
SYS_PROMPT_TMPLT = """You are a helpful assistant...
Context: {context}
Always cite sources as [Sources: 1, 3]
"""

QUERY_CONTEXTUALIZER_PROMPT = """Expand this query for better retrieval...
"""

RERANKER_PROMPT = """Score document relevance to query...
"""
```

---

## 🛣️ API Routes: `/openrag/routers/`

Maps HTTP endpoints to functionality. Each file = one router.

### **1. `indexer.py`** - Document Ingestion Endpoints

```
POST /indexer/add_file              # Upload & index a file
POST /indexer/add_text              # Add raw text
GET  /indexer/status/{task_id}      # Check ingestion progress
DELETE /indexer/{file_id}           # Remove indexed file
POST /indexer/cancel/{task_id}      # Cancel ongoing ingestion
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/indexer/add_file \
  -F "file=@document.pdf" \
  -F "partition=my_docs" \
  -H "Authorization: Bearer token"
```

---

### **2. `search.py`** - Search Endpoints

```
POST /search/semantic              # Vector similarity search
POST /search/hybrid                # Dense + sparse search
POST /search/rerank                # Re-rank existing results
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/search/semantic \
  -H "Content-Type: application/json" \
  -d '{
    "query": "software development",
    "top_k": 5,
    "partition": "tenders"
  }'
```

---

### **3. `openai.py`** - OpenAI-Compatible Endpoint

Drop-in replacement for OpenAI API. Enables use with LangChain, OpenWebUI, etc.

```
POST /v1/chat/completions          # Chat with RAG context
POST /v1/models                    # List available models
GET  /v1/models/{model}            # Model details
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [
      {"role": "user", "content": "Find software tenders"}
    ],
    "partition": "tenders"
  }'
```

---

### **4. `partition.py`** - Multi-Tenancy Management

Organize documents into isolated collections.

```
POST /partition/create             # Create new partition
GET  /partition/list               # List all partitions
DELETE /partition/{id}             # Delete partition
POST /partition/{id}/invite        # Add user to partition
GET  /partition/{id}/files         # List files in partition
```

---

### **5. `users.py`** - User Management

```
POST /user/create                  # Register new user
GET  /user/profile                 # Get current user info
POST /user/token/generate          # Create API token
DELETE /user/token                 # Revoke token
```

---

### **6. `workspaces.py`** - Named Document Groups

Organize files within a partition.

```
POST /workspace/create             # Create workspace
GET  /workspace/list               # List workspaces
POST /workspace/{id}/files         # Add files to workspace
DELETE /workspace/{id}             # Delete workspace
```

---

### **7. `monitoring.py`** - System Health

```
GET  /health                       # Health check
GET  /metrics                      # Prometheus metrics
GET  /queue/status                 # Job queue status
GET  /actor/status                 # Ray actor status
```

---

### **8. Other Routers**

| Router | Purpose |
|--------|---------|
| `auth.py` | Login, logout, token management |
| `queue.py` | View task queue & job status |
| `tools.py` | Execute helper tools (text extraction, etc) |
| `download.py` | Download indexed documents |
| `extract.py` | Extract text from documents |
| `actors.py` | Manage Ray actors |

---

## 🛠️ Utilities: `/openrag/utils/`

Helper modules for common functionality:

```
utils/
├── logger.py                   # Logging configuration
├── exceptions.py               # Custom error types
├── dependencies.py             # FastAPI dependency injection
├── config_loader.py            # Load config from YAML
├── document_parser.py          # Common doc operations
└── ...
```

---

## 🎯 Key Data Models: `/openrag/models/`

Pydantic schemas defining data structures:

```python
# Example models
class User(BaseModel):
    id: str
    email: str
    token_hash: str
    is_admin: bool

class Partition(BaseModel):
    name: str
    description: str
    owner_id: str

class Document(BaseModel):
    id: str
    content: str
    metadata: dict
    created_at: datetime
    embeddings: list[float]
```

---

## ⚙️ Configuration: `/conf/`

YAML configuration files:

```
conf/
├── config.yaml                 # Main config (LLM, VDB, etc)
└── profiles/                   # Different configurations
    ├── dev.yaml
    ├── prod.yaml
    └── test.yaml
```

**What's Configured:**
- LLM provider & model
- Embedder settings
- Vector database connection
- Chunking strategy
- Reranking settings
- Authentication
- Ray cluster settings

---

## 📦 Dependencies: `pyproject.toml`

Key Python packages:

```toml
dependencies = [
    "fastapi>=0.116",           # Web framework
    "ray[default]>=2.47.1",     # Distributed computing
    "langchain>=0.3",           # LLM abstractions
    "pymilvus>=2.6.9",          # Milvus client
    "marker-pdf>=0.2.17",       # Advanced PDF parsing
    "openai>=1.64.0",           # OpenAI API
    "chainlit>=2.2.1",          # Chat UI
    "docling>=2.24.0",          # Document parsing
    "faster-whisper>=1.1.0",    # Audio transcription
    ...
]
```

---

## 🐳 Docker Services: `docker-compose.yaml`

```yaml
services:
  # Main API
  api:
    build: .
    ports:
      - "8000:8000"
  
  # Ray cluster
  ray-head:
    image: ray:latest
  
  # Vector database
  milvus:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"
  
  # Embedder & LLM inference
  vllm:
    image: vllm/vllm-openai:latest
    ports:
      - "8001:8000"
  
  # Reranker service
  reranker:
    image: michaelfeil/infinity:latest
    ports:
      - "7997:7997"
  
  # PostgreSQL metadata
  postgres:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

---

## 🔄 Request Flow Example: "Index a PDF"

```
1. User uploads PDF to /indexer/add_file
   ↓
2. FastAPI route (routers/indexer.py) receives request
   ↓
3. Indexer Ray Actor invoked:
   - serialize_file() → MarkerLoader converts PDF to markdown
   - chunk() → SemanticChunker splits into ~512-token pieces
   - embed() → VLLM generates vectors
   - insert() → Milvus stores vectors + metadata
   ↓
4. TaskStateManager tracks progress:
   QUEUED → SERIALIZING → CHUNKING → EMBEDDING → INSERTING → COMPLETED
   ↓
5. Client polls /indexer/status/{task_id} to check progress
   ↓
6. File is now searchable via /search/semantic endpoint
```

---

## 🔍 Request Flow Example: "Search with RAG"

```
1. User sends POST /v1/chat/completions with query
   ↓
2. OpenAI router (routers/openai.py) receives request
   ↓
3. Pipeline.run() orchestrates:
   
   a) Query Understanding
      - Expand/contextualize query via LLM
      
   b) Retrieval
      - Convert query to embedding
      - Search Milvus (hybrid search)
      - Get 50 candidates
      
   c) Re-ranking
      - Reranker scores all 50
      - Keep top 10
      
   d) Context Formatting
      - Format_context() → "[Source 1]\n...\n[Source 2]\n..."
      
   e) LLM Generation
      - Send: system prompt + context + query
      - LLM responds with answer + [Sources: 1, 2]
      
   f) Source Filtering
      - Extract [Sources: 1, 2]
      - Filter document list to only cited sources
      
   g) Response
      - Return answer + metadata + source documents
   ↓
4. Response sent to client
```

---

## 🎯 Key Architecture Patterns

### **1. Ray Actors (Distributed Computing)**
```python
@ray.remote
class Indexer:
    # Runs on Ray worker nodes
    # Can be distributed across machines
    # Concurrent task handling with concurrency_groups
```

**Why?** 
- Scale document processing across GPUs
- Parallel embedding generation
- Load balancing

### **2. Factory Pattern (Component Creation)**
```python
# Load appropriate implementation based on config
embedder = EmbedderFactory.create_embedder(config)
chunker = ChunkerFactory.create_chunker(config)
reranker = RerankerFactory.create_reranker(config)
```

**Why?** Easy to swap implementations (e.g., Milvus ↔ Qdrant)

### **3. Dependency Injection (FastAPI)**
```python
async def search(
    query: str,
    vectordb: VectorDB = Depends(get_vectordb),
    auth_user: User = Depends(require_admin)
):
    # Dependencies injected by FastAPI
    # Cleaner testing & decoupling
```

### **4. Async/Await (Non-blocking I/O)**
```python
# All I/O is non-blocking
async def index_file(path: str):
    doc = await serialize_file(path)      # File I/O
    chunks = await chunker.split(doc)     # Processing
    await vectordb.insert(chunks)         # DB write
```

**Why?** Handle 1000s of concurrent requests

---

## 📊 Data Flow Architecture

```
┌─────────────────────────────────────────────────────┐
│                   FastAPI Server                     │
│  (routers/: indexer, search, openai, partition)    │
└──────────────────┬──────────────────────────────────┘
                   │
       ┌───────────┴──────────┬──────────────┐
       │                      │              │
       ↓                      ↓              ↓
   ┌────────┐          ┌──────────┐    ┌────────┐
   │ Ray    │          │ Pipeline │    │ Auth   │
   │ Actors │          │  (RAG)   │    │Middleware
   └────────┘          └──────────┘    └────────┘
       │                      │
   ┌───┴──────────┐       ┌───┴──────────┐
   │              │       │              │
  ┌▼──────┐  ┌───▼───┐  ┌▼────────┐  ┌──▼────┐
  │Indexer│  │Chunker│  │Embedder │  │Pipeline
  └───┬───┘  └───────┘  └────┬────┘  └───┬───┘
      │                       │           │
  ┌───┴──────────────────────┴───────────┴─┐
  │                                        │
  │  Dependencies & Utils                  │
  │  - Logger, Config, Exceptions         │
  │  - Document Parser, Constants         │
  │                                        │
  └────────────────┬─────────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
    ┌───▼───┐  ┌──▼────┐  ┌──▼──────┐
    │Milvus │  │VLLM   │  │Infinity │
    │(VDB)  │  │(LLM)  │  │(Rerank) │
    └────────  └───────┘  └────────┘
```

---

## 🚀 Deployment Patterns

### **Embedded (Single Machine)**
```
Single Python process with embedded Ray
- api.py starts Ray cluster
- Milvus, VLLM, Reranker in Docker containers
- Good for development & small deployments
```

### **Distributed (Multiple Machines)**
```
Ray Head Node (API server)
├─ Worker Node 1 (GPU 1)
├─ Worker Node 2 (GPU 2)
└─ Worker Node 3 (GPU 3)

Separate services:
- Milvus cluster
- VLLM cluster
- Reranker cluster
- PostgreSQL cluster
```

---

## Summary: File Purpose Map

| File/Folder | Purpose | Key Components |
|-------------|---------|-----------------|
| `api.py` | FastAPI app init | Ray initialization, middleware setup |
| `components/indexer/` | Document processing | Loader, Chunker, Embedder, VectorDB |
| `components/pipeline.py` | RAG orchestration | Query→Retrieval→Rerank→Generate |
| `routers/indexer.py` | Upload endpoints | /indexer/add_file, /indexer/status |
| `routers/search.py` | Search endpoints | /search/semantic, /search/hybrid |
| `routers/openai.py` | LLM chat | /v1/chat/completions (drop-in) |
| `routers/partition.py` | Multi-tenancy | Document collection isolation |
| `models/` | Data schemas | User, Partition, Document |
| `conf/config.yaml` | Settings | LLM, VDB, chunking strategy |
| `docker-compose.yaml` | Infrastructure | Services: Milvus, VLLM, Reranker |

---

## 🎓 Learning Path

**To understand OpenRAG in order:**

1. **Start with `api.py`** - Understand FastAPI setup, Ray initialization, middleware
2. **Read `routers/indexer.py`** - See how documents are uploaded
3. **Study `components/indexer/indexer.py`** - Understand the main processing pipeline
4. **Explore `components/indexer/loaders/`** - How files are converted to documents
5. **Review `components/indexer/chunker/`** - How documents are split
6. **Check `components/indexer/vectordb/`** - How vectors are stored
7. **Trace `components/pipeline.py`** - How RAG orchestrates retrieval+generation
8. **Look at `routers/search.py`** - How users query documents
9. **Study `routers/openai.py`** - OpenAI-compatible wrapper
10. **Review `conf/config.yaml`** - Understand all configuration options

---

## 🔗 Key Relationships

```
api.py
  ├─ initializes Ray cluster
  ├─ loads config from conf/config.yaml
  ├─ creates FastAPI app
  ├─ registers routers (indexer, search, openai, partition, users, etc)
  ├─ adds middleware (auth, monitoring, rate-limit)
  └─ serves on port 8000

routers/*
  ├─ accept HTTP requests
  ├─ validate input (Pydantic models from models/)
  ├─ call Ray actors (Indexer, VectorDB, TaskStateManager)
  ├─ return responses

components/indexer/indexer.py (Ray Actor)
  ├─ calls loaders/* to serialize files
  ├─ calls chunker/* to split documents
  ├─ calls embeddings/embedder.py to generate vectors
  └─ calls vectordb/* to store in Milvus

components/pipeline.py
  ├─ retrieves documents from VectorDB
  ├─ calls reranker/ to re-score results
  ├─ formats context for LLM
  ├─ calls LLM (VLLM or OpenAI)
  └─ extracts and filters sources

config/
  └─ controls all settings for LLM, VDB, chunking, auth, etc
```

This structure makes OpenRAG:
- **Modular**: Easy to swap components
- **Scalable**: Ray handles distribution
- **Multi-tenant**: Partitions isolate documents
- **API-compatible**: Works with LangChain, OpenWebUI, etc

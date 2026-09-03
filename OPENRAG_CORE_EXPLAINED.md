# OpenRAG: Main Parts You Need to Know

Focused guide showing what's important and what's not, plus which files are active during operations.

---

## 🎯 ESSENTIAL vs OPTIONAL

### ✅ **ESSENTIAL Folders** (You need to understand these)

| Folder | Importance | What It Does | When It's Used |
|--------|-----------|-------------|-----------------|
| **`openrag/api.py`** | ⭐⭐⭐ CRITICAL | Starts the FastAPI server & Ray cluster | Every request starts here |
| **`openrag/components/indexer/`** | ⭐⭐⭐ CRITICAL | Processes & ingests documents | When uploading tenders |
| **`openrag/routers/`** | ⭐⭐⭐ CRITICAL | HTTP API endpoints | Every user action |
| **`openrag/components/pipeline.py`** | ⭐⭐⭐ CRITICAL | RAG orchestration (search + LLM) | When searching/chatting |
| **`conf/config.yaml`** | ⭐⭐ HIGH | Configuration settings | On startup |

### 📦 **SECONDARY Folders** (Nice to know, not essential)

| Folder | What It Does | When Used |
|--------|-------------|-----------|
| `openrag/models/` | Data validation schemas | Behind the scenes |
| `openrag/utils/` | Logging, helpers | Behind the scenes |
| `openrag/components/auth/` | User authentication | Login only |
| `openrag/components/prompts/` | LLM templates | During LLM calls |
| `openrag/components/reranker/` | Re-score results | During search |

### ⏭️ **OPTIONAL Folders** (Skip for now)

| Folder | Purpose |
|--------|---------|
| `.github/` | GitHub CI/CD workflows |
| `ansible/` | Server deployment scripts |
| `benchmarks/` | Performance testing |
| `charts/` | Kubernetes configs |
| `docs/` | Documentation website |
| `tests/` | Integration tests |

---

## 🔥 The 3 Core Parts (MOST IMPORTANT)

### **Part 1: INDEXER** (`openrag/components/indexer/`)
**Purpose:** Convert files → vectors → database

```
indexer/
├── indexer.py              ⭐ MAIN - Orchestrates everything
├── loaders/                → Convert PDF/DOCX/TXT to Markdown
├── chunker/                → Split documents into pieces
├── embeddings/             → Convert text to vectors
└── vectordb/               → Store vectors in Milvus
```

**When it's used:** When you upload a tender document

---

### **Part 2: ROUTERS** (`openrag/routers/`)
**Purpose:** HTTP endpoints - the API interface

```
routers/
├── indexer.py              → POST /indexer/add_file (upload)
├── search.py               → POST /search/semantic (search)
├── openai.py               → POST /v1/chat/completions (RAG chat)
├── partition.py            → Organize documents by user
└── others (users, auth...)
```

**When it's used:** Every HTTP request from frontend

---

### **Part 3: PIPELINE** (`openrag/components/pipeline.py`)
**Purpose:** RAG orchestration - search documents + generate answers

```
pipeline.py
├── Retrieves documents from Milvus
├── Re-ranks results
├── Formats context for LLM
├── Calls LLM (VLLM/OpenAI)
└── Extracts & filters sources
```

**When it's used:** When user searches or asks a question

---

## 📊 WHAT FILES ARE ACTIVE DURING EACH OPERATION?

### **Operation 1: INDEX A TENDER DOCUMENT** 📤

**User uploads: `tender_proposal.pdf`**

Files that activate (in order):

```
1. fastapi/routers/indexer.py
   └─ Receives POST /indexer/add_file request
   
2. components/indexer/indexer.py (Ray Actor)
   └─ Main coordinator
   
3. components/indexer/loaders/pdf_loaders/marker_loader.py
   ├─ Extracts text from PDF
   ├─ Handles images, tables, OCR
   └─ Converts to Markdown
   
4. components/indexer/chunker/semantic_chunker.py
   ├─ Splits Markdown into ~512-token chunks
   └─ Preserves context between chunks
   
5. components/indexer/embeddings/embedder.py
   ├─ Calls VLLM server (external service)
   └─ Generates 1024-dimensional vectors for each chunk
   
6. components/indexer/vectordb/milvus.py
   ├─ Connects to Milvus database
   └─ Stores vectors + metadata
   
7. utils/logger.py
   └─ Logs progress to console/file
```

**Result:** Document is searchable 🎉

**Config used:** `conf/config.yaml` (chunking strategy, embedder settings)

---

### **Operation 2: SEARCH TENDERS** 🔍

**User searches: "software development for healthcare"**

Files that activate (in order):

```
1. routers/search.py
   └─ Receives POST /search/semantic request
   
2. components/pipeline.py
   ├─ Receives query
   └─ Orchestrates entire process
   
3. components/indexer/embeddings/embedder.py
   ├─ Converts query to vector
   └─ Same model as indexing (consistency!)
   
4. components/indexer/vectordb/milvus.py
   ├─ Semantic search: Find 50 similar vectors
   ├─ Hybrid search: Also keyword search (BM25)
   └─ Returns raw candidates
   
5. components/reranker/infinity.py (or openai.py)
   ├─ Re-scores all 50 candidates
   ├─ Uses CrossEncoder model
   └─ Keeps top 10 results
   
6. components/utils.py
   ├─ Formats results
   └─ Returns to API
   
7. routers/search.py
   └─ Sends JSON response to frontend
```

**Result:** Top 10 most relevant tenders returned

**Config used:** `conf/config.yaml` (reranker model, top_k settings)

---

### **Operation 3: RAG SEARCH (LLM-Powered)** 🤖

**User asks: "Find tenders that need healthcare IT expertise"**

Files that activate (in order):

```
1. routers/openai.py
   └─ Receives POST /v1/chat/completions request
   
2. components/pipeline.py (RagPipeline class)
   ├─ Receives user question
   ├─ Expands query for better retrieval
   └─ Orchestrates: Retrieve → Rerank → Generate
   
3. components/indexer/embeddings/embedder.py
   ├─ Converts expanded query to vector
   └─ Searches Milvus
   
4. components/indexer/vectordb/milvus.py
   ├─ Retrieves 50 candidates
   ├─ Uses hybrid search
   └─ Returns chunks + metadata
   
5. components/reranker/infinity.py
   ├─ Scores 50 candidates
   └─ Keeps top 10
   
6. components/utils.py
   ├─ format_context() → Converts to "[Source 1] text [Source 2] text"
   ├─ Number each source
   └─ Ensures within token limit for LLM
   
7. components/prompts/ (any prompt template)
   ├─ Loads system prompt template
   └─ Template: "You are a helpful assistant... Always cite sources as [Sources: 1, 3]"
   
8. VLLM or OpenAI API (external service)
   ├─ Receives: system prompt + context + question
   ├─ Generates answer
   └─ Response includes: "Based on tender #123... [Sources: 1, 3, 5]"
   
9. components/pipeline.py
   ├─ extract_and_strip_sources_block() → Removes [Sources: 1, 3, 5] from response
   ├─ filter_sources_by_citations() → Only include cited sources
   └─ Prepares final response
   
10. routers/openai.py
    └─ Sends response + sources to frontend
```

**Result:** Natural language answer with cited sources

**Config used:** 
- `conf/config.yaml` (LLM model, reranker, etc)
- `components/prompts/` (system instructions)

---

## 🗂️ QUICK REFERENCE: WHICH FILES FOR EACH TASK?

### **Task: Add a new file format support (e.g., PPT slides)**

Edit: `components/indexer/loaders/pptx_loader.py`
- Define: How to convert PowerPoint to Markdown
- Add image caption support
- Test with sample PPT

---

### **Task: Change chunking strategy**

Edit: `components/indexer/chunker/semantic_chunker.py`
- Adjust chunk size
- Change overlap
- Modify splitting logic

Then update: `conf/config.yaml`
- Set chunker type (recursive, semantic, etc)

---

### **Task: Use different reranker model**

Edit: `conf/config.yaml`
```yaml
reranker:
  model_name: "your-model-name"
  provider: "infinity"  # or "openai"
```

---

### **Task: Change LLM provider (OpenAI → Llama locally)**

Edit: `conf/config.yaml`
```yaml
llm:
  model: "llama-2-70b"
  base_url: "http://vllm:8000/v1"
  api_key: "EMPTY"
```

---

### **Task: Add multi-language support**

Edit: `components/utils.py`
- Add language detection
- Load appropriate prompts

Edit: `components/prompts/`
- Add translations

---

## 🎯 THE MINIMUM YOU NEED TO UNDERSTAND

### **For TenderApp Integration:**

You primarily need to know:

1. **`routers/indexer.py`**
   - How to upload tenders
   - How to check indexing status

2. **`routers/search.py`**
   - How to do semantic search
   - What query parameters are needed

3. **`routers/openai.py`**
   - How to chat with RAG
   - Response format

4. **`components/indexer/`**
   - How documents are processed internally
   - Why output is standardized

5. **`conf/config.yaml`**
   - What settings affect behavior
   - How to tune for your use case

6. **`components/pipeline.py`**
   - How RAG orchestrates search+LLM
   - Source citation mechanism

---

## 📈 TYPICAL WORKFLOW IN YOUR TENDERAPP

```
┌─────────────────────────────────────────────────────────────┐
│                   Your TenderApp Frontend                    │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ↓               ↓               ↓
    ┌─────────┐   ┌──────────┐   ┌──────────┐
    │ Upload  │   │ Search   │   │ RAG Chat │
    │Tender   │   │Tender    │   │with LLM  │
    └────┬────┘   └────┬─────┘   └────┬─────┘
         │             │              │
         ↓             ↓              ↓
   ┌────────────────────────────────────────┐
   │  routers/indexer.py                    │
   │  routers/search.py                     │
   │  routers/openai.py                     │
   └─────────────┬──────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ↓            ↓            ↓
┌──────────┐ ┌────────┐ ┌─────────────┐
│ Indexer  │ │Pipeline│ │ VectorDB    │
│components│ │components
│          │ │        │ │  (Milvus)   │
└──────────┘ └────────┘ └─────────────┘
    │            │            │
    └────────────┼────────────┘
                 │
            ┌────▼──────┐
            │ LLM/VLLM  │
            │ Reranker  │
            │ Embedder  │
            │ (External)│
            └───────────┘
```

---

## 🔗 ACTUAL CODE FLOW: SEARCH EXAMPLE

When user clicks "Search" for "software development tenders":

```python
# 1. User clicks search button
# Frontend sends: POST /search/semantic
# Route: routers/search.py
@router.post("/semantic")
async def search_semantic(query: str, top_k: int = 5):
    # 2. Call pipeline
    results = await pipeline.search(query, top_k)
    # Pipeline does:
    #   - Call embedder to convert query to vector
    #   - Call milvus.search() to find 50 candidates
    #   - Call reranker to score all 50
    #   - Return top 5
    return results

# 3. Response sent to frontend
# Frontend displays results
```

**Files that ran:**
- `routers/search.py` - API endpoint
- `components/pipeline.py` - Orchestration
- `components/indexer/embeddings/embedder.py` - Query embedding
- `components/indexer/vectordb/milvus.py` - Similarity search
- `components/reranker/infinity.py` - Re-ranking

---

## 🎯 SUMMARY: FILES YOU ABSOLUTELY MUST KNOW

| File | Why | When Modified |
|------|-----|----------------|
| `openrag/api.py` | Entry point | Rarely (setup only) |
| `openrag/routers/indexer.py` | Upload API | Never (you use it) |
| `openrag/routers/search.py` | Search API | Never (you use it) |
| `openrag/routers/openai.py` | RAG Chat API | Never (you use it) |
| `openrag/components/indexer/indexer.py` | Doc processing | Never (you use it) |
| `openrag/components/pipeline.py` | RAG logic | Maybe (custom flows) |
| `conf/config.yaml` | Settings | Often (tuning) |
| `components/prompts/` | LLM instructions | Sometimes (better answers) |

---

## 📝 WHAT HAPPENS STEP-BY-STEP

### **Step 1: Initialize RAG for Tenders**

```bash
# Backend does this once during setup
POST /indexer/add_file
├─ File: tender_1.md
├─ Partition: "government-tenders"
└─ Metadata: {id: 123, buyer: "Ministry of Health"}

# Files active:
# - routers/indexer.py
# - components/indexer/indexer.py
# - components/indexer/loaders/markdown_loader.py (no conversion needed)
# - components/indexer/chunker/semantic_chunker.py
# - components/indexer/embeddings/embedder.py
# - components/indexer/vectordb/milvus.py
```

### **Step 2: User Searches**

```bash
# User searches for "healthcare IT"
POST /search/semantic
├─ Query: "healthcare IT"
├─ Top_k: 5
└─ Partition: "government-tenders"

# Files active:
# - routers/search.py
# - components/pipeline.py
# - components/indexer/embeddings/embedder.py
# - components/indexer/vectordb/milvus.py
# - components/reranker/infinity.py
```

### **Step 3: User Asks a Question (RAG)**

```bash
# User asks: "Which tenders need Python expertise?"
POST /v1/chat/completions
├─ Messages: [{role: "user", content: "Which tenders..."}]
├─ Model: "gpt-3.5-turbo"
└─ Partition: "government-tenders"

# Files active:
# - routers/openai.py
# - components/pipeline.py (RagPipeline)
# - components/indexer/embeddings/embedder.py
# - components/indexer/vectordb/milvus.py
# - components/reranker/infinity.py
# - components/prompts/*.txt (system prompt)
# - VLLM API (external LLM service)
# - components/utils.py (formatting)
```

---

## ⚡ PERFORMANCE: What files to tune for speed?

| Bottleneck | File to Edit | What to Change |
|-----------|-------------|-----------------|
| Indexing is slow | `components/indexer/chunker/` | Increase chunk size |
| Search is slow | `components/indexer/vectordb/milvus.py` | Tune collection parameters |
| LLM responses slow | `conf/config.yaml` | Use faster LLM model |
| Reranking slow | `conf/config.yaml` | Reduce `reranker.top_k` |
| Memory usage high | `components/indexer/embeddings/embedder.py` | Use smaller embedder model |

---

## 🎓 READ IN THIS ORDER

For TenderApp integration:

1. **Start here:** `openrag/api.py` (5 min)
   - Understand FastAPI setup

2. **Then:** `conf/config.yaml` (5 min)
   - Understand configuration

3. **Then:** `routers/search.py` (10 min)
   - Understand search API

4. **Then:** `routers/openai.py` (10 min)
   - Understand RAG chat API

5. **Then:** `components/pipeline.py` (15 min)
   - Understand RAG orchestration

6. **Then:** `components/indexer/indexer.py` (15 min)
   - Understand document processing

7. **Optionally:** Everything else
   - Deep dives for specific features

**Total: 60 minutes to understand OpenRAG well enough to use it!**


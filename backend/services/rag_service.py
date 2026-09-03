import os
import requests
import json
from typing import List, Dict, Optional
from datetime import datetime
import logging
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility

logger = logging.getLogger(__name__)


class TenderRAGService:
    """Service to integrate TenderApp with Milvus for semantic search"""

    def __init__(self):
        # We use Ollama as it is much more stable on CPU/WSL than vLLM
        self.embedding_url = os.getenv('EMBEDDING_URL', 'http://localhost:11434')
        self.milvus_host = os.getenv('MILVUS_HOST', 'localhost')
        self.milvus_port = int(os.getenv('MILVUS_PORT', 19530))
        self.collection_name = 'tenders'
        # mxbai-embed-large uses 1024 dimensions
        self.embedding_dim = 1024
        self.embedding_model = "mxbai-embed-large"
        
        self._collection_initialized = False
        self._model_available = False
        
        logger.info(f"TenderRAGService initialized:")
        logger.info(f"  Embedding Provider: {self.embedding_url} (Ollama)")
        logger.info(f"  Milvus: {self.milvus_host}:{self.milvus_port}")
        
        # Connect to Milvus
        self.connect_milvus()


    def ensure_model_downloaded(self):
        """Tell Ollama to pull the model if not present"""
        if self._model_available:
            return
        try:
            logger.info(f"Ensuring embedding model '{self.embedding_model}' is available...")
            response = requests.post(
                f"{self.embedding_url}/api/pull",
                json={"name": self.embedding_model},
                timeout=30
            )
            if response.status_code == 200:
                self._model_available = True
                logger.info("Model successfully pulled/verified")
        except Exception as e:
            logger.warning(f"Could not pull model from Ollama: {e}")

    def ensure_collection_created(self):
        """Create Milvus collection if it doesn't exist (lazy initialization)"""
        if self._collection_initialized:
            return
        self.create_collection()
        self._collection_initialized = True

    def connect_milvus(self):
        """Connect to Milvus"""
        try:
            connections.connect("default", host=self.milvus_host, port=self.milvus_port)
            logger.info("Connected to Milvus")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise

    def create_collection(self):
        """Create Milvus collection if it doesn't exist"""
        try:
            if utility.has_collection(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return
            
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="tender_id", dtype=DataType.INT64),
                FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="buyer", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="type", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="reference", dtype=DataType.VARCHAR, max_length=200),
                FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=10000),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            ]
            
            schema = CollectionSchema(fields=fields, description="Government Tenders")
            collection = Collection(name=self.collection_name, schema=schema)
            
            # Create index on embedding field
            index_params = {
                "metric_type": "L2",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 100}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            
            logger.info(f"Collection '{self.collection_name}' created successfully")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def test_connection(self) -> bool:
        """Test if services are reachable"""
        try:
            # Test Ollama (instead of VLLM)
            try:
                response = requests.get(
                    f'{self.embedding_url}/api/tags',
                    timeout=5
                )
                embedding_healthy = response.status_code == 200
            except:
                embedding_healthy = False
            
            # Test Milvus
            try:
                # Just check if we can list collections
                milvus_healthy = utility.has_collection(self.collection_name) is not None
            except:
                milvus_healthy = False
            
            is_healthy = embedding_healthy and milvus_healthy
            logger.info(f"Services health: Embedding={embedding_healthy}, Milvus={milvus_healthy}")
            return is_healthy
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

    def get_embedding(self, text: str) -> Optional[List[float]]:
        """Get embedding from Ollama"""
        try:
            response = requests.post(
                f'{self.embedding_url}/api/embeddings',
                json={
                    "model": self.embedding_model,
                    "prompt": text
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                embedding = result['embedding']
                return embedding
            else:
                logger.error(f"Ollama embedding failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return None

    def convert_tender_to_markdown(self, tender: Dict) -> str:
        """Convert tender dict to markdown format for embedding"""
        doc = f"""# {tender.get('title', 'Untitled Tender')}

## Reference
{tender.get('reference', 'N/A')}

## Buyer
{tender.get('buyer', 'N/A')}

## Type
{tender.get('type', 'N/A')}

## Description
{tender.get('description', 'No description')}

## Requirements
{tender.get('requirements', 'No requirements specified')}

## Deadline
{tender.get('deadline', 'N/A')}

## Budget
{tender.get('budget', 'N/A')}

## Status
{tender.get('status', 'N/A')}
"""
        return doc

    def index_tender(self, tender: Dict) -> Dict:
        """Index a single tender into Milvus"""
        try:
            # Ensure collection exists
            self.ensure_collection_created()
            self.ensure_model_downloaded()
            
            # Convert to markdown
            content = self.convert_tender_to_markdown(tender)
            
            # Get embedding
            embedding = self.get_embedding(content)
            if not embedding:
                return {
                    'success': False,
                    'tender_id': tender['id'],
                    'error': 'Failed to get embedding'
                }
            
            # Insert into Milvus
            collection = Collection(self.collection_name)
            collection.insert([
                [tender['id']],  # tender_id
                [tender.get('title', '')],
                [tender.get('buyer', '')],
                [tender.get('type', '')],
                [tender.get('reference', '')],
                [content],
                [embedding]
            ])
            
            logger.info(f"Indexed tender {tender['id']}")

            return {
                'success': True,
                'tender_id': tender['id']
            }
        
        except Exception as e:
            logger.error(f"Error indexing tender {tender.get('id')}: {e}")
            return {
                'success': False,
                'tender_id': tender.get('id'),
                'error': str(e)
            }

    def index_all_tenders(self, tenders: List[Dict]) -> Dict:
        """Index multiple tenders - optimized for batch processing"""
        try:
            # Setup once for all tenders
            self.ensure_collection_created()
            self.ensure_model_downloaded()
            
            results = {
                'total': len(tenders),
                'indexed': 0,
                'failed': 0,
                'batch_size': min(50, len(tenders))  # Process 50 at a time
            }
            
            logger.info(f"Starting batch indexing of {len(tenders)} tenders...")
            
            collection = Collection(self.collection_name)
            
            # Process tenders in batches
            batch = {
                'tender_ids': [],
                'titles': [],
                'buyers': [],
                'types': [],
                'references': [],
                'contents': [],
                'embeddings': []
            }
            
            for idx, tender in enumerate(tenders):
                try:
                    # Convert to markdown
                    content = self.convert_tender_to_markdown(tender)
                    
                    # Get embedding
                    embedding = self.get_embedding(content)
                    if not embedding:
                        logger.warning(f"Skipping tender {tender.get('id')}: failed to get embedding")
                        results['failed'] += 1
                        continue
                    
                    # Add to batch
                    batch['tender_ids'].append(tender['id'])
                    batch['titles'].append(tender.get('title', ''))
                    batch['buyers'].append(tender.get('buyer', ''))
                    batch['types'].append(tender.get('type', ''))
                    batch['references'].append(tender.get('reference', ''))
                    batch['contents'].append(content)
                    batch['embeddings'].append(embedding)
                    
            # Insert batch when it reaches batch_size or end of list
                    if len(batch['embeddings']) >= results['batch_size'] or idx == len(tenders) - 1:
                        if batch['embeddings']:
                            try:
                                # Clean strings for Milvus (max length 500)
                                def clean_str(s, max_len=500):
                                    if not s: return ""
                                    s = str(s)
                                    return (s[:max_len-3] + '...') if len(s) > max_len else s

                                cleaned_titles = [clean_str(t) for t in batch['titles']]
                                cleaned_buyers = [clean_str(b) for b in batch['buyers']]
                                
                                collection.insert([
                                    batch['tender_ids'],
                                    cleaned_titles,
                                    cleaned_buyers,
                                    batch['types'],
                                    batch['references'],
                                    batch['contents'],
                                    batch['embeddings']
                                ])
                                collection.flush() # Ensure data is written
                                results['indexed'] += len(batch['embeddings'])
                                logger.info(f"Indexed batch of {len(batch['embeddings'])} tenders ({results['indexed']}/{results['total']})")
                                
                                # Reset batch
                                batch = {
                                    'tender_ids': [],
                                    'titles': [],
                                    'buyers': [],
                                    'types': [],
                                    'references': [],
                                    'contents': [],
                                    'embeddings': []
                                }
                            except Exception as e:
                                logger.error(f"Error inserting batch: {e}")
                                results['failed'] += len(batch['embeddings'])
                                batch = {
                                    'tender_ids': [],
                                    'titles': [],
                                    'buyers': [],
                                    'types': [],
                                    'references': [],
                                    'contents': [],
                                    'embeddings': []
                                }
                
                except Exception as e:
                    logger.error(f"Error processing tender {tender.get('id')}: {e}")
                    results['failed'] += 1
                    continue
            
            logger.info(f"Batch indexing complete: {results['indexed']}/{results['total']} successful, {results['failed']} failed")
            return results
        
        except Exception as e:
            logger.error(f"Error in batch indexing: {e}")
            return {
                'total': len(tenders),
                'indexed': 0,
                'failed': len(tenders),
                'error': str(e)
            }

    def search_semantic(self, query: str, top_k: int = 5) -> Dict:
        """Perform semantic search on indexed tenders"""
        try:
            # Ensure collection exists
            self.ensure_collection_created()
            self.ensure_model_downloaded()
            
            # Get query embedding
            query_embedding = self.get_embedding(query)
            if not query_embedding:
                return {
                    'success': False,
                    'error': 'Failed to embed query'
                }
            
            # Search in Milvus
            collection = Collection(self.collection_name)
            collection.load() # MODIFIED: Ensure collection is loaded before search
            results = collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["tender_id", "title", "buyer", "type", "reference"]
            )
            
            search_results = []
            for hits in results:
                for hit in hits:
                    search_results.append({
                        'tender_id': hit.entity.get('tender_id'),
                        'title': hit.entity.get('title'),
                        'buyer': hit.entity.get('buyer'),
                        'type': hit.entity.get('type'),
                        'reference': hit.entity.get('reference'),
                        'score': float(hit.score)
                    })
            
            logger.info(f"Semantic search for '{query}': found {len(search_results)} results")
            return {
                'success': True,
                'query': query,
                'results': search_results,
                'count': len(search_results)
            }
        
        except Exception as e:
            logger.error(f"Error performing semantic search: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
_rag_service = None
_rag_service_error = None


def get_rag_service() -> Optional[TenderRAGService]:
    """Get or create RAG service instance, returns None if unavailable"""
    global _rag_service, _rag_service_error
    if _rag_service is None and _rag_service_error is None:
        try:
            _rag_service = TenderRAGService()
        except Exception as e:
            _rag_service_error = str(e)
            logger.error(f"Failed to initialize RAG service: {e}")
    return _rag_service

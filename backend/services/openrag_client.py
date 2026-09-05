# """
# OpenRAG Client - Wrapper for OpenRAG API
# Handles document ingestion and semantic search against tenders
# """
# import os
# import requests
# import json
# import io
# from typing import List, Dict, Any
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)


# class OpenRAGClient:
#     def __init__(self, base_url: str = None, auth_token: str = None):
#         """Initialize OpenRAG client
        
#         Args:
#             base_url: OpenRAG API base URL (default: uses OPENRAG_URL env var or http://127.0.0.1:8080)
#             auth_token: Optional authentication token (if not provided, uses placeholder)
#         """
#         # Use provided base_url, env variable, or default
#         if base_url is None:
#             base_url = os.getenv("OPENRAG_URL", "http://127.0.0.1:8080")
#         self.base_url = base_url.rstrip('/')
#         print(f"DEBUG: OpenRAGClient initialized with base_url={self.base_url}, env OPENRAG_URL={os.getenv('OPENRAG_URL')}")
#         # Use provided token, default placeholder, or empty for no auth
#         self.auth_token = auth_token or os.getenv("OPENRAG_TOKEN", "sk-openrag-dev")
#         self.partition_name = "tenders"
#         self.headers = self._build_headers()
    
#     def _build_headers(self) -> dict:
#         """Build request headers with authorization"""
#         headers = {}
#         if self.auth_token:
#             headers['Authorization'] = f'Bearer {self.auth_token}'
#         return headers
        
#     def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
#         """Make HTTP request to OpenRAG API"""
#         url = f"{self.base_url}{endpoint}"
#         headers = {**self.headers, **kwargs.get('headers', {})}
#         try:
#             response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
#             response.raise_for_status()
#             return response.json() if response.text else {}
#         except requests.exceptions.RequestException as e:
#             logger.error(f"OpenRAG API error: {e}")
#             raise
    
#     def create_partition(self, partition_name: str = None) -> Dict[str, Any]:
#         """Create a partition for tenders
        
#         Args:
#             partition_name: Name of partition (default: 'tenders')
        
#         Returns:
#             API response
#         """
#         partition_name = partition_name or self.partition_name
#         endpoint = f"/partition/{partition_name}"
#         try:
#             result = self._request('POST', endpoint)
#             logger.info(f"Created partition: {partition_name}")
#             return {"success": True, "partition": partition_name}
#         except requests.exceptions.HTTPException as e:
#             if e.response.status_code == 409:  # Already exists
#                 logger.info(f"Partition {partition_name} already exists")
#                 return {"success": True, "partition": partition_name, "message": "Partition already exists"}
#             raise
    
#     def upload_tender(self, tender_id: str, tender_data: Dict[str, Any], partition_name: str = None) -> Dict[str, Any]:
#         """Upload a single tender as a document
        
#         Args:
#             tender_id: Unique tender ID
#             tender_data: Tender data dictionary
#             partition_name: Target partition (default: 'tenders')
        
#         Returns:
#             API response with task status
#         """
#         partition_name = partition_name or self.partition_name
        
#         # Create text content from tender data
#         content = self._tender_to_text(tender_data)
        
#         # Create metadata
#         metadata = {
#             "tender_id": str(tender_id),
#             "title": tender_data.get('title', 'Untitled Tender'),
#             "reference": tender_data.get('reference', ''),
#             "source": "TUNEPS",
#             "created_at": datetime.utcnow().isoformat(),
#         }
        
#         # Upload via OpenRAG indexer API
#         file_id = f"tender_{tender_id}"
        
#         # Create file-like object
#         file_content = io.BytesIO(content.encode('utf-8'))
#         files = {
#             'file': (f"{file_id}.txt", file_content, 'text/plain')
#         }
#         data = {
#             'metadata': json.dumps(metadata)
#         }
        
#         endpoint = f"/indexer/partition/{partition_name}/file/{file_id}"
#         try:
#             response = requests.post(
#                 f"{self.base_url}{endpoint}",
#                 files=files,
#                 data=data,
#                 headers=self.headers,
#                 timeout=30
#             )
#             response.raise_for_status()
#             logger.info(f"Uploaded tender {tender_id} to OpenRAG")
#             return {"success": True, "tender_id": tender_id, "file_id": file_id}
#         except Exception as e:
#             logger.error(f"Failed to upload tender {tender_id}: {e}")
#             raise
    
#     def index_tenders_batch(self, tenders: List[Dict[str, Any]], partition_name: str = None) -> Dict[str, Any]:
#         """Index multiple tenders
        
#         Args:
#             tenders: List of tender dictionaries
#             partition_name: Target partition (default: 'tenders')
        
#         Returns:
#             Summary of indexing results
#         """
#         partition_name = partition_name or self.partition_name
        
#         # Ensure partition exists
#         self.create_partition(partition_name)
        
#         results = {
#             "total": len(tenders),
#             "successful": 0,
#             "failed": 0,
#             "errors": []
#         }
        
#         for tender in tenders:
#             try:
#                 self.upload_tender(tender.get('id'), tender, partition_name)
#                 results["successful"] += 1
#             except Exception as e:
#                 results["failed"] += 1
#                 results["errors"].append({
#                     "tender_id": tender.get('id'),
#                     "error": str(e)
#                 })
        
#         return results
    
#     def search(self, query: str, top_k: int = 5, partition_name: str = None, 
#                similarity_threshold: float = 0.75) -> Dict[str, Any]:
#         """Perform semantic search across tenders
        
#         Args:
#             query: Search query text
#             top_k: Number of results to return
#             partition_name: Partition to search (default: 'tenders')
#             similarity_threshold: Minimum similarity score (0-1)
        
#         Returns:
#             Search results with matched tenders
#         """
#         partition_name = partition_name or self.partition_name
        
#         params = {
#             "partitions": [partition_name],
#             "text": query,
#             "top_k": top_k,
#             "similarity_threshold": similarity_threshold
#         }
        
#         try:
#             response = requests.get(
#                 f"{self.base_url}/search",
#                 params=params,
#                 headers=self.headers,
#                 timeout=30
#             )
#             response.raise_for_status()
#             results = response.json()
            
#             # Parse results
#             parsed_results = {
#                 "success": True,
#                 "query": query,
#                 "total": len(results.get("results", [])),
#                 "results": []
#             }
            
#             for result in results.get("results", []):
#                 parsed_results["results"].append({
#                     "content": result.get("content", ""),
#                     "score": result.get("similarity_score", 0),
#                     "metadata": result.get("metadata", {})
#                 })
            
#             return parsed_results
            
#         except Exception as e:
#             logger.error(f"Search failed: {e}")
#             raise
    
#     def health_check(self) -> bool:
#         """Check if OpenRAG is healthy"""
#         try:
#             response = requests.get(f"{self.base_url}/health_check", timeout=5)
#             return response.status_code == 200
#         except Exception as e:
#             logger.error(f"OpenRAG health check failed: {e}")
#             return False
    
#     @staticmethod
#     def _tender_to_text(tender_data: Dict[str, Any]) -> str:
#         """Convert tender dictionary to formatted text for indexing
        
#         Args:
#             tender_data: Tender information
        
#         Returns:
#             Formatted text string
#         """
#         lines = [
#             f"Title: {tender_data.get('title', '')}",
#             f"Reference: {tender_data.get('reference', '')}",
#             f"",
#             f"Description:",
#             f"{tender_data.get('description', '')}",
#             f"",
#             f"Details:",
#             f"- Budget: {tender_data.get('budget', 'N/A')}",
#             f"- Location: {tender_data.get('location', 'N/A')}",
#             f"- Category: {tender_data.get('category', 'N/A')}",
#             f"- Start Date: {tender_data.get('start_date', 'N/A')}",
#             f"- End Date: {tender_data.get('end_date', 'N/A')}",
#         ]
#         return "\n".join(lines)
import io
from urllib import response

import os
import requests
import json
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger(__name__)
# from openrag.openrag.openrag.core.models import query

class OpenRAGClient:
    def __init__(self, base_url=None, token=None):
        # Use environment variable if base_url not provided
        if base_url is None:
            base_url = os.getenv("OPENRAG_URL", "http://localhost:8080")
        # Use environment variable if token not provided
        if token is None:
            token = os.getenv("OPENRAG_TOKEN", "or-openrag-1234")
        
        self.base_url = base_url
        self.token = token
        print(f"[OpenRAGClient] Initialized with base_url={self.base_url}, token={self.token[:10]}...")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.milvus_initialized = False
        self.milvus_collection = None



    # def _init_milvus(self):
    #     """Initialize Milvus connection for direct operations"""
    #     if self.milvus_initialized:
    #         return
    
    #     try:
    #         from pymilvus import connections, Collection
        
    #     # Your backend is on the host machine, Milvus is exposed on localhost:19530
    #         connections.connect(host='localhost', port='19530')
    #         logger.info("✅ Connected to Milvus at localhost:19530")
        
    #         self.milvus_collection = Collection('tender_db')
    #         self.milvus_collection.load()
    #         self.milvus_initialized = True
    #         logger.info("✅ Milvus collection 'tender_db' loaded successfully")
    #     except Exception as e:
    #         logger.error(f"❌ Failed to connect to Milvus: {e}")
    #     # Don't raise - we can still use OpenRAG for deletion
    #         logger.warning("⚠️ Direct Milvus connection failed, OpenRAG deletion will still work")











    def health_check(self) -> bool:
        """Check if OpenRAG is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health_check",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    # def search(self, query: str, top_k: int = 5, partition_name: str = "tenders", similarity_threshold: float = 0.75) -> Dict:
    #     """Search for relevant documents using semantic search"""
    #     response = requests.post(
    #         f"{self.base_url}/v1/chat/completions",
    #         headers=self.headers,
    #         json={
    #             "messages": [{"role": "user", "content": query}],
    #             "model": "deepseek-v4-flash",
    #             "metadata": {
    #                 "partition": partition_name,
    #                 "top_k": top_k,
    #                 "similarity_threshold": similarity_threshold
    #             }
    #         }
    #     )
    #     return response.json()

    def search(self, query: str, top_k: int = 5, partition_name: str = "tenders", similarity_threshold: float = 0.75) -> Dict:
        """Search for relevant documents using semantic search"""
        # Use the /search endpoint with parameters
        params = {
            "text": query,
            "partitions": partition_name,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
    
        response = requests.get(
            f"{self.base_url}/search",
            params=params,
            headers=self.headers
        )
        return response.json()








    # def upload_tender(self, tender_id: int, tender_data: Dict) -> Dict:
    #     """Upload/Index a single tender to OpenRAG"""
    #     # Create a text representation using your actual tender fields
    #     content = f"""
    #     Tender Reference: {tender_data.get('reference', 'N/A')}
    #     Title: {tender_data.get('title', 'N/A')}
    #     Buyer: {tender_data.get('buyer', 'N/A')}
    #     Publication Date: {tender_data.get('publication_date', 'N/A')}
    #     Deadline: {tender_data.get('deadline', 'N/A')}
    #     Source: {tender_data.get('source', 'TUNEPS')}
    #     """
    
    #     response = requests.post(
    #         f"{self.base_url}/v1/chat/completions",
    #         headers=self.headers,
    #         json={
    #             "messages": [
    #                 {"role": "user", "content": f"Please index this tender document for searching:\n\n{content}"}
    #             ],
    #             "model": "deepseek-v4-flash",
    #             "metadata": {
    #                 "partition": "tenders",
    #                 "tender_id": tender_id,
    #                 "index_mode": True
    #             }
    #         }
    #     )
    #     return response.json()


    def upload_tender(self, tender_id: int, tender_data: Dict) -> Dict:
        """Upload/Index a single tender to OpenRAG as a file"""
        import io
    
        # Create text content
        content = f"""Tender Reference: {tender_data.get('reference', 'N/A')}
        Title: {tender_data.get('title', 'N/A')}
        Buyer: {tender_data.get('buyer', 'N/A')}
        Publication Date: {tender_data.get('publication_date', 'N/A')}
        Deadline: {tender_data.get('deadline', 'N/A')}
        Source: {tender_data.get('source', 'TUNEPS')}
        """
    
        # Create file-like object
        file_content = io.BytesIO(content.encode('utf-8'))
    
        files = {
            'file': (f"tender_{tender_id}.txt", file_content, 'text/plain')
        }
    
        data = {
            'metadata': json.dumps({
            'tender_id': tender_id,
            'reference': tender_data.get('reference', ''),
            'buyer': tender_data.get('buyer', ''),
            'source': 'TUNEPS'
        })
    }
    
        response = requests.post(
            f"{self.base_url}/indexer/partition/tenders/file/tender_{tender_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            files=files,
            data=data,
            timeout=30
        )
        return response.json()











    def index_tenders_batch(self, tenders: List[Dict]) -> Dict:
        """Submit multiple tenders for indexing (non-blocking)
        
        Submits all documents to OpenRAG and returns immediately with task IDs.
        Does NOT wait for indexing to complete.
        """
        task_ids = []
        failed_count = 0
        
        for i, tender in enumerate(tenders):
            try:
                tender_id = tender.get('id', tender.get('tender_id'))
                if not tender_id:
                    failed_count += 1
                    continue
                
                # Submit to OpenRAG without waiting
                try:
                    result = self._submit_tender_async(tender_id, tender)
                    if result.get('error'):
                        print(f"[batch {i}] Tender {tender_id}: {result.get('error')}")
                        failed_count += 1
                        continue
                        
                    if 'task_status_url' in result:
                        # Extract task_id from URL: /indexer/task/{task_id}
                        task_id = result['task_status_url'].split('/')[-1]
                        task_ids.append({
                            'tender_id': tender_id,
                            'task_id': task_id,
                            'status_url': result['task_status_url']
                        })
                    else:
                        print(f"[batch {i}] Tender {tender_id}: No task_status_url in response: {result}")
                        failed_count += 1
                except Exception as e:
                    print(f"[batch {i}] Error submitting tender {tender_id}: {type(e).__name__}: {e}")
                    failed_count += 1
            except Exception as e:
                print(f"[batch {i}] Error processing tender: {type(e).__name__}: {e}")
                failed_count += 1
        
        return {
            "total": len(tenders),
            "submitted": len(task_ids),
            "failed": failed_count,
            "task_ids": task_ids
        }
    
    def _submit_tender_async(self, tender_id: int, tender_data: Dict) -> Dict:
        """Submit a single tender without waiting for completion"""
        import io
        
        try:
            content = f"""Tender Reference: {tender_data.get('reference', 'N/A')}
        Title: {tender_data.get('title', 'N/A')}
        Buyer: {tender_data.get('buyer', 'N/A')}
        Publication Date: {tender_data.get('publication_date', 'N/A')}
        Deadline: {tender_data.get('deadline', 'N/A')}
        Source: {tender_data.get('source', 'TUNEPS')}
        """
            
            file_content = io.BytesIO(content.encode('utf-8'))
            files = {
                'file': (f"tender_{tender_id}.txt", file_content, 'text/plain')
            }
            data = {
                'metadata': json.dumps({
                    'tender_id': tender_id,
                    'reference': tender_data.get('reference', ''),
                    'buyer': tender_data.get('buyer', ''),
                    'source': 'TUNEPS'
                })
            }
            
            url = f"{self.base_url}/indexer/partition/tenders/file/tender_{tender_id}"
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code >= 400:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
            
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": f"Request timeout for tender_{tender_id}"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {str(e)}"}
    
    def get_task_status(self, task_id: str) -> Dict:
        """Check status of an indexing task"""
        try:
            response = requests.get(
                f"{self.base_url}/indexer/task/{task_id}",
                headers=self.headers,
                timeout=5
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_partitions(self) -> List[Dict]:
        """Get all partitions"""
        response = requests.get(
            f"{self.base_url}/partition/",
            headers=self.headers
        )
        return response.json().get("partitions", [])

    # def delete_tender(self, tender_id: int, partition_name: str = "tenders") -> Dict:
    #     """Delete a single tender document from OpenRAG/Milvus
        
    #     Args:
    #         tender_id: Tender ID to delete
    #         partition_name: Partition name (default: 'tenders')
        
    #     Returns:
    #         API response
    #     """
    #     try:
    #         # The file_id is the document ID in OpenRAG
    #         file_id = f"tender_{tender_id}"
    #         url = f"{self.base_url}/indexer/partition/{partition_name}/file/{file_id}"
            
    #         response = requests.delete(
    #             url,
    #             headers={"Authorization": f"Bearer {self.token}"},
    #             timeout=30
    #         )
            
    #         if response.status_code == 404:
    #             # Document not found - consider it already deleted
    #             return {"success": True, "message": f"Document {file_id} already deleted or not found"}
            
    #         response.raise_for_status()
    #         return {"success": True, "message": f"Deleted document {file_id}"}
            
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"Failed to delete tender {tender_id} from OpenRAG: {e}")
    #         return {"success": False, "error": str(e), "tender_id": tender_id}

    # ============ DELETE USING OPENRAG ONLY ============
    def delete_tender(self, tender_id: int, partition_name: str = "tenders") -> Dict:
        """Delete a single tender document from both OpenRAG and Milvus"""
        results = {
            "tender_id": tender_id,
            "openrag_deleted": False,
            "milvus_deleted": False,
            "error": None
        }
    
    # 1. Delete from OpenRAG
        try:
            file_id = f"tender_{tender_id}"
            url = f"{self.base_url}/indexer/partition/{partition_name}/file/{file_id}"
        
            logger.info(f"🗑️ DELETE from OpenRAG: {url}")
        
            response = requests.delete(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=30
            )
        
            if response.status_code in [200, 204]:
                results["openrag_deleted"] = True
                logger.info(f"✅ Deleted tender {tender_id} from OpenRAG")
            elif response.status_code == 404:
                results["openrag_deleted"] = True
                logger.info(f"ℹ️ Tender {tender_id} already deleted from OpenRAG")
            else:
                results["error"] = f"OpenRAG HTTP {response.status_code}"
                logger.warning(f"⚠️ OpenRAG deletion returned: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error deleting from OpenRAG: {e}")
            results["error"] = str(e)
    
    # 2. Delete from Milvus via OpenRAG container (if OpenRAG deletion succeeded)
        if results["openrag_deleted"]:
            try:
                logger.info(f"🗑️ Deleting tender {tender_id} from Milvus via container...")
                milvus_success = self.delete_from_milvus_via_container(tender_id)
                results["milvus_deleted"] = milvus_success
                if milvus_success:
                    logger.info(f"✅ Deleted tender {tender_id} from Milvus")
                else:
                    logger.warning(f"⚠️ Failed to delete tender {tender_id} from Milvus")
            except Exception as e:
                logger.error(f"Error deleting from Milvus: {e}")
                results["milvus_deleted"] = False
                if not results["error"]:
                    results["error"] = f"Milvus error: {str(e)}"
    
    # ✅ This return should be OUTSIDE the if block
        return results

    def delete_tenders_batch(self, tender_ids: List[int], partition_name: str = "tenders") -> Dict:
        """Delete multiple tenders from both OpenRAG and Milvus"""
        results = {
            "total": len(tender_ids),
            "openrag_successful": 0,
            "milvus_successful": 0,
            "failed": 0,
            "errors": []
        }
    
        for tender_id in tender_ids:
            try:
                result = self.delete_tender(tender_id, partition_name)
            
                if result["openrag_deleted"]:
                    results["openrag_successful"] += 1
                if result["milvus_deleted"]:
                    results["milvus_successful"] += 1
            
                if not result["openrag_deleted"] and not result["milvus_deleted"]:
                    results["failed"] += 1
                    if result["error"]:
                        results["errors"].append({
                            "tender_id": tender_id,
                            "error": result["error"]
                        })
                elif result["openrag_deleted"] and not result["milvus_deleted"]:
                # OpenRAG deleted but Milvus failed - still count as partial success
                    logger.warning(f"⚠️ Tender {tender_id}: OpenRAG deleted but Milvus deletion failed")
                
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({
                    "tender_id": tender_id,
                    "error": str(e)
                })
    
        logger.info(f"📊 Deletion results: {results}")
        return results

    def count_milvus_documents(self) -> int:
        """Get count of documents in Milvus"""
        try:
            from pymilvus import connections, Collection
            connections.connect(host='localhost', port='19530')
            collection = Collection('tender_db')
            collection.load()
            count = collection.num_entities
            logger.info(f"📊 Milvus documents: {count}")
            return count
        except Exception as e:
            logger.error(f"Failed to count Milvus documents: {e}")
            return -1




    def delete_from_milvus_by_tender_id(self, tender_id: int) -> bool:
        """Delete documents from Milvus by tender_id"""
        try:
            from pymilvus import connections, Collection
        
        # Connect to Milvus
            connections.connect(host='localhost', port='19530')
            collection = Collection('tender_db')
            collection.load()
        
        # Query by tender_id in metadata
            expr = f"metadata['tender_id'] == {tender_id}"
            results = collection.query(expr=expr, output_fields=["id"])
        
            if not results:
                logger.info(f"Tender {tender_id} not found in Milvus")
                return True
        
        # Delete by IDs
            ids = [str(r['id']) for r in results]
            collection.delete(expr=f"id in {ids}")
            collection.flush()
        
            logger.info(f"✅ Deleted tender {tender_id} from Milvus ({len(ids)} documents)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete tender {tender_id} from Milvus: {e}")
            return False


    # """
# OpenRAG Client - Wrapper for OpenRAG API
# Handles document ingestion and semantic search against tenders
# """
# import os
# import requests
# import json
# import io
# from typing import List, Dict, Any
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)


# class OpenRAGClient:
#     def __init__(self, base_url: str = None, auth_token: str = None):
#         """Initialize OpenRAG client
        
#         Args:
#             base_url: OpenRAG API base URL (default: uses OPENRAG_URL env var or http://127.0.0.1:8080)
#             auth_token: Optional authentication token (if not provided, uses placeholder)
#         """
#         # Use provided base_url, env variable, or default
#         if base_url is None:
#             base_url = os.getenv("OPENRAG_URL", "http://127.0.0.1:8080")
#         self.base_url = base_url.rstrip('/')
#         print(f"DEBUG: OpenRAGClient initialized with base_url={self.base_url}, env OPENRAG_URL={os.getenv('OPENRAG_URL')}")
#         # Use provided token, default placeholder, or empty for no auth
#         self.auth_token = auth_token or os.getenv("OPENRAG_TOKEN", "sk-openrag-dev")
#         self.partition_name = "tenders"
#         self.headers = self._build_headers()
    
#     def _build_headers(self) -> dict:
#         """Build request headers with authorization"""
#         headers = {}
#         if self.auth_token:
#             headers['Authorization'] = f'Bearer {self.auth_token}'
#         return headers
        
#     def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
#         """Make HTTP request to OpenRAG API"""
#         url = f"{self.base_url}{endpoint}"
#         headers = {**self.headers, **kwargs.get('headers', {})}
#         try:
#             response = requests.request(method, url, headers=headers, timeout=30, **kwargs)
#             response.raise_for_status()
#             return response.json() if response.text else {}
#         except requests.exceptions.RequestException as e:
#             logger.error(f"OpenRAG API error: {e}")
#             raise
    
#     def create_partition(self, partition_name: str = None) -> Dict[str, Any]:
#         """Create a partition for tenders
        
#         Args:
#             partition_name: Name of partition (default: 'tenders')
        
#         Returns:
#             API response
#         """
#         partition_name = partition_name or self.partition_name
#         endpoint = f"/partition/{partition_name}"
#         try:
#             result = self._request('POST', endpoint)
#             logger.info(f"Created partition: {partition_name}")
#             return {"success": True, "partition": partition_name}
#         except requests.exceptions.HTTPException as e:
#             if e.response.status_code == 409:  # Already exists
#                 logger.info(f"Partition {partition_name} already exists")
#                 return {"success": True, "partition": partition_name, "message": "Partition already exists"}
#             raise
    
#     def upload_tender(self, tender_id: str, tender_data: Dict[str, Any], partition_name: str = None) -> Dict[str, Any]:
#         """Upload a single tender as a document
        
#         Args:
#             tender_id: Unique tender ID
#             tender_data: Tender data dictionary
#             partition_name: Target partition (default: 'tenders')
        
#         Returns:
#             API response with task status
#         """
#         partition_name = partition_name or self.partition_name
        
#         # Create text content from tender data
#         content = self._tender_to_text(tender_data)
        
#         # Create metadata
#         metadata = {
#             "tender_id": str(tender_id),
#             "title": tender_data.get('title', 'Untitled Tender'),
#             "reference": tender_data.get('reference', ''),
#             "source": "TUNEPS",
#             "created_at": datetime.utcnow().isoformat(),
#         }
        
#         # Upload via OpenRAG indexer API
#         file_id = f"tender_{tender_id}"
        
#         # Create file-like object
#         file_content = io.BytesIO(content.encode('utf-8'))
#         files = {
#             'file': (f"{file_id}.txt", file_content, 'text/plain')
#         }
#         data = {
#             'metadata': json.dumps(metadata)
#         }
        
#         endpoint = f"/indexer/partition/{partition_name}/file/{file_id}"
#         try:
#             response = requests.post(
#                 f"{self.base_url}{endpoint}",
#                 files=files,
#                 data=data,
#                 headers=self.headers,
#                 timeout=30
#             )
#             response.raise_for_status()
#             logger.info(f"Uploaded tender {tender_id} to OpenRAG")
#             return {"success": True, "tender_id": tender_id, "file_id": file_id}
#         except Exception as e:
#             logger.error(f"Failed to upload tender {tender_id}: {e}")
#             raise
    
#     def index_tenders_batch(self, tenders: List[Dict[str, Any]], partition_name: str = None) -> Dict[str, Any]:
#         """Index multiple tenders
        
#         Args:
#             tenders: List of tender dictionaries
#             partition_name: Target partition (default: 'tenders')
        
#         Returns:
#             Summary of indexing results
#         """
#         partition_name = partition_name or self.partition_name
        
#         # Ensure partition exists
#         self.create_partition(partition_name)
        
#         results = {
#             "total": len(tenders),
#             "successful": 0,
#             "failed": 0,
#             "errors": []
#         }
        
#         for tender in tenders:
#             try:
#                 self.upload_tender(tender.get('id'), tender, partition_name)
#                 results["successful"] += 1
#             except Exception as e:
#                 results["failed"] += 1
#                 results["errors"].append({
#                     "tender_id": tender.get('id'),
#                     "error": str(e)
#                 })
        
#         return results
    
#     def search(self, query: str, top_k: int = 5, partition_name: str = None, 
#                similarity_threshold: float = 0.75) -> Dict[str, Any]:
#         """Perform semantic search across tenders
        
#         Args:
#             query: Search query text
#             top_k: Number of results to return
#             partition_name: Partition to search (default: 'tenders')
#             similarity_threshold: Minimum similarity score (0-1)
        
#         Returns:
#             Search results with matched tenders
#         """
#         partition_name = partition_name or self.partition_name
        
#         params = {
#             "partitions": [partition_name],
#             "text": query,
#             "top_k": top_k,
#             "similarity_threshold": similarity_threshold
#         }
        
#         try:
#             response = requests.get(
#                 f"{self.base_url}/search",
#                 params=params,
#                 headers=self.headers,
#                 timeout=30
#             )
#             response.raise_for_status()
#             results = response.json()
            
#             # Parse results
#             parsed_results = {
#                 "success": True,
#                 "query": query,
#                 "total": len(results.get("results", [])),
#                 "results": []
#             }
            
#             for result in results.get("results", []):
#                 parsed_results["results"].append({
#                     "content": result.get("content", ""),
#                     "score": result.get("similarity_score", 0),
#                     "metadata": result.get("metadata", {})
#                 })
            
#             return parsed_results
            
#         except Exception as e:
#             logger.error(f"Search failed: {e}")
#             raise
    
#     def health_check(self) -> bool:
#         """Check if OpenRAG is healthy"""
#         try:
#             response = requests.get(f"{self.base_url}/health_check", timeout=5)
#             return response.status_code == 200
#         except Exception as e:
#             logger.error(f"OpenRAG health check failed: {e}")
#             return False
    
#     @staticmethod
#     def _tender_to_text(tender_data: Dict[str, Any]) -> str:
#         """Convert tender dictionary to formatted text for indexing
        
#         Args:
#             tender_data: Tender information
        
#         Returns:
#             Formatted text string
#         """
#         lines = [
#             f"Title: {tender_data.get('title', '')}",
#             f"Reference: {tender_data.get('reference', '')}",
#             f"",
#             f"Description:",
#             f"{tender_data.get('description', '')}",
#             f"",
#             f"Details:",
#             f"- Budget: {tender_data.get('budget', 'N/A')}",
#             f"- Location: {tender_data.get('location', 'N/A')}",
#             f"- Category: {tender_data.get('category', 'N/A')}",
#             f"- Start Date: {tender_data.get('start_date', 'N/A')}",
#             f"- End Date: {tender_data.get('end_date', 'N/A')}",
#         ]
#         return "\n".join(lines)
import io
from urllib import response

import os
import requests
import json
from typing import Dict, List, Any, Optional
import logging
logger = logging.getLogger(__name__)
# from openrag.openrag.openrag.core.models import query

class OpenRAGClient:
    def __init__(self, base_url=None, token=None):
        # Use environment variable if base_url not provided
        if base_url is None:
            base_url = os.getenv("OPENRAG_URL", "http://localhost:8080")
        # Use environment variable if token not provided
        if token is None:
            token = os.getenv("OPENRAG_TOKEN", "or-openrag-1234")
        
        self.base_url = base_url
        self.token = token
        print(f"[OpenRAGClient] Initialized with base_url={self.base_url}, token={self.token[:10]}...")
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        self.milvus_initialized = False
        self.milvus_collection = None



    # def _init_milvus(self):
    #     """Initialize Milvus connection for direct operations"""
    #     if self.milvus_initialized:
    #         return
    
    #     try:
    #         from pymilvus import connections, Collection
        
    #     # Your backend is on the host machine, Milvus is exposed on localhost:19530
    #         connections.connect(host='localhost', port='19530')
    #         logger.info("✅ Connected to Milvus at localhost:19530")
        
    #         self.milvus_collection = Collection('tender_db')
    #         self.milvus_collection.load()
    #         self.milvus_initialized = True
    #         logger.info("✅ Milvus collection 'tender_db' loaded successfully")
    #     except Exception as e:
    #         logger.error(f"❌ Failed to connect to Milvus: {e}")
    #     # Don't raise - we can still use OpenRAG for deletion
    #         logger.warning("⚠️ Direct Milvus connection failed, OpenRAG deletion will still work")











    def health_check(self) -> bool:
        """Check if OpenRAG is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/health_check",
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

    # def search(self, query: str, top_k: int = 5, partition_name: str = "tenders", similarity_threshold: float = 0.75) -> Dict:
    #     """Search for relevant documents using semantic search"""
    #     response = requests.post(
    #         f"{self.base_url}/v1/chat/completions",
    #         headers=self.headers,
    #         json={
    #             "messages": [{"role": "user", "content": query}],
    #             "model": "deepseek-v4-flash",
    #             "metadata": {
    #                 "partition": partition_name,
    #                 "top_k": top_k,
    #                 "similarity_threshold": similarity_threshold
    #             }
    #         }
    #     )
    #     return response.json()

    def search(self, query: str, top_k: int = 5, partition_name: str = "tenders", similarity_threshold: float = 0.75) -> Dict:
        """Search for relevant documents using semantic search"""
        # Use the /search endpoint with parameters
        params = {
            "text": query,
            "partitions": partition_name,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold
        }
    
        response = requests.get(
            f"{self.base_url}/search",
            params=params,
            headers=self.headers
        )
        return response.json()








    # def upload_tender(self, tender_id: int, tender_data: Dict) -> Dict:
    #     """Upload/Index a single tender to OpenRAG"""
    #     # Create a text representation using your actual tender fields
    #     content = f"""
    #     Tender Reference: {tender_data.get('reference', 'N/A')}
    #     Title: {tender_data.get('title', 'N/A')}
    #     Buyer: {tender_data.get('buyer', 'N/A')}
    #     Publication Date: {tender_data.get('publication_date', 'N/A')}
    #     Deadline: {tender_data.get('deadline', 'N/A')}
    #     Source: {tender_data.get('source', 'TUNEPS')}
    #     """
    
    #     response = requests.post(
    #         f"{self.base_url}/v1/chat/completions",
    #         headers=self.headers,
    #         json={
    #             "messages": [
    #                 {"role": "user", "content": f"Please index this tender document for searching:\n\n{content}"}
    #             ],
    #             "model": "deepseek-v4-flash",
    #             "metadata": {
    #                 "partition": "tenders",
    #                 "tender_id": tender_id,
    #                 "index_mode": True
    #             }
    #         }
    #     )
    #     return response.json()


    def upload_tender(self, tender_id: int, tender_data: Dict) -> Dict:
        """Upload/Index a single tender to OpenRAG as a file"""
        import io
    
        # Create text content
        content = f"""Tender Reference: {tender_data.get('reference', 'N/A')}
        Title: {tender_data.get('title', 'N/A')}
        Buyer: {tender_data.get('buyer', 'N/A')}
        Publication Date: {tender_data.get('publication_date', 'N/A')}
        Deadline: {tender_data.get('deadline', 'N/A')}
        Source: {tender_data.get('source', 'TUNEPS')}
        """
    
        # Create file-like object
        file_content = io.BytesIO(content.encode('utf-8'))
    
        files = {
            'file': (f"tender_{tender_id}.txt", file_content, 'text/plain')
        }
    
        data = {
            'metadata': json.dumps({
            'tender_id': tender_id,
            'reference': tender_data.get('reference', ''),
            'buyer': tender_data.get('buyer', ''),
            'source': 'TUNEPS'
        })
    }
    
        response = requests.post(
            f"{self.base_url}/indexer/partition/tenders/file/tender_{tender_id}",
            headers={"Authorization": f"Bearer {self.token}"},
            files=files,
            data=data,
            timeout=30
        )
        return response.json()











    def index_tenders_batch(self, tenders: List[Dict]) -> Dict:
        """Submit multiple tenders for indexing (non-blocking)
        
        Submits all documents to OpenRAG and returns immediately with task IDs.
        Does NOT wait for indexing to complete.
        """
        task_ids = []
        failed_count = 0
        
        for i, tender in enumerate(tenders):
            try:
                tender_id = tender.get('id', tender.get('tender_id'))
                if not tender_id:
                    failed_count += 1
                    continue
                
                # Submit to OpenRAG without waiting
                try:
                    result = self._submit_tender_async(tender_id, tender)
                    if result.get('error'):
                        print(f"[batch {i}] Tender {tender_id}: {result.get('error')}")
                        failed_count += 1
                        continue
                        
                    if 'task_status_url' in result:
                        # Extract task_id from URL: /indexer/task/{task_id}
                        task_id = result['task_status_url'].split('/')[-1]
                        task_ids.append({
                            'tender_id': tender_id,
                            'task_id': task_id,
                            'status_url': result['task_status_url']
                        })
                    else:
                        print(f"[batch {i}] Tender {tender_id}: No task_status_url in response: {result}")
                        failed_count += 1
                except Exception as e:
                    print(f"[batch {i}] Error submitting tender {tender_id}: {type(e).__name__}: {e}")
                    failed_count += 1
            except Exception as e:
                print(f"[batch {i}] Error processing tender: {type(e).__name__}: {e}")
                failed_count += 1
        
        return {
            "total": len(tenders),
            "submitted": len(task_ids),
            "failed": failed_count,
            "task_ids": task_ids
        }
    
    def _submit_tender_async(self, tender_id: int, tender_data: Dict) -> Dict:
        """Submit a single tender without waiting for completion"""
        import io
        
        try:
            content = f"""Tender Reference: {tender_data.get('reference', 'N/A')}
        Title: {tender_data.get('title', 'N/A')}
        Buyer: {tender_data.get('buyer', 'N/A')}
        Publication Date: {tender_data.get('publication_date', 'N/A')}
        Deadline: {tender_data.get('deadline', 'N/A')}
        Source: {tender_data.get('source', 'TUNEPS')}
        """
            
            file_content = io.BytesIO(content.encode('utf-8'))
            files = {
                'file': (f"tender_{tender_id}.txt", file_content, 'text/plain')
            }
            data = {
                'metadata': json.dumps({
                    'tender_id': tender_id,
                    'reference': tender_data.get('reference', ''),
                    'buyer': tender_data.get('buyer', ''),
                    'source': 'TUNEPS'
                })
            }
            
            url = f"{self.base_url}/indexer/partition/tenders/file/tender_{tender_id}"
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                files=files,
                data=data,
                timeout=10
            )
            
            if response.status_code >= 400:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
            
            return response.json()
        except requests.exceptions.Timeout:
            return {"error": f"Request timeout for tender_{tender_id}"}
        except requests.exceptions.ConnectionError as e:
            return {"error": f"Connection error: {str(e)}"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {str(e)}"}
    
    def get_task_status(self, task_id: str) -> Dict:
        """Check status of an indexing task"""
        try:
            response = requests.get(
                f"{self.base_url}/indexer/task/{task_id}",
                headers=self.headers,
                timeout=5
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def get_partitions(self) -> List[Dict]:
        """Get all partitions"""
        response = requests.get(
            f"{self.base_url}/partition/",
            headers=self.headers
        )
        return response.json().get("partitions", [])

    # def delete_tender(self, tender_id: int, partition_name: str = "tenders") -> Dict:
    #     """Delete a single tender document from OpenRAG/Milvus
        
    #     Args:
    #         tender_id: Tender ID to delete
    #         partition_name: Partition name (default: 'tenders')
        
    #     Returns:
    #         API response
    #     """
    #     try:
    #         # The file_id is the document ID in OpenRAG
    #         file_id = f"tender_{tender_id}"
    #         url = f"{self.base_url}/indexer/partition/{partition_name}/file/{file_id}"
            
    #         response = requests.delete(
    #             url,
    #             headers={"Authorization": f"Bearer {self.token}"},
    #             timeout=30
    #         )
            
    #         if response.status_code == 404:
    #             # Document not found - consider it already deleted
    #             return {"success": True, "message": f"Document {file_id} already deleted or not found"}
            
    #         response.raise_for_status()
    #         return {"success": True, "message": f"Deleted document {file_id}"}
            
    #     except requests.exceptions.RequestException as e:
    #         logger.error(f"Failed to delete tender {tender_id} from OpenRAG: {e}")
    #         return {"success": False, "error": str(e), "tender_id": tender_id}

    # ============ DELETE USING OPENRAG ONLY ============


    # services/openrag_client.py - Updated delete_tender method

    def delete_tender(self, tender_id: int, partition_name: str = "tenders") -> Dict:
        """Delete a single tender document from Milvus via container (skip OpenRAG)"""
        results = {
            "tender_id": tender_id,
            "openrag_deleted": False,
            "milvus_deleted": False,
            "error": None
        }
    
    # Skip OpenRAG deletion - just delete from Milvus via container
        try:
            logger.info(f"🗑️ Deleting tender {tender_id} from Milvus via container...")
            milvus_success = self.delete_from_milvus_via_container(tender_id)
            results["milvus_deleted"] = milvus_success
            if milvus_success:
                logger.info(f"✅ Deleted tender {tender_id} from Milvus")
            # Mark as success even though we skipped OpenRAG
                results["openrag_deleted"] = True
            else:
                logger.warning(f"⚠️ Failed to delete tender {tender_id} from Milvus")
        except Exception as e:
            logger.error(f"Error deleting from Milvus: {e}")
            results["milvus_deleted"] = False
            results["error"] = f"Milvus error: {str(e)}"
    
        return results















    # def delete_tender(self, tender_id: int, partition_name: str = "tenders") -> Dict:
    #     """Delete a single tender document from both OpenRAG and Milvus"""
    #     results = {
    #         "tender_id": tender_id,
    #         "openrag_deleted": False,
    #         "milvus_deleted": False,
    #         "error": None
    #     }
    
    # # 1. Delete from OpenRAG
    #     try:
    #         file_id = f"tender_{tender_id}"
    #         url = f"{self.base_url}/indexer/partition/{partition_name}/file/{file_id}"
        
    #         logger.info(f"🗑️ DELETE from OpenRAG: {url}")
        
    #         response = requests.delete(
    #             url,
    #             headers={"Authorization": f"Bearer {self.token}"},
    #             timeout=30
    #         )
        
    #         if response.status_code in [200, 204]:
    #             results["openrag_deleted"] = True
    #             logger.info(f"✅ Deleted tender {tender_id} from OpenRAG")
    #         elif response.status_code == 404:
    #             results["openrag_deleted"] = True
    #             logger.info(f"ℹ️ Tender {tender_id} already deleted from OpenRAG")
    #         else:
    #             results["error"] = f"OpenRAG HTTP {response.status_code}"
    #             logger.warning(f"⚠️ OpenRAG deletion returned: {response.status_code}")
            
    #     except Exception as e:
    #         logger.error(f"Error deleting from OpenRAG: {e}")
    #         results["error"] = str(e)
    
    # # 2. Delete from Milvus via OpenRAG container (if OpenRAG deletion succeeded)
    #     if results["openrag_deleted"]:
    #         try:
    #             logger.info(f"🗑️ Deleting tender {tender_id} from Milvus via container...")
    #             milvus_success = self.delete_from_milvus_via_container(tender_id)
    #             results["milvus_deleted"] = milvus_success
    #             if milvus_success:
    #                 logger.info(f"✅ Deleted tender {tender_id} from Milvus")
    #             else:
    #                 logger.warning(f"⚠️ Failed to delete tender {tender_id} from Milvus")
    #         except Exception as e:
    #             logger.error(f"Error deleting from Milvus: {e}")
    #             results["milvus_deleted"] = False
    #             if not results["error"]:
    #                 results["error"] = f"Milvus error: {str(e)}"
    
    # # ✅ This return should be OUTSIDE the if block
    #     return results

    def delete_tenders_batch(self, tender_ids: List[int], partition_name: str = "tenders") -> Dict:
        """Delete multiple tenders in smaller batches"""
        results = {
            "total": len(tender_ids),
            "openrag_successful": 0,
            "milvus_successful": 0,
            "failed": 0,
            "errors": []
        }
    
    # Process in batches of 10 to avoid overwhelming the system
        batch_size = 10
        for i in range(0, len(tender_ids), batch_size):
            batch = tender_ids[i:i+batch_size]
            print(f"🗑️ Processing batch {i//batch_size + 1}: {len(batch)} tenders")
        
            for tender_id in batch:
                try:
                    result = self.delete_tender(tender_id, partition_name)
                    if result["openrag_deleted"]:
                        results["openrag_successful"] += 1
                    if result["milvus_deleted"]:
                        results["milvus_successful"] += 1
                    if not result["openrag_deleted"] and not result["milvus_deleted"]:
                        results["failed"] += 1
                        if result["error"]:
                            results["errors"].append({
                                "tender_id": tender_id,
                                "error": result["error"]
                            })
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append({
                        "tender_id": tender_id,
                        "error": str(e)
                    })
        
        # Wait 2 seconds between batches
            if i + batch_size < len(tender_ids):
                import time
                time.sleep(2)
    
        return results

    def count_milvus_documents(self) -> int:
        """Get count of documents in Milvus"""
        hosts_to_try = ['milvus', 'localhost']
        for host in hosts_to_try:
            try:
                from pymilvus import connections, Collection
                connections.connect(host=host, port='19530')
                collection = Collection('tender_db')
                collection.load()
                count = collection.num_entities
                logger.info(f"📊 Milvus documents: {count} (connected via {host})")
                return count
            except Exception as e:
                logger.warning(f"Could not connect to Milvus via {host}: {e}")
                continue
        logger.error(f"Failed to count Milvus documents on any host")
        return -1




    def delete_from_milvus_by_tender_id(self, tender_id: int) -> bool:
        """Delete documents from Milvus by tender_id"""
        try:
            from pymilvus import connections, Collection
        
        # Connect to Milvus
            connections.connect(host='localhost', port='19530')
            collection = Collection('tender_db')
            collection.load()
        
        # Query by tender_id in metadata
            expr = f"metadata['tender_id'] == {tender_id}"
            results = collection.query(expr=expr, output_fields=["id"])
        
            if not results:
                logger.info(f"Tender {tender_id} not found in Milvus")
                return True
        
        # Delete by IDs
            ids = [str(r['id']) for r in results]
            collection.delete(expr=f"id in {ids}")
            collection.flush()
        
            logger.info(f"✅ Deleted tender {tender_id} from Milvus ({len(ids)} documents)")
            return True
        
        except Exception as e:
            logger.error(f"Failed to delete tender {tender_id} from Milvus: {e}")
            return False


#     def delete_from_milvus_via_container(self, tender_id: int) -> bool:
#         """
#     Delete a document from Milvus by executing Python inside the OpenRAG container.
#     This works because the OpenRAG container is on the same Docker network as Milvus.
#     """
#         try:
#             import subprocess
#             import tempfile
#             import os
        
#         # Create a Python script WITHOUT f-strings - use string concatenation
#             script_content = '''
# from pymilvus import connections, Collection

# try:
#     connections.connect(host="milvus", port="19530")
#     collection = Collection("tender_db")
#     collection.load()
    
#     expr = "tender_id == " + str({tender_id})
#     results = collection.query(expr=expr, output_fields=["_id"])
    
#     if not results:
#         print("NOT_FOUND")
#     else:
#         ids = [r["_id"] for r in results]
#         collection.delete(expr="_id in " + str(ids))
#         collection.flush()
#         print("DELETED")
#         print("Removed " + str(len(ids)) + " documents")
        
# except Exception as e:
#     print("ERROR: " + str(e))
# '''
        
#         # Insert the tender_id
#             script_content = script_content.format(tender_id=tender_id)
        
#         # Debug: print the script
#             # print(f"Script to execute:\n{script_content}")
        
#         # Write the script to a temporary file
#             with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
#                 f.write(script_content)
#                 script_path = f.name
        
#             try:
#             # Copy the script to the OpenRAG container
#                 subprocess.run([
#                     "docker", "cp",
#                     script_path,
#                     "compose-openrag-cpu-1:/tmp/delete_milvus.py"
#                 ], capture_output=True, check=True)
            
#             # Execute the script inside the OpenRAG container
#                 result = subprocess.run([
#                     "docker", "exec", "compose-openrag-cpu-1",
#                     "bash", "-c",
#                     "source /app/.venv/bin/activate && python3 /tmp/delete_milvus.py"
#                 ], capture_output=True, text=True, timeout=30)
            
#                 # print(f"Container STDOUT: {result.stdout}")
#                 if result.stderr:
#                     print(f"Container STDERR: {result.stderr}")
            
#             # Check the result
#                 if "DELETED" in result.stdout:
#                     logger.info(f"✅ Deleted tender {tender_id} from Milvus via container")
#                     return True
#                 elif "NOT_FOUND" in result.stdout:
#                     logger.info(f"ℹ️ Tender {tender_id} not found in Milvus")
#                     return True
#                 else:
#                     logger.error(f"❌ Milvus deletion failed: {result.stdout}")
#                     return False
                
#             finally:
#             # Clean up the temporary file
#                 try:
#                     os.unlink(script_path)
#                 except:
#                     pass
#                 try:
#                     subprocess.run([
#                         "docker", "exec", "compose-openrag-cpu-1",
#                         "rm", "-f", "/tmp/delete_milvus.py"
#                     ], capture_output=True)
#                 except:
#                     pass
            
#         except subprocess.TimeoutExpired:
#             logger.error(f"❌ Milvus deletion timed out for tender {tender_id}")
#             return False
#         except Exception as e:
#             logger.error(f"Failed to delete tender {tender_id} from Milvus via container: {e}")
#             return False

    def delete_from_milvus_via_container(self, tender_id: int) -> bool:
        """
        Delete a document from Milvus by executing Python inside the OpenRAG container.
        """
        try:
            import subprocess
            import tempfile
            import os
        
            container_name = "compose-openrag-cpu-1"
        
        # ✅ ÉTAPE 1 : Installer pymilvus dans le conteneur (si pas déjà installé)
            print(f"📦 Checking/installing pymilvus in container...")
            install_result = subprocess.run([
                "docker", "exec", container_name,
                "bash", "-c",
                "pip install pymilvus -q 2>/dev/null || echo 'pymilvus already installed'"
            ], capture_output=True, text=True, timeout=60)
        
            if install_result.returncode != 0:
                print(f"⚠️ Could not install pymilvus, but continuing...")
            else:
                print(f"✅ pymilvus ready")
        
        # ✅ ÉTAPE 2 : Créer le script Python
            script_content = f"""
from pymilvus import connections, Collection

try:
    connections.connect(host="milvus", port="19530")
    collection = Collection("tender_db")
    collection.load()
    
    expr = "tender_id == {tender_id}"
    results = collection.query(expr=expr, output_fields=["_id"])
    
    if not results:
        print("NOT_FOUND")
    else:
        ids = [r["_id"] for r in results]
        collection.delete(expr="_id in " + str(ids))
        collection.flush()
        print("DELETED")
        print("Removed " + str(len(ids)) + " documents")
        
except Exception as e:
    print("ERROR: " + str(e))
"""
        
        # Écrire le script dans un fichier temporaire LOCAL
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(script_content)
                script_path = f.name
        
            print(f"📝 Script created locally: {script_path}")
        
            try:
            # ✅ ÉTAPE 3 : Copier le script vers le conteneur
                cp_result = subprocess.run([
                    "docker", "cp",
                    script_path,
                    f"{container_name}:/tmp/delete_milvus.py"
                ], capture_output=True, text=True)
            
                if cp_result.returncode != 0:
                    print(f"❌ Docker cp failed: {cp_result.stderr}")
                    return False
            
                print(f"✅ Script copied to container: {container_name}:/tmp/delete_milvus.py")
            
            # ✅ ÉTAPE 4 : Exécuter le script
                result = subprocess.run([
                    "docker", "exec", container_name,
                    "bash", "-c",
                    "python3 /tmp/delete_milvus.py"
                ], capture_output=True, text=True, timeout=30)
            
                if result.stderr:
                    print(f"Container STDERR: {result.stderr}")
            
                print(f"Container STDOUT: {result.stdout}")
            
                if "DELETED" in result.stdout:
                    logger.info(f"✅ Deleted tender {tender_id} from Milvus via container")
                    return True
                elif "NOT_FOUND" in result.stdout:
                    logger.info(f"ℹ️ Tender {tender_id} not found in Milvus")
                    return True
                else:
                    logger.error(f"❌ Milvus deletion failed: {result.stdout}")
                    return False
            
            finally:
            # Nettoyer
                try:
                    os.unlink(script_path)
                except:
                    pass
                try:
                    subprocess.run([
                        "docker", "exec", container_name,
                        "rm", "-f", "/tmp/delete_milvus.py"
                    ], capture_output=True)
                except:
                    pass
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Milvus deletion timed out for tender {tender_id}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete tender {tender_id} from Milvus via container: {e}")
            return False
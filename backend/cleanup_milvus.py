import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from services.openrag_client import OpenRAGClient
from datetime import datetime
import logging
import json
import subprocess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_expired_from_milvus():
    """Delete expired tenders directly from Milvus by checking document metadata"""
    
    print("=" * 60)
    print(f"🔍 Starting cleanup of expired tenders directly from Milvus")
    print("=" * 60)
    
    with app.app_context():
        client = OpenRAGClient()
        current_date = datetime.now()
        
        try:
            container_name = "compose-openrag-cpu-1"
            
            # Query all documents from Milvus with their metadata
            # Using pk which is the primary key in your schema
            script = '''
from pymilvus import connections, Collection
import json

try:
    connections.connect(host="milvus", port="19530")
    collection = Collection("tender_db")
    collection.load()
    
    # Get all documents - use pk instead of id
    results = collection.query(
        expr="pk >= 0",
        output_fields=["pk", "tender_id", "metadata"],
        limit=10000  # Get up to 10000 documents
    )
    
    # Print as JSON for parsing
    print(json.dumps(results))
    
except Exception as e:
    print(f"ERROR: {str(e)}")
'''
            
            # Execute script in container
            result = subprocess.run([
                "docker", "exec", container_name,
                "bash", "-c",
                f"source /app/.venv/bin/activate && python3 -c '{script}'"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                print(f"❌ Failed to query Milvus: {result.stderr}")
                print(f"Output: {result.stdout}")
                return
            
            if not result.stdout or result.stdout.strip() == '':
                print("❌ No output from Milvus query")
                return
            
            try:
                documents = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse JSON: {e}")
                print(f"Raw output: {result.stdout[:500]}...")
                return
            
            print(f"📊 Found {len(documents)} documents in Milvus")
            
            if len(documents) == 0:
                print("✅ No documents found in Milvus!")
                return
            
            expired_docs = []
            
            for doc in documents:
                # Get metadata - could be in different fields
                metadata = doc.get('metadata', {})
                
                # If metadata is a string, parse it as JSON
                if isinstance(metadata, str):
                    try:
                        metadata = json.loads(metadata)
                    except:
                        metadata = {}
                
                # Try different field names for tender_id and deadline
                tender_id = doc.get('tender_id') or metadata.get('tender_id')
                deadline = doc.get('deadline') or metadata.get('deadline')
                
                # If we found both, check if expired
                if tender_id and deadline:
                    try:
                        # Parse deadline
                        deadline_date = None
                        deadline_str = str(deadline)
                        
                        # Try different formats
                        formats = [
                            '%Y-%m-%d',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S',
                            '%Y-%m-%dT%H:%M:%SZ',
                            '%Y-%m-%d %H:%M:%S.%f',
                            '%d/%m/%Y'
                        ]
                        
                        for fmt in formats:
                            try:
                                deadline_date = datetime.strptime(deadline_str, fmt)
                                break
                            except:
                                continue
                        
                        # If ISO format with timezone
                        if not deadline_date:
                            try:
                                deadline_date = datetime.fromisoformat(deadline_str.replace('Z', '+00:00'))
                            except:
                                pass
                        
                        if deadline_date and deadline_date < current_date:
                            expired_docs.append({
                                'pk': doc.get('pk'),
                                'tender_id': tender_id,
                                'deadline': deadline,
                                'metadata': metadata
                            })
                            print(f"⏰ Found expired: tender_id={tender_id}, deadline={deadline}")
                            
                    except Exception as e:
                        print(f"⚠️ Could not parse date for tender {tender_id}: {e}")
                else:
                    # Debug: show what we found
                    if not tender_id:
                        print(f"ℹ️ Document has no tender_id: {doc.get('pk')}")
                    if not deadline:
                        print(f"ℹ️ Document has no deadline: {doc.get('pk')}")
            
            print(f"\n📊 Found {len(expired_docs)} expired documents in Milvus")
            
            if not expired_docs:
                print("✅ No expired documents found in Milvus!")
                return
            
            # Delete each expired document
            success_count = 0
            failed_docs = []
            
            print("\n🗑️ Deleting expired tenders from Milvus...")
            for doc in expired_docs:
                try:
                    tender_id = doc['tender_id']
                    print(f"🗑️ Deleting tender {tender_id} (pk: {doc.get('pk')})...")
                    
                    result = client.delete_from_milvus_via_container(tender_id)
                    
                    if result:
                        success_count += 1
                        print(f"✅ Deleted tender {tender_id}")
                    else:
                        failed_docs.append(tender_id)
                        print(f"❌ Failed to delete tender {tender_id}")
                        
                except Exception as e:
                    failed_docs.append(tender_id)
                    print(f"❌ Error deleting tender {tender_id}: {e}")
            
            print(f"\n📊 Summary:")
            print(f"  - Found: {len(expired_docs)} expired documents")
            print(f"  - Deleted: {success_count}")
            print(f"  - Failed: {len(failed_docs)}")
            
            if failed_docs:
                print(f"  - Failed IDs: {failed_docs}")
            
            # Show final count
            final_script = '''
from pymilvus import connections, Collection
connections.connect(host="milvus", port="19530")
collection = Collection("tender_db")
collection.load()
print(collection.num_entities)
'''
            final_result = subprocess.run([
                "docker", "exec", container_name,
                "bash", "-c",
                f"source /app/.venv/bin/activate && python3 -c '{final_script}'"
            ], capture_output=True, text=True, timeout=30)
            
            if final_result.stdout.strip():
                print(f"📊 Milvus now has {final_result.stdout.strip()} documents")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    cleanup_expired_from_milvus()
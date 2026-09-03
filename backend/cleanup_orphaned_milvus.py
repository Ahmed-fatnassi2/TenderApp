import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from services.openrag_client import OpenRAGClient
from models.tender import Tender
from database import db
import logging
import subprocess
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_orphaned_milvus():
    """Delete Milvus documents that don't exist in PostgreSQL"""
    
    print("🔍 Checking for orphaned Milvus documents...")
    
    with app.app_context():
        client = OpenRAGClient()
        
        # Get all tender IDs from PostgreSQL
        db_tender_ids = set(t.id for t in Tender.query.all())
        print(f"📊 PostgreSQL has {len(db_tender_ids)} tenders")
        
        # Get all tender_ids from Milvus using the container
        script = '''
from pymilvus import connections, Collection
import json
connections.connect(host="milvus", port="19530")
col = Collection("tender_db")
col.load()
results = col.query(expr="", output_fields=["tender_id"], limit=10000)
tender_ids = [str(r.get("tender_id")) for r in results if r.get("tender_id")]
print(json.dumps(tender_ids))
'''
        
        cmd = [
            "docker", "exec", "compose-openrag-cpu-1",
            "bash", "-c",
            f"source /app/.venv/bin/activate && python3 -c '{script}'"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Failed to get Milvus data: {result.stderr}")
            return
        
        try:
            milvus_tender_ids = set(json.loads(result.stdout))
            print(f"📊 Milvus has {len(milvus_tender_ids)} documents")
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse Milvus data: {e}")
            print(f"Raw output: {result.stdout[:200]}")
            return
        
        # Find orphaned documents (in Milvus but not in PostgreSQL)
        orphaned_ids = milvus_tender_ids - set(str(tid) for tid in db_tender_ids)
        print(f"📊 Found {len(orphaned_ids)} orphaned documents in Milvus")
        
        if not orphaned_ids:
            print("✅ No orphaned documents found!")
            return
        
        # Delete orphaned documents
        print("\n🗑️ Deleting orphaned documents from Milvus...")
        success_count = 0
        for tender_id in orphaned_ids:
            try:
                result = client.delete_from_milvus_via_container(int(tender_id))
                if result:
                    success_count += 1
                    print(f"✅ Deleted orphaned tender {tender_id}")
                else:
                    print(f"❌ Failed to delete orphaned tender {tender_id}")
            except Exception as e:
                print(f"❌ Error deleting tender {tender_id}: {e}")
        
        print(f"\n📊 Summary: Deleted {success_count}/{len(orphaned_ids)} orphaned documents from Milvus")

if __name__ == "__main__":
    cleanup_orphaned_milvus()

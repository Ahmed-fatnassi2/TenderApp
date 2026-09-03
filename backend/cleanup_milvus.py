import sys
import os

# Add the backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from services.openrag_client import OpenRAGClient
from models.tender import Tender
from database import db
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cleanup_expired_from_milvus():
    """Delete all expired tenders from Milvus"""
    
    print("🔍 Starting cleanup of expired tenders from Milvus...")
    
    with app.app_context():
        client = OpenRAGClient()
        current_date = datetime.now()
        expired_ids = []
        
        # Find expired tenders
        tenders = Tender.query.all()
        print(f"📊 Found {len(tenders)} total tenders in PostgreSQL")
        
        for t in tenders:
            if t.deadline:
                try:
                    deadline_str = str(t.deadline)
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S.%f']:
                        try:
                            deadline_date = datetime.strptime(deadline_str, fmt)
                            if deadline_date < current_date:
                                expired_ids.append(t.id)
                                print(f"⏰ Found expired tender: {t.id} - {t.reference} (deadline: {t.deadline})")
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"⚠️ Could not parse deadline for tender {t.id}: {e}")
                    continue
        
        print(f"\n📊 Found {len(expired_ids)} expired tenders in PostgreSQL")
        
        if not expired_ids:
            print("✅ No expired tenders found!")
            return
        
        # Delete each from Milvus
        success_count = 0
        failed_tenders = []
        
        print("\n🗑️ Deleting expired tenders from Milvus...")
        for tid in expired_ids:
            try:
                result = client.delete_from_milvus_via_container(tid)
                if result:
                    success_count += 1
                    print(f"✅ Deleted tender {tid} from Milvus")
                else:
                    failed_tenders.append(tid)
                    print(f"❌ Failed to delete tender {tid}")
            except Exception as e:
                failed_tenders.append(tid)
                print(f"❌ Error deleting tender {tid}: {e}")
        
        print(f"\n📊 Summary: Deleted {success_count}/{len(expired_ids)} expired tenders from Milvus")
        
        if failed_tenders:
            print(f"⚠️ Failed to delete: {failed_tenders}")
        
        # Also check Milvus count if possible
        try:
            count = client.count_milvus_documents()
            if count >= 0:
                print(f"📊 Milvus now has {count} documents")
        except:
            pass

if __name__ == "__main__":
    cleanup_expired_from_milvus()

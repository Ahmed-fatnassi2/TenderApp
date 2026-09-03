from flask import Blueprint, request, jsonify
from services.openrag_client import OpenRAGClient
import os
# Add these imports at the top of openrag_routes.py
import logging
from services.scraper import TUNEPSListingScraper  # This import is missing!

# Initialize logger
logger = logging.getLogger(__name__)
openrag_bp = Blueprint('openrag', __name__, url_prefix='/api/openrag')

# Debug: Print environment variables on module load
print(f"[openrag_routes] OPENRAG_URL env var: {os.getenv('OPENRAG_URL')}")

def get_client():
    """Get OpenRAGClient instance with proper environment configuration"""
    openrag_url = os.getenv('OPENRAG_URL')
    print(f"[get_client] Creating OpenRAGClient with OPENRAG_URL={openrag_url}")
    return OpenRAGClient()

@openrag_bp.route('/health', methods=['GET'])
def health():
    """Check OpenRAG health status"""
    try:
        client = get_client()
        is_healthy = client.health_check()
        return jsonify({
            "success": True,
            "healthy": is_healthy,
            "status": "connected" if is_healthy else "disconnected"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@openrag_bp.route('/search', methods=['POST'])
def search():
    """Search for relevant documents using semantic search"""
    try:
        client = get_client()
        data = request.get_json()
        query = data.get('query')
        top_k = data.get('top_k', 5)
        threshold = data.get('similarity_threshold', 0.75)
        partition = data.get('partition', 'tenders')
        
        if not query:
            return jsonify({"success": False, "error": "Query required"}), 400
        
        result = client.search(query, top_k=top_k, partition_name=partition, similarity_threshold=threshold)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@openrag_bp.route('/index-tender', methods=['POST'])
def index_tender():
    """Index a single tender"""
    try:
        from models import Tender
        client = get_client()
        data = request.get_json()
        tender_id = data.get('tender_id')
        
        if not tender_id:
            return jsonify({"success": False, "error": "tender_id required"}), 400
        
        tender = Tender.query.get(tender_id)
        if not tender:
            return jsonify({"success": False, "error": "Tender not found"}), 404
        
        result = client.upload_tender(tender_id, tender.to_dict())
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@openrag_bp.route('/index-all', methods=['POST'])
def index_all():
    """Submit all tenders for indexing (non-blocking)
    
    Returns immediately with task IDs. Check /api/openrag/batch-status to monitor progress.
    """
    try:
        from models import Tender
        client = get_client()
        tenders = Tender.query.all()
        
        if not tenders:
            return jsonify({
                "success": True,
                "message": "No tenders to index",
                "data": {"total": 0, "submitted": 0, "failed": 0, "task_ids": []}
            })
        
        tender_list = [t.to_dict() for t in tenders]
        result = client.index_tenders_batch(tender_list)
        
        return jsonify({
            "success": result['failed'] < len(tenders),  # Success if most submitted
            "message": f"Submitted {result['submitted']}/{result['total']} tenders for indexing",
            "data": result
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@openrag_bp.route('/batch-status/<task_id>', methods=['GET'])
def batch_status(task_id):
    """Check status of a single indexing task"""
    try:
        client = get_client()
        status = client.get_task_status(task_id)
        return jsonify({"success": True, "data": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    









@openrag_bp.route('/scrape-and-index', methods=['POST'])
def scrape_and_index():
    """Scrape new tenders and automatically index them"""
    try:
        logger.info("=" * 60)
        logger.info("Starting scrape and index operation")
        
        from app import db
        from models import Tender
        
        # Scrape new tenders
        scraper = TUNEPSListingScraper()
        scrape_result = scraper.scrape_and_save(db, Tender)
        
        new_count = scrape_result.get('new', 0)
        duplicate_count = scrape_result.get('duplicates', 0)
        total_count = scrape_result.get('total', 0)
        new_tender_ids = scrape_result.get('new_tender_ids', [])
        
        indexed_count = 0
        failed_count = 0
        indexing_results = []
        
        if new_count > 0 and new_tender_ids:
            logger.info(f"📊 Indexing {len(new_tender_ids)} new tenders")
            
            # Get the OpenRAG client
            client = get_client()
            
            # Get the new tenders from database
            tenders = Tender.query.filter(Tender.id.in_(new_tender_ids)).all()
            
            # Convert tenders to dict list (same format as index-all)
            tender_list = [t.to_dict() for t in tenders]
            
            # Use the exact same method as index-all - index_tenders_batch
            # This is the working method that submits all tenders for indexing
            result = client.index_tenders_batch(tender_list)
            
            logger.info(f"📊 Batch indexing result: {result}")
            
            # Process the result
            if result:
                submitted = result.get('submitted', 0)
                failed = result.get('failed', 0)
                task_ids = result.get('task_ids', [])
                
                indexed_count = submitted
                failed_count = failed
                
                # Build indexing results
                for i, tender in enumerate(tenders):
                    if i < submitted:
                        status = "success"
                        task_id = task_ids[i] if i < len(task_ids) else None
                    else:
                        status = "failed"
                        task_id = None
                    
                    indexing_results.append({
                        "tender_id": tender.id,
                        "reference": tender.reference,
                        "status": status,
                        "task_id": task_id
                    })
                
                logger.info(f"✅ Indexing submitted: {indexed_count} successful, {failed_count} failed")
                
                # If there are task_ids, we can optionally check their status
                if task_ids:
                    logger.info(f"📋 Task IDs: {task_ids}")
                    
            else:
                logger.warning("No result from index_tenders_batch")
                failed_count = new_count
                for tender in tenders:
                    indexing_results.append({
                        "tender_id": tender.id,
                        "reference": tender.reference,
                        "status": "failed",
                        "error": "No response from indexing service"
                    })
        
        return jsonify({
            "success": True,
            "message": f"Scraped {new_count} new tenders. Submitted {indexed_count} for indexing, {failed_count} failed.",
            "data": {
                "scraped": {
                    "new": new_count,
                    "duplicates": duplicate_count,
                    "total": total_count
                },
                "indexing": {
                    "total": new_count,
                    "successful": indexed_count,
                    "failed": failed_count,
                    "details": indexing_results
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Scrape and index failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500  
# # # routes/scraper_routes.py
# # from flask import Blueprint, request, jsonify
# # from services.scraper_manager import ScraperManager
# # import logging

# # scraper_bp = Blueprint('scraper', __name__, url_prefix='/api/scrapers')
# # logger = logging.getLogger(__name__)

# # @scraper_bp.route('/sources', methods=['GET'])
# # def get_sources():
# #     """Get all scraper sources"""
# #     try:
# #         sources = ScraperManager.get_all_sources()
# #         return jsonify({
# #             'success': True,
# #             'sources': sources
# #         })
# #     except Exception as e:
# #         logger.error(f"Error getting sources: {e}")
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/sources', methods=['POST'])
# # def create_source():
# #     """Create a new scraper source"""
# #     try:
# #         data = request.get_json()
# #         result = ScraperManager.create_source(data)
        
# #         if result.get('success'):
# #             return jsonify(result), 201
# #         else:
# #             return jsonify(result), 400
            
# #     except Exception as e:
# #         logger.error(f"Error creating source: {e}")
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/sources/<int:source_id>', methods=['GET'])
# # def get_source(source_id):
# #     """Get a specific source"""
# #     try:
# #         source = ScraperManager.get_source(source_id)
# #         if source:
# #             return jsonify({'success': True, 'source': source})
# #         else:
# #             return jsonify({'success': False, 'error': 'Source not found'}), 404
            
# #     except Exception as e:
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/sources/<int:source_id>', methods=['DELETE'])
# # def delete_source(source_id):
# #     """Delete a source"""
# #     try:
# #         result = ScraperManager.delete_source(source_id)
        
# #         if result.get('success'):
# #             return jsonify(result)
# #         else:
# #             return jsonify(result), 400
            
# #     except Exception as e:
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/sources/<int:source_id>/scrape', methods=['POST'])
# # def scrape_source(source_id):
# #     """Scrape a source"""
# #     try:
# #         result = ScraperManager.scrape_source(source_id)
        
# #         if result.get('success'):
# #             return jsonify(result)
# #         else:
# #             return jsonify(result), 400
            
# #     except Exception as e:
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/test', methods=['POST'])
# # def test_source():
# #     """Test a scraper configuration"""
# #     try:
# #         data = request.get_json()
# #         result = ScraperManager.test_source(data)
# #         return jsonify(result)
        
# #     except Exception as e:
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/available-sources', methods=['GET'])
# # def get_available_sources():
# #     """Get list of pre-configured available sources"""
# #     try:
# #         # Pre-configured sources
# #         available = [
# #             {
# #                 'name': 'TUNEPS',
# #                 'display_name': 'TUNEPS - Tunisian Government Procurement',
# #                 'description': 'Official Tunisian government procurement portal',
# #                 'icon': '🏛️',
# #                 'type': 'api',
# #                 'preconfigured': True
# #             },
# #             # You can add more pre-configured sources here
# #         ]
# #         return jsonify({
# #             'success': True,
# #             'available_sources': available
# #         })
# #     except Exception as e:
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/sources/<int:source_id>/scrape-and-index', methods=['POST'])
# # def scrape_and_index_source(source_id):
# #     """Scrape a source and index the new tenders"""
# #     try:
# #         from services.openrag_client import OpenRAGClient
        
# #         # First, scrape
# #         result = ScraperManager.scrape_source(source_id)
        
# #         if not result.get('success'):
# #             return jsonify(result), 400
        
# #         # If there are new tenders, index them
# #         if result.get('data', {}).get('new', 0) > 0:
# #             new_tender_ids = result.get('data', {}).get('new_tender_ids', [])
# #             if new_tender_ids:
# #                 from models.tender import Tender
# #                 new_tenders = Tender.query.filter(
# #                     Tender.id.in_(new_tender_ids)
# #                 ).all()
                
# #                 openrag_client = OpenRAGClient()
# #                 tender_dicts = [t.to_dict() for t in new_tenders]
# #                 index_result = openrag_client.index_tenders_batch(tender_dicts)
                
# #                 result['data']['indexing'] = index_result
        
# #         return jsonify(result)
        
# #     except Exception as e:
# #         logger.error(f"Scrape and index error: {e}")
# #         return jsonify({'success': False, 'error': str(e)}), 500

# # @scraper_bp.route('/scrape-all-and-index', methods=['POST'])
# # def scrape_all_and_index():
# #     """Scrape all sources and index new tenders"""
# #     try:
# #         from services.openrag_client import OpenRAGClient
# #         from models.scraper_config import ScraperConfig
        
# #         sources = ScraperConfig.query.filter_by(is_active=True).all()
# #         results = {}
# #         total_new = 0
# #         all_new_tender_ids = []
        
# #         for source in sources:
# #             result = ScraperManager.scrape_source(source.id)
# #             results[source.id] = result
            
# #             if result.get('success'):
# #                 new_tender_ids = result.get('data', {}).get('new_tender_ids', [])
# #                 all_new_tender_ids.extend(new_tender_ids)
# #                 total_new += result.get('data', {}).get('new', 0)
        
# #         # Index all new tenders
# #         if all_new_tender_ids:
# #             from models.tender import Tender
# #             new_tenders = Tender.query.filter(
# #                 Tender.id.in_(all_new_tender_ids)
# #             ).all()
            
# #             openrag_client = OpenRAGClient()
# #             tender_dicts = [t.to_dict() for t in new_tenders]
# #             index_result = openrag_client.index_tenders_batch(tender_dicts)
            
# #             return jsonify({
# #                 'success': True,
# #                 'message': f'Scraped {total_new} new tenders from {len(sources)} sources and indexed them',
# #                 'data': {
# #                     'total_new': total_new,
# #                     'sources': results,
# #                     'indexing': index_result
# #                 }
# #             })
        
# #         return jsonify({
# #             'success': True,
# #             'message': f'Scraped {total_new} new tenders from {len(sources)} sources',
# #             'data': {
# #                 'total_new': total_new,
# #                 'sources': results
# #             }
# #         })
        
# #     except Exception as e:
# #         logger.error(f"Scrape all and index error: {e}")
# #         return jsonify({'success': False, 'error': str(e)}), 500


# # routes/scraper_routes.py - ADD THESE ENDPOINTS
# from flask import Blueprint, request, jsonify
# from services.scraper_manager import ScraperManager
# import logging

# scraper_bp = Blueprint('scraper', __name__, url_prefix='/api/scrapers')
# logger = logging.getLogger(__name__)

# @scraper_bp.route('/sources', methods=['GET'])
# def get_sources():
#     """Get all scraper sources"""
#     try:
#         sources = ScraperManager.get_all_sources()
#         return jsonify({
#             'success': True,
#             'sources': sources
#         })
#     except Exception as e:
#         logger.error(f"Error getting sources: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/sources', methods=['POST'])
# def create_source():
#     """Create a new scraper source"""
#     try:
#         data = request.get_json()
#         result = ScraperManager.create_source(data)
        
#         if result.get('success'):
#             return jsonify(result), 201
#         else:
#             return jsonify(result), 400
            
#     except Exception as e:
#         logger.error(f"Error creating source: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/sources/<int:source_id>', methods=['GET'])
# def get_source(source_id):
#     """Get a specific source"""
#     try:
#         source = ScraperManager.get_source(source_id)
#         if source:
#             return jsonify({'success': True, 'source': source})
#         else:
#             return jsonify({'success': False, 'error': 'Source not found'}), 404
            
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/sources/<int:source_id>', methods=['DELETE'])
# def delete_source(source_id):
#     """Delete a source"""
#     try:
#         result = ScraperManager.delete_source(source_id)
        
#         if result.get('success'):
#             return jsonify(result)
#         else:
#             return jsonify(result), 400
            
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/sources/<int:source_id>/scrape', methods=['POST'])
# def scrape_source(source_id):
#     """Scrape a source"""
#     try:
#         result = ScraperManager.scrape_source(source_id)
        
#         if result.get('success'):
#             return jsonify(result)
#         else:
#             return jsonify(result), 400
            
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

# # ============ NEW: Scrape and Index Endpoints ============

# @scraper_bp.route('/sources/<int:source_id>/scrape-and-index', methods=['POST'])
# def scrape_and_index_source(source_id):
#     """Scrape a source and index the new tenders in OpenRAG"""
#     try:
#         from services.openrag_client import OpenRAGClient
#         from models.tender import Tender
        
#         # First, scrape
#         result = ScraperManager.scrape_source(source_id)
        
#         if not result.get('success'):
#             return jsonify(result), 400
        
#         # If there are new tenders, index them
#         data = result.get('data', {})
#         new_count = data.get('new', 0)
#         new_tender_ids = data.get('new_tender_ids', [])
        
#         indexing_result = {'submitted': 0, 'failed': 0, 'message': 'No new tenders to index'}
        
#         if new_count > 0 and new_tender_ids:
#             try:
#                 # Get the new tenders from database
#                 new_tenders = Tender.query.filter(
#                     Tender.id.in_(new_tender_ids)
#                 ).all()
                
#                 # Convert to dicts for indexing
#                 tender_dicts = [t.to_dict() for t in new_tenders]
                
#                 # Index them in OpenRAG
#                 openrag_client = OpenRAGClient()
#                 index_result = openrag_client.index_tenders_batch(tender_dicts)
                
#                 indexing_result = {
#                     'submitted': index_result.get('submitted', 0),
#                     'failed': index_result.get('failed', 0),
#                     'task_ids': index_result.get('task_ids', []),
#                     'message': f"Submitted {index_result.get('submitted', 0)} tenders for indexing"
#                 }
                
#                 logger.info(f"📤 Indexed {len(tender_dicts)} new tenders in OpenRAG")
                
#             except Exception as e:
#                 logger.error(f"Failed to index tenders: {e}")
#                 indexing_result = {
#                     'submitted': 0,
#                     'failed': new_count,
#                     'error': str(e),
#                     'message': f"Indexing failed: {str(e)}"
#                 }
        
#         # Add indexing info to result
#         result['data']['indexing'] = indexing_result
        
#         return jsonify(result)
        
#     except Exception as e:
#         logger.error(f"Scrape and index error: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/scrape-all-and-index', methods=['POST'])
# def scrape_all_and_index():
#     """Scrape all sources and index new tenders"""
#     try:
#         from services.openrag_client import OpenRAGClient
#         from models.tender import Tender
#         from models.scraper_config import ScraperConfig
        
#         # Get all active sources
#         sources = ScraperConfig.query.filter_by(is_active=True).all()
        
#         if not sources:
#             return jsonify({
#                 'success': False,
#                 'error': 'No active sources found'
#             }), 400
        
#         results = {}
#         total_new = 0
#         all_new_tender_ids = []
#         successful_sources = 0
#         failed_sources = 0
        
#         # Scrape each source
#         for source in sources:
#             try:
#                 result = ScraperManager.scrape_source(source.id)
#                 results[source.id] = result
                
#                 if result.get('success'):
#                     successful_sources += 1
#                     data = result.get('data', {})
#                     total_new += data.get('new', 0)
#                     all_new_tender_ids.extend(data.get('new_tender_ids', []))
#                 else:
#                     failed_sources += 1
#                     results[source.id] = {
#                         'success': False,
#                         'error': result.get('error', 'Unknown error')
#                     }
#             except Exception as e:
#                 results[source.id] = {'success': False, 'error': str(e)}
#                 failed_sources += 1
        
#         # Index all new tenders
#         indexing_result = {'submitted': 0, 'failed': 0, 'message': 'No new tenders to index'}
        
#         if all_new_tender_ids:
#             try:
#                 new_tenders = Tender.query.filter(
#                     Tender.id.in_(all_new_tender_ids)
#                 ).all()
                
#                 tender_dicts = [t.to_dict() for t in new_tenders]
                
#                 openrag_client = OpenRAGClient()
#                 index_result = openrag_client.index_tenders_batch(tender_dicts)
                
#                 indexing_result = {
#                     'submitted': index_result.get('submitted', 0),
#                     'failed': index_result.get('failed', 0),
#                     'task_ids': index_result.get('task_ids', []),
#                     'message': f"Submitted {index_result.get('submitted', 0)} tenders for indexing"
#                 }
                
#                 logger.info(f"📤 Indexed {len(tender_dicts)} new tenders in OpenRAG")
                
#             except Exception as e:
#                 logger.error(f"Failed to index tenders: {e}")
#                 indexing_result = {
#                     'submitted': 0,
#                     'failed': len(all_new_tender_ids),
#                     'error': str(e),
#                     'message': f"Indexing failed: {str(e)}"
#                 }
        
#         return jsonify({
#             'success': True,
#             'message': f'Scraped {total_new} new tenders from {successful_sources} sources ({failed_sources} failed)',
#             'data': {
#                 'total_new': total_new,
#                 'successful_sources': successful_sources,
#                 'failed_sources': failed_sources,
#                 'sources': results,
#                 'indexing': indexing_result
#             }
#         })
        
#     except Exception as e:
#         logger.error(f"Scrape all and index error: {e}")
#         return jsonify({'success': False, 'error': str(e)}), 500

# # ============ Existing Test Endpoint ============

# @scraper_bp.route('/test', methods=['POST'])
# def test_source():
#     """Test a scraper configuration"""
#     try:
#         data = request.get_json()
#         result = ScraperManager.test_source(data)
#         return jsonify(result)
        
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500

# @scraper_bp.route('/available-sources', methods=['GET'])
# def get_available_sources():
#     """Get list of pre-configured available sources"""
#     try:
#         available = [
#             {
#                 'name': 'TUNEPS',
#                 'display_name': 'TUNEPS - Tunisian Government Procurement',
#                 'description': 'Official Tunisian government procurement portal',
#                 'icon': '🏛️',
#                 'type': 'api',
#                 'preconfigured': True
#             },
#         ]
#         return jsonify({
#             'success': True,
#             'available_sources': available
#         })
#     except Exception as e:
#         return jsonify({'success': False, 'error': str(e)}), 500



# routes/scraper_routes.py - UPDATED to handle OpenRAG client response
from flask import Blueprint, request, jsonify
from services.scraper_manager import ScraperManager
import logging
from database import db
from models.tender import Tender
from datetime import datetime 
scraper_bp = Blueprint('scraper', __name__, url_prefix='/api/scrapers')
logger = logging.getLogger(__name__)

@scraper_bp.route('/sources', methods=['GET'])
def get_sources():
    """Get all scraper sources"""
    try:
        sources = ScraperManager.get_all_sources()
        return jsonify({
            'success': True,
            'sources': sources
        })
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/sources', methods=['POST'])
def create_source():
    """Create a new scraper source"""
    try:
        data = request.get_json()
        result = ScraperManager.create_source(data)
        
        if result.get('success'):
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error creating source: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/sources/<int:source_id>', methods=['GET'])
def get_source(source_id):
    """Get a specific source"""
    try:
        source = ScraperManager.get_source(source_id)
        if source:
            return jsonify({'success': True, 'source': source})
        else:
            return jsonify({'success': False, 'error': 'Source not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/sources/<int:source_id>', methods=['DELETE'])
def delete_source(source_id):
    """Delete a source"""
    try:
        result = ScraperManager.delete_source(source_id)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/sources/<int:source_id>/scrape', methods=['POST'])
def scrape_source(source_id):
    """Scrape a source"""
    try:
        result = ScraperManager.scrape_source(source_id)
        
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ SCRAPE AND INDEX ENDPOINTS ============

@scraper_bp.route('/sources/<int:source_id>/scrape-and-index', methods=['POST'])
def scrape_and_index_source(source_id):
    """Scrape a source and index the new tenders in OpenRAG"""
    try:
        from services.openrag_client import OpenRAGClient
        from models.tender import Tender
        
        logger.info(f"🔄 Starting scrape and index for source {source_id}")
        
        # First, scrape
        result = ScraperManager.scrape_source(source_id)
        logger.info(f"📊 Scrape result: {result}")
        
        if not result.get('success'):
            return jsonify(result), 400
        
        # If there are new tenders, index them
        data = result.get('data', {})
        new_count = data.get('new', 0)
        new_tender_ids = data.get('new_tender_ids', [])
        
        indexing_result = {'submitted': 0, 'failed': 0, 'message': 'No new tenders to index'}
        
        if new_count > 0 and new_tender_ids:
            try:
                # Get the new tenders from database
                new_tenders = Tender.query.filter(
                    Tender.id.in_(new_tender_ids)
                ).all()
                
                if not new_tenders:
                    logger.warning(f"No new tenders found with IDs: {new_tender_ids}")
                else:
                    logger.info(f"📊 Retrieved {len(new_tenders)} new tenders from database")
                    
                    # Convert to dicts for indexing
                    tender_dicts = [t.to_dict() for t in new_tenders]
                    logger.info(f"📊 Sample tender: {tender_dicts[0] if tender_dicts else 'None'}")
                    
                    # Index them in OpenRAG
                    openrag_client = OpenRAGClient()
                    index_result = openrag_client.index_tenders_batch(tender_dicts)
                    logger.info(f"📊 Index result: {index_result}")
                    
                    indexing_result = {
                        'submitted': index_result.get('submitted', 0),
                        'failed': index_result.get('failed', 0),
                        'task_ids': index_result.get('task_ids', []),
                        'message': f"Submitted {index_result.get('submitted', 0)} tenders for indexing",
                        'errors': index_result.get('errors', [])
                    }
                    
                    logger.info(f"✅ Indexing complete: {indexing_result['submitted']} submitted, {indexing_result['failed']} failed")
                
            except Exception as e:
                logger.error(f"❌ Failed to index tenders: {e}")
                import traceback
                traceback.print_exc()
                indexing_result = {
                    'submitted': 0,
                    'failed': new_count,
                    'error': str(e),
                    'message': f"Indexing failed: {str(e)}"
                }
        else:
            logger.info("ℹ️ No new tenders to index")
        
        # Add indexing info to result
        result['data']['indexing'] = indexing_result
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"❌ Scrape and index error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/scrape-all-and-index', methods=['POST'])
def scrape_all_and_index():
    """Scrape all sources and index new tenders"""
    try:
        from services.openrag_client import OpenRAGClient
        from models.tender import Tender
        from models.scraper_config import ScraperConfig
        
        logger.info("🔄 Starting scrape all and index")
        
        # Get all active sources
        sources = ScraperConfig.query.filter_by(is_active=True).all()
        
        if not sources:
            return jsonify({
                'success': False,
                'error': 'No active sources found'
            }), 400
        
        results = {}
        total_new = 0
        all_new_tender_ids = []
        successful_sources = 0
        failed_sources = 0
        
        # Scrape each source
        for source in sources:
            try:
                logger.info(f"📊 Scraping source: {source.name}")
                result = ScraperManager.scrape_source(source.id)
                results[source.id] = result
                
                if result.get('success'):
                    successful_sources += 1
                    data = result.get('data', {})
                    total_new += data.get('new', 0)
                    new_ids = data.get('new_tender_ids', [])
                    if new_ids:
                        all_new_tender_ids.extend(new_ids)
                        logger.info(f"📊 Source {source.name}: {len(new_ids)} new tenders")
                else:
                    failed_sources += 1
                    logger.error(f"❌ Source {source.name} failed: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"❌ Error scraping source {source.name}: {e}")
                results[source.id] = {'success': False, 'error': str(e)}
                failed_sources += 1
        
        # Index all new tenders
        indexing_result = {'submitted': 0, 'failed': 0, 'message': 'No new tenders to index'}
        
        if all_new_tender_ids:
            try:
                logger.info(f"📊 Indexing {len(all_new_tender_ids)} new tenders")
                
                new_tenders = Tender.query.filter(
                    Tender.id.in_(all_new_tender_ids)
                ).all()
                
                if new_tenders:
                    tender_dicts = [t.to_dict() for t in new_tenders]
                    
                    openrag_client = OpenRAGClient()
                    index_result = openrag_client.index_tenders_batch(tender_dicts)
                    
                    indexing_result = {
                        'submitted': index_result.get('submitted', 0),
                        'failed': index_result.get('failed', 0),
                        'task_ids': index_result.get('task_ids', []),
                        'message': f"Submitted {index_result.get('submitted', 0)} tenders for indexing",
                        'errors': index_result.get('errors', [])
                    }
                    
                    logger.info(f"✅ Indexing complete: {indexing_result['submitted']} submitted, {indexing_result['failed']} failed")
                else:
                    logger.warning(f"No new tenders found with IDs: {all_new_tender_ids}")
                
            except Exception as e:
                logger.error(f"❌ Failed to index tenders: {e}")
                import traceback
                traceback.print_exc()
                indexing_result = {
                    'submitted': 0,
                    'failed': len(all_new_tender_ids),
                    'error': str(e),
                    'message': f"Indexing failed: {str(e)}"
                }
        else:
            logger.info("ℹ️ No new tenders to index")
        
        return jsonify({
            'success': True,
            'message': f'Scraped {total_new} new tenders from {successful_sources} sources ({failed_sources} failed)',
            'data': {
                'total_new': total_new,
                'successful_sources': successful_sources,
                'failed_sources': failed_sources,
                'sources': results,
                'indexing': indexing_result
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Scrape all and index error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ============ TEST ENDPOINT ============

@scraper_bp.route('/test', methods=['POST'])
def test_source():
    """Test a scraper configuration"""
    try:
        data = request.get_json()
        result = ScraperManager.test_source(data)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/available-sources', methods=['GET'])
def get_available_sources():
    """Get list of pre-configured available sources"""
    try:
        available = [
            {
                'name': 'TUNEPS',
                'display_name': 'TUNEPS - Tunisian Government Procurement',
                'description': 'Official Tunisian government procurement portal',
                'icon': '🏛️',
                'type': 'api',
                'preconfigured': True
            },
        ]
        return jsonify({
            'success': True,
            'available_sources': available
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@scraper_bp.route('/check-expired-deadlines', methods=['POST', 'OPTIONS'])
def check_expired_deadlines():
    """Check and update tenders whose deadlines have passed"""
    try:
        logger.info("🔍 Checking for expired tender deadlines")
        
        # Get ALL tenders (since we don't have a status field)
        # Or filter by those that might not be expired yet
        tenders = Tender.query.all()  # ✅ Get all tenders
        
        expired_count = 0
        expired_tenders = []
        current_date = datetime.now()
        
        for tender in tenders:
            if not tender.deadline:
                continue
                
            try:
                # Parse deadline date - handles multiple formats
                deadline_date = None
                deadline_str = str(tender.deadline).strip()
                
                # Try different date formats
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%d/%m/%Y',
                    '%b %d, %Y',
                    '%d %b %Y',
                ]
                
                for fmt in formats:
                    try:
                        deadline_date = datetime.strptime(deadline_str, fmt)
                        break
                    except ValueError:
                        continue
                
                # If no format matched, try to extract date with regex
                if not deadline_date:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline_str)
                    if date_match:
                        try:
                            deadline_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                        except:
                            pass
                    
                    # Try DD/MM/YYYY format
                    if not deadline_date:
                        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_str)
                        if date_match:
                            try:
                                deadline_date = datetime.strptime(date_match.group(1), '%d/%m/%Y')
                            except:
                                pass
                
                if deadline_date and deadline_date < current_date:
                    # Deadline has passed - increment count
                    expired_count += 1
                    expired_tenders.append({
                        'id': tender.id,
                        'reference': tender.reference,
                        'title': tender.title[:100] if tender.title else 'N/A',
                        'deadline': tender.deadline
                    })
                    logger.info(f"⏰ Tender {tender.reference} expired (deadline: {tender.deadline})")
                    
            except Exception as e:
                logger.warning(f"Could not parse deadline for tender {tender.reference}: {e}")
                continue
        
        logger.info(f"✅ Found {expired_count} expired tenders out of {len(tenders)} checked")
        
        return jsonify({
            'success': True,
            'message': f'Found {expired_count} expired tenders',
            'data': {
                'expired_count': expired_count,
                'expired_tenders': expired_tenders[:20],  # Show first 20
                'total_checked': len(tenders)
            }
        })
        
    except Exception as e:
        logger.error(f"Error checking expired deadlines: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@scraper_bp.route('/tenders/expired', methods=['GET'])
def get_expired_tenders():
    """Get all expired tenders"""
    try:
        # Since we don't have a status field, we need to check deadlines dynamically
        tenders = Tender.query.all()
        expired_tenders = []
        current_date = datetime.now()
        
        for tender in tenders:
            if not tender.deadline:
                continue
                
            try:
                deadline_str = str(tender.deadline).strip()
                deadline_date = None
                
                # Try to parse date
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%d/%m/%Y',
                ]
                
                for fmt in formats:
                    try:
                        deadline_date = datetime.strptime(deadline_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if deadline_date and deadline_date < current_date:
                    expired_tenders.append(tender.to_dict())
                    
            except Exception as e:
                continue
        
        return jsonify({
            'success': True,
            'data': {
                'count': len(expired_tenders),
                'tenders': expired_tenders
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting expired tenders: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Also add a test endpoint to verify the route works
@scraper_bp.route('/test', methods=['GET'])
def test_scraper_route():
    """Test endpoint to verify scraper routes work"""
    return jsonify({
        'success': True,
        'message': 'Scraper routes are working!',
        'timestamp': datetime.now().isoformat()
    })




# @scraper_bp.route('/delete-expired', methods=['POST', 'OPTIONS'])
# def delete_expired_tenders():
#     """Delete all tenders whose deadlines have passed"""
#     try:
#         logger.info("🗑️ Deleting expired tenders...")
        
#         # Get all tenders
#         tenders = Tender.query.all()
#         current_date = datetime.now()
#         deleted_count = 0
#         deleted_tenders = []
        
#         for tender in tenders:
#             if not tender.deadline:
#                 continue
                
#             try:
#                 deadline_str = str(tender.deadline).strip()
#                 deadline_date = None
                
#                 # Try different date formats
#                 formats = [
#                     '%Y-%m-%d %H:%M:%S',
#                     '%Y-%m-%d %H:%M:%S.%f',
#                     '%Y-%m-%dT%H:%M:%S',
#                     '%Y-%m-%d %H:%M',
#                     '%Y-%m-%d',
#                     '%d/%m/%Y %H:%M:%S',
#                     '%d/%m/%Y %H:%M',
#                     '%d/%m/%Y',
#                     '%b %d, %Y',
#                     '%d %b %Y',
#                 ]
                
#                 for fmt in formats:
#                     try:
#                         deadline_date = datetime.strptime(deadline_str, fmt)
#                         break
#                     except ValueError:
#                         continue
                
#                 # If no format matched, try regex
#                 if not deadline_date:
#                     date_match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline_str)
#                     if date_match:
#                         try:
#                             deadline_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
#                         except:
#                             pass
                    
#                     if not deadline_date:
#                         date_match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_str)
#                         if date_match:
#                             try:
#                                 deadline_date = datetime.strptime(date_match.group(1), '%d/%m/%Y')
#                             except:
#                                 pass
                
#                 if deadline_date and deadline_date < current_date:
#                     # Store info before deleting
#                     deleted_tenders.append({
#                         'id': tender.id,
#                         'reference': tender.reference,
#                         'title': tender.title[:100] if tender.title else 'N/A',
#                         'deadline': tender.deadline
#                     })
                    
#                     # Delete the tender
#                     db.session.delete(tender)
#                     deleted_count += 1
#                     logger.info(f"🗑️ Deleted expired tender {tender.reference} (deadline: {tender.deadline})")
                    
#             except Exception as e:
#                 logger.warning(f"Could not parse deadline for tender {tender.reference}: {e}")
#                 continue
        
#         # Commit the deletion
#         db.session.commit()
        
#         logger.info(f"✅ Deleted {deleted_count} expired tenders")
        
#         return jsonify({
#             'success': True,
#             'message': f'Deleted {deleted_count} expired tenders',
#             'data': {
#                 'deleted_count': deleted_count,
#                 'deleted_tenders': deleted_tenders[:20],
#                 'total_checked': len(tenders)
#             }
#         })
        
#     except Exception as e:
#         logger.error(f"Error deleting expired tenders: {e}")
#         db.session.rollback()
#         import traceback
#         traceback.print_exc()
#         return jsonify({'success': False, 'error': str(e)}), 500

@scraper_bp.route('/delete-expired', methods=['POST', 'OPTIONS'])
def delete_expired_tenders():
    """Delete all tenders whose deadlines have passed - from both PostgreSQL AND Milvus"""
    try:
        from services.openrag_client import OpenRAGClient
        from models.tender import Tender
        from database import db
        from datetime import datetime
        import re
        
        logger.info("🗑️ Deleting expired tenders from PostgreSQL and Milvus...")
        
        # Get all tenders
        tenders = Tender.query.all()
        current_date = datetime.now()
        deleted_count = 0
        deleted_tenders = []
        tender_ids_to_delete = []
        
        # First, identify which tenders are expired
        for tender in tenders:
            if not tender.deadline:
                continue
                
            try:
                deadline_str = str(tender.deadline).strip()
                deadline_date = None
                
                formats = [
                    '%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',
                    '%Y-%m-%dT%H:%M:%S',
                    '%Y-%m-%d %H:%M',
                    '%Y-%m-%d',
                    '%d/%m/%Y %H:%M:%S',
                    '%d/%m/%Y %H:%M',
                    '%d/%m/%Y',
                    '%b %d, %Y',
                    '%d %b %Y',
                ]
                
                for fmt in formats:
                    try:
                        deadline_date = datetime.strptime(deadline_str, fmt)
                        break
                    except ValueError:
                        continue
                
                if not deadline_date:
                    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', deadline_str)
                    if date_match:
                        try:
                            deadline_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                        except:
                            pass
                    
                    if not deadline_date:
                        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', deadline_str)
                        if date_match:
                            try:
                                deadline_date = datetime.strptime(date_match.group(1), '%d/%m/%Y')
                            except:
                                pass
                
                if deadline_date and deadline_date < current_date:
                    tender_ids_to_delete.append(tender.id)
                    deleted_tenders.append({
                        'id': tender.id,
                        'reference': tender.reference,
                        'title': tender.title[:100] if tender.title else 'N/A',
                        'deadline': tender.deadline
                    })
                    deleted_count += 1
                    
            except Exception as e:
                logger.warning(f"Could not parse deadline for tender {tender.reference}: {e}")
                continue
        
        if deleted_count == 0:
            return jsonify({
                'success': True,
                'message': 'No expired tenders found to delete',
                'data': {
                    'deleted_count': 0,
                    'deleted_tenders': []
                }
            })
        
        # Initialize OpenRAG client
        openrag_client = OpenRAGClient()
        
        # Get Milvus count before deletion (will return -1 if not available)
        before_count = openrag_client.count_milvus_documents()
        if before_count >= 0:
            logger.info(f"📊 Milvus documents before deletion: {before_count}")
        else:
            logger.info("ℹ️ Direct Milvus count not available - OpenRAG handles deletion")
        
        # Delete from OpenRAG (which handles Milvus)
        rag_result = openrag_client.delete_tenders_batch(tender_ids_to_delete)
        
        # Get Milvus count after deletion (will return -1 if not available)
        after_count = openrag_client.count_milvus_documents()
        if after_count >= 0:
            logger.info(f"📊 Milvus documents after deletion: {after_count}")
        else:
            logger.info("ℹ️ Direct Milvus count not available - OpenRAG handled deletion")
        
        logger.info(f"🗑️ OpenRAG deletion result: {rag_result}")
        logger.info(f"🗑️ Deleted {rag_result.get('openrag_successful', 0)} tenders from OpenRAG (handles Milvus)")
        if rag_result.get('failed', 0) > 0:
            logger.warning(f"⚠️ {rag_result.get('failed', 0)} tenders failed to delete")
        
        # Delete from PostgreSQL
        for tender in tenders:
            if tender.id in tender_ids_to_delete:
                db.session.delete(tender)
        
        db.session.commit()
        
        logger.info(f"✅ Deleted {deleted_count} expired tenders from PostgreSQL")
        
        return jsonify({
            'success': True,
            'message': f'Deleted {deleted_count} expired tenders',
            'data': {
                'deleted_count': deleted_count,
                'deleted_tenders': deleted_tenders[:20],
                'total_checked': len(tenders),
                'openrag_deletion': {
                    'openrag_successful': rag_result.get('openrag_successful', 0),
                    'milvus_successful': rag_result.get('milvus_successful', 0),
                    'failed': rag_result.get('failed', 0),
                    'errors': rag_result.get('errors', [])
                },
                'milvus_count': {
                    'before': before_count if before_count >= 0 else 'N/A',
                    'after': after_count if after_count >= 0 else 'N/A'
                }
            }
        })
        
    except Exception as e:
        logger.error(f"Error deleting expired tenders: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
        
    
# /////////////////////// new

# services/scraper_manager.py
from models.scraper_config import ScraperConfig
from models.tender import Tender
from services.scrapers.dynamic_scraper import DynamicScraper
from database import db
import json
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ScraperManager:
    """Manages all scraper sources"""
    
    @staticmethod
    def get_all_sources():
        """Get all configured sources"""
        configs = ScraperConfig.query.all()
        return [c.to_dict() for c in configs]
    
    @staticmethod
    def get_source(source_id):
        """Get a specific source"""
        config = ScraperConfig.query.get(source_id)
        return config.to_dict() if config else None
    
    @staticmethod
    def create_source(data):
        """Create a new scraper source"""
        try:
            # Validate required fields
            required = ['name', 'display_name', 'base_url']
            for field in required:
                if not data.get(field):
                    return {'success': False, 'error': f'{field} is required'}
            
            # Check if name already exists
            if ScraperConfig.query.filter_by(name=data['name']).first():
                return {'success': False, 'error': 'Source name already exists'}
            
            # Test the configuration
            test_result = ScraperManager.test_source(data)
            if not test_result.get('success'):
                return {'success': False, 'error': f'Configuration test failed: {test_result.get("error")}'}
            
            # Create config
            config = ScraperConfig(
                name=data['name'],
                display_name=data['display_name'],
                source_type=data.get('source_type', 'api'),
                base_url=data['base_url'],
                headers=json.dumps(data.get('headers', {})),
                auth_type=data.get('auth_type', 'none'),
                auth_config=json.dumps(data.get('auth_config', {})),
                parser_config=json.dumps(data.get('parser_config', {})),
                is_active=True
            )
            
            db.session.add(config)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Source {data["name"]} created successfully',
                'config': config.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating source: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def test_source(data):
        """Test a scraper configuration"""
        try:
            scraper = DynamicScraper(data)
            valid, message = scraper.validate_config()
            if not valid:
                return {'success': False, 'error': message}
            
            # Test scrape (limit 5)
            tenders = scraper.scrape_tenders(limit=5)
            
            if tenders:
                return {
                    'success': True,
                    'message': f'Successfully scraped {len(tenders)} tenders',
                    'sample': tenders[:3]
                }
            else:
                return {
                    'success': False,
                    'error': 'No tenders found. Check your configuration.'
                }
                
        except Exception as e:
            logger.error(f"Test error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def scrape_source(source_id):
        """Scrape a specific source"""
        try:
            config = ScraperConfig.query.get(source_id)
            if not config:
                return {'success': False, 'error': 'Source not found'}
            
            if not config.is_active:
                return {'success': False, 'error': 'Source is inactive'}
            
            # Build config dict for dynamic scraper
            config_dict = {
                'name': config.name,
                'display_name': config.display_name,
                'base_url': config.base_url,
                'headers': json.loads(config.headers) if config.headers else {},
                'auth_type': config.auth_type,
                'auth_config': json.loads(config.auth_config) if config.auth_config else {},
                'parser_config': json.loads(config.parser_config) if config.parser_config else {},
                'source_type': config.source_type
            }
            
            scraper = DynamicScraper(config_dict)
            
            # Scrape tenders
            tenders = scraper.scrape_tenders()
            
            # Save to database
            result = scraper.save_tenders(db, Tender, tenders)
            
            # Update config
            config.last_scraped = datetime.utcnow()
            config.total_tenders = Tender.query.filter_by(source=config.name).count()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Scraped {result["new"]} new tenders from {config.display_name}',
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Scrape error: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def delete_source(source_id):
        """Delete a source and its tenders"""
        try:
            config = ScraperConfig.query.get(source_id)
            if not config:
                return {'success': False, 'error': 'Source not found'}
            
            # Delete all tenders from this source
            Tender.query.filter_by(source=config.name).delete()
            
            # Delete the config
            db.session.delete(config)
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Source {config.name} and its tenders deleted'
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}




    @staticmethod
    def scrape_and_index_source(source_id):
        """Scrape a specific source and index the new tenders to OpenRAG"""
        try:
            from services.openrag_client import OpenRAGClient
            
            config = ScraperConfig.query.get(source_id)
            if not config:
                return {'success': False, 'error': 'Source not found'}
            
            if not config.is_active:
                return {'success': False, 'error': 'Source is inactive'}
            
            # Build config dict for dynamic scraper
            config_dict = {
                'name': config.name,
                'display_name': config.display_name,
                'base_url': config.base_url,
                'headers': json.loads(config.headers) if config.headers else {},
                'auth_type': config.auth_type,
                'auth_config': json.loads(config.auth_config) if config.auth_config else {},
                'parser_config': json.loads(config.parser_config) if config.parser_config else {},
                'source_type': config.source_type
            }
            
            scraper = DynamicScraper(config_dict)
            
            # Scrape tenders
            tenders = scraper.scrape_tenders()
            
            # Save to database
            result = scraper.save_tenders(db, Tender, tenders)
            
            # Index new tenders to OpenRAG
            openrag = OpenRAGClient()
            indexed_count = 0
            
            if result.get('new', 0) > 0:
                # Get the new tenders (those with is_new flag)
                new_tenders = Tender.query.filter_by(
                    source=config.name,
                    is_new=True
                ).all()
                
                print(f"📤 Indexing {len(new_tenders)} new tenders to OpenRAG...")
                
                for tender in new_tenders:
                    try:
                        tender_dict = tender.to_dict()
                        openrag.upload_tender(tender.id, tender_dict)
                        indexed_count += 1
                        # Mark as indexed
                        tender.is_indexed = True
                        print(f"  ✅ Indexed tender {tender.id} - {tender.reference}")
                    except Exception as e:
                        print(f"  ❌ Error indexing tender {tender.id}: {e}")
                
                db.session.commit()
                print(f"✅ Indexed {indexed_count}/{result.get('new', 0)} new tenders")
            
            # Update config
            config.last_scraped = datetime.utcnow()
            config.total_tenders = Tender.query.filter_by(source=config.name).count()
            db.session.commit()
            
            return {
                'success': True,
                'message': f'Scraped {result["new"]} new tenders from {config.display_name}, indexed {indexed_count}',
                'data': {
                    'new': result.get('new', 0),
                    'indexed': indexed_count,
                    'total': result.get('total', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Scrape and index error: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
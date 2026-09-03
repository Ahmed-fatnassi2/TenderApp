# services/scrapers/tuneps_scraper.py
from services.scrapers.base_scraper import BaseScraper
import requests
from datetime import datetime
import re
import logging
from typing import Dict, List, Any, Optional  # Add this import!

logger = logging.getLogger(__name__)

class TUNEPSScraper(BaseScraper):
    """TUNEPS scraper implementation"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            'name': 'TUNEPS',
            'display_name': 'TUNEPS - Tunisian Government Procurement',
            'source_type': 'api',
            'base_url': 'https://www.tuneps.tn/api2/portail/bid/master/data',
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Content-Type': 'application/json',
                'Origin': 'https://www.tuneps.tn',
                'Referer': 'https://www.tuneps.tn/portail/offres',
            }
        }
        super().__init__(config or default_config)
    
    def validate_config(self) -> tuple[bool, str]:
        if not self.config.get('base_url'):
            return False, "Base URL is required"
        return True, "Valid"
    
    def get_source_info(self) -> Dict[str, str]:
        return {
            'name': self.source_name,
            'display_name': self.display_name,
            'description': 'Tunisian Government Procurement Portal',
            'icon': '🏛️',
            'type': 'api'
        }
    
    def scrape_tenders(self, limit: int = 1500) -> List[Dict[str, Any]]:
        """Fetch tenders from TUNEPS API"""
        logger.info(f"🔍 Fetching tenders from TUNEPS API...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        payload = {
            "listSort": [],
            "dataSearch": [
                {"key": "publicYn", "value": "Y", "specificSearch": "="},
                {"key": "bdRecvEndDt", "value": today, "specificSearch": ">="}
            ],
            "listCol": [],
            "pagination": {"offSet": 0, "limit": limit},
            "sort": {"nameCol": "publicDt", "direction": "desc nulls last"}
        }
        
        try:
            response = requests.post(
                self.config['base_url'],
                headers=self.config['headers'],
                json=payload,
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                return []
            
            data = response.json()
            
            if data.get('code') == '200':
                payload_data = data.get('payload', {})
                tender_list = payload_data.get('data', [])
            else:
                tender_list = data.get('data', data.get('list', []))
            
            if not tender_list:
                logger.warning("No tenders found")
                return []
            
            valid_tenders = []
            for item in tender_list:
                try:
                    tender = {
                        'reference': item.get('bidNo', '').strip(),
                        'buyer': item.get('bidInstNm', '').strip(),
                        'publication_date': item.get('publicDt', ''),
                        'title': (
                            item.get('bidNmAr', '') or 
                            item.get('bidNmFr', '') or 
                            item.get('bidNmEn', '') or
                            'No title'
                        ).strip(),
                        'deadline': item.get('bdRecvEndDt', ''),
                    }
                    
                    if tender['reference']:
                        valid_tenders.append(tender)
                        
                except Exception as e:
                    logger.debug(f"Error processing tender: {e}")
                    continue
            
            logger.info(f"✅ Found {len(valid_tenders)} valid tenders from TUNEPS")
            return valid_tenders
            
        except Exception as e:
            logger.error(f"TUNEPS scraping error: {e}")
            return []
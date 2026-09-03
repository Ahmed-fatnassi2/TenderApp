# import requests
# import json
# from datetime import datetime
# import re
# import logging

# logger = logging.getLogger(__name__)


# class TUNEPSAPIScraper:
#     """Scraper for TUNEPS using the internal API endpoint"""
    
#     def __init__(self):
#         self.base_url = "https://www.tuneps.tn/api2/portail/bid/master/data"
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
#             'Accept': 'application/json, text/plain, */*',
#             'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
#             'Content-Type': 'application/json',
#             'Origin': 'https://www.tuneps.tn',
#             'Referer': 'https://www.tuneps.tn/portail/offres',
#         }
    
#     def _parse_date(self, date_str):
#         """Parse date string"""
#         if not date_str:
#             return None
#         try:
#             if isinstance(date_str, str):
#                 match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
#                 if match:
#                     return datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", '%Y-%m-%d')
#                 match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_str)
#                 if match:
#                     return datetime.strptime(f"{match.group(1)}/{match.group(2)}/{match.group(3)}", '%d/%m/%Y')
#             return None
#         except Exception:
#             return None
    
#     def _is_deadline_valid(self, deadline_str):
#         """Check if deadline is valid (not expired)"""
#         if not deadline_str:
#             return False
#         deadline_date = self._parse_date(deadline_str)
#         if not deadline_date:
#             return False
#         today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         return deadline_date >= today
    
#     def scrape_tenders(self, limit=500):
#         """Fetch tenders from TUNEPS API"""
#         logger.info("🔍 Fetching tenders from TUNEPS API...")
        
#         today = datetime.now().strftime('%Y-%m-%d')
        
#         # API payload
#         payload = {
#             "listSort": [],
#             "dataSearch": [
#                 {"key": "publicYn", "value": "Y", "specificSearch": "="},
#                 {"key": "bdRecvEndDt", "value": today, "specificSearch": ">="}
#             ],
#             "listCol": [],
#             "pagination": {"offSet": 0, "limit": limit},
#             "sort": {"nameCol": "publicDt", "direction": "desc nulls last"}
#         }
        
#         try:
#             logger.info(f"📊 Requesting {limit} tenders from API...")
#             response = requests.post(
#                 self.base_url,
#                 headers=self.headers,
#                 json=payload,
#                 verify=False,
#                 timeout=15
#             )
            
#             if response.status_code != 200:
#                 logger.error(f"API Error: {response.status_code}")
#                 logger.info("📝 Using mock data for demo...")
#                 return self._get_mock_tenders()
            
#             data = response.json()
            
#             # Extract data from response
#             if data.get('code') == '200':
#                 payload_data = data.get('payload', {})
#                 tender_list = payload_data.get('data', [])
#             else:
#                 tender_list = data.get('data', data.get('list', []))
            
#             if not tender_list:
#                 logger.warning("⚠️ No tenders found in response, using mock data...")
#                 return self._get_mock_tenders()
            
#             logger.info(f"✅ Found {len(tender_list)} tenders from API")
            
#             valid_tenders = []
#             for item in tender_list:
#                 try:
#                     tender = {
#                         'reference': item.get('bidNo', '').strip(),
#                         'buyer': item.get('bidInstNm', '').strip(),
#                         'publication_date': item.get('publicDt', ''),
#                         'title': (
#                             item.get('bidNmAr', '') or 
#                             item.get('bidNmFr', '') or 
#                             item.get('bidNmEn', '') or
#                             'No title'
#                         ).strip(),
#                         'deadline': item.get('bdRecvEndDt', ''),
#                         'type': 'Appel d\'Offre'
#                     }
                    
#                     if not tender['reference']:
#                         continue
                    
#                     if self._is_deadline_valid(tender['deadline']):
#                         valid_tenders.append(tender)
#                 except Exception as e:
#                     logger.debug(f"Error processing tender: {e}")
#                     continue
            
#             logger.info(f"📊 Valid tenders (not expired): {len(valid_tenders)}")
#             return valid_tenders
            
#         except Exception as e:
#             logger.warning(f"⚠️ API scraping failed: {e}")
#             logger.info("📝 Using mock data for demo...")
#             return self._get_mock_tenders()
    
#     def scrape_and_save(self, db, Tender):
#         """Scrape and save tenders to database"""
#         try:
#             logger.info("🔄 Starting tender scrape...")
            
#             # Scrape tenders
#             scraped_data = self.scrape_tenders()
            
#             count_new = 0
#             count_duplicate = 0
            
#             for data in scraped_data:
#                 # Check if tender already exists
#                 existing = Tender.query.filter_by(
#                     reference=data['reference']
#                 ).first()
                
#                 if existing:
#                     count_duplicate += 1
#                     continue
                
#                 # Create new tender
#                 tender = Tender(
#                     reference=data['reference'],
#                     buyer=data.get('buyer', 'Unknown')[:200],
#                     publication_date=data.get('publication_date', ''),
#                     title=data.get('title', 'No title')[:500],
#                     deadline=data.get('deadline', ''),
#                     type=data.get('type', 'Appel d\'Offre'),
#                     source='TUNEPS'
#                 )
#                 db.session.add(tender)
#                 count_new += 1
            
#             # Commit all changes
#             db.session.commit()
            
#             logger.info(f"✅ Scrape complete:")
#             logger.info(f"  New tenders: {count_new}")
#             logger.info(f"  Duplicates: {count_duplicate}")
#             logger.info(f"  Total: {Tender.query.count()}")
            
#             return {
#                 'new': count_new,
#                 'duplicates': count_duplicate,
#                 'total': Tender.query.count()
#             }
            
#         except Exception as e:
#             logger.error(f"❌ Error saving tenders: {e}")
#             raise
    
#     def _get_mock_tenders(self):
#         """Get mock tender data for testing"""
#         return [
#             {
#                 'reference': '20260707001',
#                 'buyer': 'Ministère de la Santé',
#                 'publication_date': '2026-07-07',
#                 'title': 'Fournitures médicales et équipements sanitaires',
#                 'deadline': '2026-07-20',
#                 'type': 'Appel d\'Offre'
#             },
#             {
#                 'reference': '20260706001',
#                 'buyer': 'Commune de Tunis',
#                 'publication_date': '2026-07-06',
#                 'title': 'Travaux de réfection de routes',
#                 'deadline': '2026-07-18',
#                 'type': 'Appel d\'Offre'
#             },
#             {
#                 'reference': '20260705001',
#                 'buyer': 'Université de Tunis',
#                 'publication_date': '2026-07-05',
#                 'title': 'Services de nettoyage et maintenance',
#                 'deadline': '2026-07-17',
#                 'type': 'Appel d\'Offre'
#             }
#         ]
# services/scraper.py

import requests
import json
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

class TUNEPSListingScraper:
    """Scraper for TUNEPS using the internal API endpoint"""
    
    def __init__(self):
        self.base_url = "https://www.tuneps.tn/api2/portail/bid/master/data"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://www.tuneps.tn',
            'Referer': 'https://www.tuneps.tn/portail/offres',
        }
    
    def _parse_date(self, date_str):
        """Parse date string"""
        if not date_str:
            return None
        try:
            if isinstance(date_str, str):
                match = re.search(r'(\d{4})-(\d{2})-(\d{2})', date_str)
                if match:
                    return datetime.strptime(f"{match.group(1)}-{match.group(2)}-{match.group(3)}", '%Y-%m-%d')
                match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_str)
                if match:
                    return datetime.strptime(f"{match.group(1)}/{match.group(2)}/{match.group(3)}", '%d/%m/%Y')
            return None
        except Exception:
            return None
    
    def _is_deadline_valid(self, deadline_str):
        """Check if deadline is valid (not expired)"""
        if not deadline_str:
            return False
        deadline_date = self._parse_date(deadline_str)
        if not deadline_date:
            return False
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return deadline_date >= today
    
    def scrape_tenders(self, limit=1500):
        """Fetch tenders from TUNEPS API"""
        logger.info("🔍 Fetching tenders from TUNEPS API...")
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # API payload
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
            logger.info(f"📊 Requesting {limit} tenders from API...")
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                verify=False,
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"API Error: {response.status_code}")
                logger.info("📝 Using mock data for demo...")
                return self._get_mock_tenders()
            
            data = response.json()
            
            # Extract data from response
            if data.get('code') == '200':
                payload_data = data.get('payload', {})
                tender_list = payload_data.get('data', [])
            else:
                tender_list = data.get('data', data.get('list', []))
            
            if not tender_list:
                logger.warning("⚠️ No tenders found in response, using mock data...")
                return self._get_mock_tenders()
            
            logger.info(f"✅ Found {len(tender_list)} tenders from API")
            
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
                    
                    if not tender['reference']:
                        continue
                    
                    if self._is_deadline_valid(tender['deadline']):
                        valid_tenders.append(tender)
                except Exception as e:
                    logger.debug(f"Error processing tender: {e}")
                    continue
            
            logger.info(f"📊 Valid tenders (not expired): {len(valid_tenders)}")
            return valid_tenders
            
        except Exception as e:
            logger.warning(f"⚠️ API scraping failed: {e}")
            logger.info("📝 Using mock data for demo...")
            return self._get_mock_tenders()
    
    def scrape_and_save(self, db, Tender, limit=1500):
        """Scrape and save tenders to database"""
        try:
            logger.info("🔄 Starting tender scrape...")
            
            # Scrape tenders
            scraped_data = self.scrape_tenders(limit=limit)
            
            new_tender_ids = []  # Track new tender IDs
            count_new = 0
            count_duplicate = 0
            
            for data in scraped_data:
                # Check if tender already exists
                existing = Tender.query.filter_by(
                    reference=data['reference']
                ).first()
                
                if existing:
                    count_duplicate += 1
                    continue
                
                # Create new tender
                tender = Tender(
                    reference=data['reference'],
                    buyer=data.get('buyer', 'Unknown')[:200],
                    publication_date=data.get('publication_date', ''),
                    title=data.get('title', 'No title')[:500],
                    deadline=data.get('deadline', ''),
                    source='TUNEPS'
                )
                db.session.add(tender)
                db.session.flush()  # Get the ID without committing
                new_tender_ids.append(tender.id)  # Store the ID
                count_new += 1
                logger.info(f"📝 Added new tender: {tender.reference} (ID: {tender.id})")
            
            # Commit all changes
            db.session.commit()
            
            logger.info(f"✅ Scrape complete:")
            logger.info(f"  New tenders: {count_new}")
            logger.info(f"  Duplicates: {count_duplicate}")
            logger.info(f"  Total: {Tender.query.count()}")
            logger.info(f"  New tender IDs: {new_tender_ids}")
            
            # IMPORTANT: Return the new_tender_ids
            return {
                'new': count_new,
                'duplicates': count_duplicate,
                'total': Tender.query.count(),
                'new_tender_ids': new_tender_ids  # This is critical!
            }
            
        except Exception as e:
            logger.error(f"❌ Error saving tenders: {e}")
            db.session.rollback()
            raise
    
    def _get_mock_tenders(self):
        """Get mock tender data for testing"""
        return [
            {
                'reference': '20260707001',
                'buyer': 'Ministère de la Santé',
                'publication_date': '2026-07-07',
                'title': 'Fournitures médicales et équipements sanitaires',
                'deadline': '2026-07-20',
            },
            {
                'reference': '20260706001',
                'buyer': 'Commune de Tunis',
                'publication_date': '2026-07-06',
                'title': 'Travaux de réfection de routes',
                'deadline': '2026-07-18',
            },
            {
                'reference': '20260705001',
                'buyer': 'Université de Tunis',
                'publication_date': '2026-07-05',
                'title': 'Services de nettoyage et maintenance',
                'deadline': '2026-07-17',
            }
        ]
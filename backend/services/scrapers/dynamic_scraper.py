


# # services/scrapers/dynamic_scraper.py
# from services.scrapers.base_scraper import BaseScraper
# import requests
# import json
# from typing import Dict, List, Any, Optional
# import logging
# import urllib3
# import warnings

# # Disable all SSL warnings
# warnings.filterwarnings("ignore")
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# logger = logging.getLogger(__name__)

# class DynamicScraper(BaseScraper):
#     """Dynamic scraper for user-configured sources"""
    
#     def __init__(self, config: Dict[str, Any]):
#         super().__init__(config)
#         self.base_url = config.get('base_url')
#         self.headers = json.loads(config.get('headers', '{}')) if isinstance(config.get('headers'), str) else config.get('headers', {})
#         self.parser_config = json.loads(config.get('parser_config', '{}')) if isinstance(config.get('parser_config'), str) else config.get('parser_config', {})
#         self.auth_config = json.loads(config.get('auth_config', '{}')) if isinstance(config.get('auth_config'), str) else config.get('auth_config', {})
#         self.auth_type = config.get('auth_type', 'none')
#         self.source_type = config.get('source_type', 'api')
    
#     def validate_config(self) -> tuple[bool, str]:
#         if not self.config.get('base_url'):
#             return False, "Base URL is required"
#         if not self.config.get('name'):
#             return False, "Source name is required"
#         return True, "Valid"
    
#     def get_source_info(self) -> Dict[str, str]:
#         return {
#             'name': self.source_name,
#             'display_name': self.display_name,
#             'description': f'Dynamic source: {self.display_name}',
#             'icon': '🔌',
#             'type': self.source_type,
#             'url': self.base_url
#         }
    
#     def _get_auth_headers(self) -> Dict[str, str]:
#         """Build authentication headers"""
#         auth_headers = {}
        
#         if self.auth_type == 'bearer':
#             token = self.auth_config.get('token', '')
#             if token:
#                 auth_headers['Authorization'] = f'Bearer {token}'
                
#         elif self.auth_type == 'api_key':
#             key = self.auth_config.get('api_key', '')
#             key_name = self.auth_config.get('key_name', 'X-API-Key')
#             if key:
#                 auth_headers[key_name] = key
                
#         return auth_headers
    
#     def scrape_tenders(self, limit: int = 500) -> List[Dict[str, Any]]:
#         """Scrape tenders from dynamic source"""
#         try:
#             headers = {**self.headers, **self._get_auth_headers()}
            
#             if self.source_type == 'html':
#                 return self._scrape_html(limit, headers)
#             else:
#                 return self._scrape_api(limit, headers)
                
#         except Exception as e:
#             logger.error(f"Dynamic scraping error for {self.source_name}: {e}")
#             return []
    
#     def _scrape_api(self, limit: int, headers: Dict) -> List[Dict]:
#         """Scrape from API endpoint"""
#         try:
#             is_post = self.parser_config.get('method', 'GET').upper() == 'POST'
            
#             # Create a new session for each request
#             session = requests.Session()
#             # Disable SSL verification
#             session.verify = False
#             # Disable SSL warnings for this session
#             session.trust_env = False
            
#             if is_post:
#                 payload = self.parser_config.get('payload', {})
#                 if 'pagination' in payload:
#                     payload['pagination']['limit'] = limit
                
#                 logger.info(f"📤 POST request to {self.base_url}")
#                 response = session.post(
#                     self.base_url,
#                     headers=headers,
#                     json=payload,
#                     timeout=30
#                 )
#             else:
#                 params = self.parser_config.get('params', {})
#                 params['length'] = limit
                
#                 logger.info(f"📤 GET request to {self.base_url}")
#                 response = session.get(
#                     self.base_url,
#                     headers=headers,
#                     params=params,
#                     timeout=30
#                 )
            
#             session.close()
            
#             if response.status_code != 200:
#                 logger.error(f"API error: {response.status_code}")
#                 return []
            
#             data = response.json()
            
#             # Find the data path
#             path = self.parser_config.get('data_path', '').split('.')
#             items = self._get_nested_value(data, path, [])
            
#             if not items or not isinstance(items, list):
#                 logger.warning(f"No items found at data path: {path}")
#                 return []
            
#             # Map fields
#             mapping = self.parser_config.get('field_mapping', {})
#             tenders = []
            
#             for item in items[:limit]:
#                 tender = {
#                     'reference': str(self._get_nested_value(item, mapping.get('reference', '').split('.'), '')),
#                     'title': self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title'),
#                     'buyer': self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown'),
#                     'publication_date': self._get_nested_value(item, mapping.get('publication_date', '').split('.'), ''),
#                     'deadline': self._get_nested_value(item, mapping.get('deadline', '').split('.'), ''),
#                 }
                
#                 if tender['reference']:
#                     tenders.append(tender)
            
#             logger.info(f"✅ Found {len(tenders)} tenders from {self.source_name}")
#             return tenders
            
#         except Exception as e:
#             logger.error(f"API scraping error: {e}")
#             return []
    
#     def _scrape_html(self, limit: int, headers: Dict) -> List[Dict]:
#         """Scrape from HTML page"""
#         try:
#             from bs4 import BeautifulSoup
            
#             session = requests.Session()
#             session.verify = False
#             session.trust_env = False
            
#             response = session.get(
#                 self.base_url,
#                 headers=headers,
#                 timeout=30
#             )
            
#             session.close()
            
#             if response.status_code != 200:
#                 return []
            
#             soup = BeautifulSoup(response.content, 'html.parser')
#             selector = self.parser_config.get('item_selector', 'tr')
#             items = soup.select(selector)
            
#             mapping = self.parser_config.get('field_mapping', {})
#             tenders = []
            
#             for item in items[:limit]:
#                 tender = {
#                     'reference': self._get_html_text(item, mapping.get('reference', '')),
#                     'title': self._get_html_text(item, mapping.get('title', 'No title')),
#                     'buyer': self._get_html_text(item, mapping.get('buyer', 'Unknown')),
#                     'publication_date': self._get_html_text(item, mapping.get('publication_date', '')),
#                     'deadline': self._get_html_text(item, mapping.get('deadline', '')),
#                 }
                
#                 if tender['reference']:
#                     tenders.append(tender)
            
#             return tenders
            
#         except Exception as e:
#             logger.error(f"HTML scraping error: {e}")
#             return []
    
#     def _get_nested_value(self, data: Any, path: List[str], default: Any = None) -> Any:
#         """Get nested dictionary value by path"""
#         current = data
#         for key in path:
#             if not key:
#                 continue
#             if isinstance(current, dict):
#                 current = current.get(key)
#             elif isinstance(current, list):
#                 try:
#                     index = int(key) if key.isdigit() else 0
#                     current = current[index] if index < len(current) else default
#                 except (ValueError, IndexError):
#                     return default
#             else:
#                 return default
#         return current if current is not None else default
    
#     def _get_html_text(self, element, selector: str) -> str:
#         """Get text from HTML element using CSS selector"""
#         if not selector:
#             return ''
#         try:
#             selected = element.select_one(selector)
#             return selected.text.strip() if selected else ''
#         except:
#             return ''


# //////////////////////////////////////////////////////this works after adding the id of tenders to search










# # services/scrapers/dynamic_scraper.py
# from services.scrapers.base_scraper import BaseScraper
# import requests
# import json
# from typing import Dict, List, Any, Optional
# import logging
# import urllib3
# import warnings

# # Disable all SSL warnings
# warnings.filterwarnings("ignore")
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# logger = logging.getLogger(__name__)

# class DynamicScraper(BaseScraper):
#     """Dynamic scraper for user-configured sources"""
    
#     def __init__(self, config: Dict[str, Any]):
#         super().__init__(config)
#         self.base_url = config.get('base_url')
#         self.headers = json.loads(config.get('headers', '{}')) if isinstance(config.get('headers'), str) else config.get('headers', {})
#         self.parser_config = json.loads(config.get('parser_config', '{}')) if isinstance(config.get('parser_config'), str) else config.get('parser_config', {})
#         self.auth_config = json.loads(config.get('auth_config', '{}')) if isinstance(config.get('auth_config'), str) else config.get('auth_config', {})
#         self.auth_type = config.get('auth_type', 'none')
#         self.source_type = config.get('source_type', 'api')
    
#     def validate_config(self) -> tuple[bool, str]:
#         if not self.config.get('base_url'):
#             return False, "Base URL is required"
#         if not self.config.get('name'):
#             return False, "Source name is required"
#         return True, "Valid"
    
#     def get_source_info(self) -> Dict[str, str]:
#         return {
#             'name': self.source_name,
#             'display_name': self.display_name,
#             'description': f'Dynamic source: {self.display_name}',
#             'icon': '🔌',
#             'type': self.source_type,
#             'url': self.base_url
#         }
    
#     def _get_auth_headers(self) -> Dict[str, str]:
#         """Build authentication headers"""
#         auth_headers = {}
        
#         if self.auth_type == 'bearer':
#             token = self.auth_config.get('token', '')
#             if token:
#                 auth_headers['Authorization'] = f'Bearer {token}'
                
#         elif self.auth_type == 'api_key':
#             key = self.auth_config.get('api_key', '')
#             key_name = self.auth_config.get('key_name', 'X-API-Key')
#             if key:
#                 auth_headers[key_name] = key
                
#         return auth_headers
    
#     def scrape_tenders(self, limit: int = 500) -> List[Dict[str, Any]]:
#         """Scrape tenders from dynamic source"""
#         try:
#             headers = {**self.headers, **self._get_auth_headers()}
            
#             if self.source_type == 'html':
#                 return self._scrape_html(limit, headers)
#             else:
#                 return self._scrape_api(limit, headers)
                
#         except Exception as e:
#             logger.error(f"Dynamic scraping error for {self.source_name}: {e}")
#             return []
    
#     def _scrape_api(self, limit: int, headers: Dict) -> List[Dict]:
#         """Scrape from API endpoint"""
#         try:
#             is_post = self.parser_config.get('method', 'GET').upper() == 'POST'
            
#             session = requests.Session()
#             session.verify = False
#             session.trust_env = False
            
#             if is_post:
#                 payload = self.parser_config.get('payload', {})
#                 if 'pagination' in payload:
#                     payload['pagination']['limit'] = limit
                
#                 logger.info(f"📤 POST request to {self.base_url}")
#                 response = session.post(
#                     self.base_url,
#                     headers=headers,
#                     json=payload,
#                     timeout=30
#                 )
#             else:
#                 params = self.parser_config.get('params', {})
#                 params['length'] = limit
                
#                 logger.info(f"📤 GET request to {self.base_url}")
#                 response = session.get(
#                     self.base_url,
#                     headers=headers,
#                     params=params,
#                     timeout=30
#                 )
            
#             session.close()
            
#             if response.status_code != 200:
#                 logger.error(f"API error: {response.status_code}")
#                 return []
            
#             data = response.json()
            
#             # Find the data path
#             path = self.parser_config.get('data_path', '').split('.')
#             items = self._get_nested_value(data, path, [])
            
#             if not items or not isinstance(items, list):
#                 logger.warning(f"No items found at data path: {path}")
#                 return []
            
#             # Map fields
#             mapping = self.parser_config.get('field_mapping', {})
            
#             # ✅ Récupérer les champs pour l'URL
#             url_template = self.parser_config.get('url_template', '')
#             tender_id_field = mapping.get('tender_id', '')
            
#             tenders = []
            
#             for item in items[:limit]:
#                 # Extraire les champs
#                 reference = str(self._get_nested_value(item, mapping.get('reference', '').split('.'), ''))
#                 title = self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title')
#                 buyer = self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown')
#                 publication_date = self._get_nested_value(item, mapping.get('publication_date', '').split('.'), '')
#                 deadline = self._get_nested_value(item, mapping.get('deadline', '').split('.'), '')
                
#                 # ✅ Construire l'URL
#                 source_url = None
#                 if url_template and tender_id_field and reference:
#                     tender_id = str(self._get_nested_value(item, tender_id_field.split('.'), ''))
#                     if tender_id:
#                         source_url = url_template.replace('{tender_id}', tender_id).replace('{reference}', reference)
#                 elif url_template and reference:
#                     # Fallback: essayer avec juste la référence
#                     source_url = url_template.replace('{reference}', reference)
#                     if '{tender_id}' in source_url:
#                         source_url = None  # Pas d'ID disponible
                
#                 tender = {
#                     'reference': reference,
#                     'title': title,
#                     'buyer': buyer,
#                     'publication_date': publication_date,
#                     'deadline': deadline,
#                     'source_url': source_url,  # ✅ Ajouter l'URL
#                 }
                
#                 if tender['reference']:
#                     tenders.append(tender)
            
#             logger.info(f"✅ Found {len(tenders)} tenders from {self.source_name}")
#             return tenders
            
#         except Exception as e:
#             logger.error(f"API scraping error: {e}")
#             return []
    
#     def _scrape_html(self, limit: int, headers: Dict) -> List[Dict]:
#         """Scrape from HTML page"""
#         try:
#             from bs4 import BeautifulSoup
            
#             session = requests.Session()
#             session.verify = False
#             session.trust_env = False
            
#             response = session.get(
#                 self.base_url,
#                 headers=headers,
#                 timeout=30
#             )
            
#             session.close()
            
#             if response.status_code != 200:
#                 return []
            
#             soup = BeautifulSoup(response.content, 'html.parser')
#             selector = self.parser_config.get('item_selector', 'tr')
#             items = soup.select(selector)
            
#             mapping = self.parser_config.get('field_mapping', {})
            
#             # ✅ Récupérer l'URL depuis le HTML
#             url_selector = self.parser_config.get('url_selector', '')
#             url_prefix = self.parser_config.get('url_prefix', '')
#             url_template = self.parser_config.get('url_template', '')
            
#             tenders = []
            
#             for item in items[:limit]:
#                 # Extraire les champs
#                 reference = self._get_html_text(item, mapping.get('reference', ''))
#                 title = self._get_html_text(item, mapping.get('title', 'No title'))
#                 buyer = self._get_html_text(item, mapping.get('buyer', 'Unknown'))
#                 publication_date = self._get_html_text(item, mapping.get('publication_date', ''))
#                 deadline = self._get_html_text(item, mapping.get('deadline', ''))
                
#                 # ✅ Extraire l'URL depuis le HTML
#                 source_url = None
#                 if url_selector:
#                     link_element = item.select_one(url_selector)
#                     if link_element:
#                         href = link_element.get('href')
#                         if href:
#                             if href.startswith('/') and url_prefix:
#                                 source_url = f"{url_prefix}{href}"
#                             elif href.startswith('http'):
#                                 source_url = href
#                             else:
#                                 source_url = href
                
#                 # ✅ Si pas d'URL trouvée, utiliser le template
#                 if not source_url and url_template and reference:
#                     source_url = url_template.replace('{reference}', reference)
#                     if '{tender_id}' in source_url:
#                         source_url = None
                
#                 tender = {
#                     'reference': reference,
#                     'title': title,
#                     'buyer': buyer,
#                     'publication_date': publication_date,
#                     'deadline': deadline,
#                     'source_url': source_url,  # ✅ Ajouter l'URL
#                 }
                
#                 if tender['reference']:
#                     tenders.append(tender)
            
#             return tenders
            
#         except Exception as e:
#             logger.error(f"HTML scraping error: {e}")
#             return []
    
#     def _get_nested_value(self, data: Any, path: List[str], default: Any = None) -> Any:
#         """Get nested dictionary value by path"""
#         current = data
#         for key in path:
#             if not key:
#                 continue
#             if isinstance(current, dict):
#                 current = current.get(key)
#             elif isinstance(current, list):
#                 try:
#                     index = int(key) if key.isdigit() else 0
#                     current = current[index] if index < len(current) else default
#                 except (ValueError, IndexError):
#                     return default
#             else:
#                 return default
#         return current if current is not None else default
    
#     def _get_html_text(self, element, selector: str) -> str:
#         """Get text from HTML element using CSS selector"""
#         if not selector:
#             return ''
#         try:
#             selected = element.select_one(selector)
#             return selected.text.strip() if selected else ''
#         except:
#             return ''





# services/scrapers/dynamic_scraper.py
from services.scrapers.base_scraper import BaseScraper
import requests
import json
from typing import Dict, List, Any, Optional
import logging
import urllib3
import warnings
from datetime import datetime

# Disable all SSL warnings
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class DynamicScraper(BaseScraper):
    """Dynamic scraper for user-configured sources"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get('base_url')
        self.headers = json.loads(config.get('headers', '{}')) if isinstance(config.get('headers'), str) else config.get('headers', {})
        self.parser_config = json.loads(config.get('parser_config', '{}')) if isinstance(config.get('parser_config'), str) else config.get('parser_config', {})
        self.auth_config = json.loads(config.get('auth_config', '{}')) if isinstance(config.get('auth_config'), str) else config.get('auth_config', {})
        self.auth_type = config.get('auth_type', 'none')
        self.source_type = config.get('source_type', 'api')
    
    def validate_config(self) -> tuple[bool, str]:
        if not self.config.get('base_url'):
            return False, "Base URL is required"
        if not self.config.get('name'):
            return False, "Source name is required"
        return True, "Valid"
    
    def get_source_info(self) -> Dict[str, str]:
        return {
            'name': self.source_name,
            'display_name': self.display_name,
            'description': f'Dynamic source: {self.display_name}',
            'icon': '🔌',
            'type': self.source_type,
            'url': self.base_url
        }
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """Build authentication headers"""
        auth_headers = {}
        
        if self.auth_type == 'bearer':
            token = self.auth_config.get('token', '')
            if token:
                auth_headers['Authorization'] = f'Bearer {token}'
                
        elif self.auth_type == 'api_key':
            key = self.auth_config.get('api_key', '')
            key_name = self.auth_config.get('key_name', 'X-API-Key')
            if key:
                auth_headers[key_name] = key
                
        return auth_headers
    
    def _is_expired(self, deadline_str: str) -> bool:
        """Vérifier si un tender est expiré"""
        if not deadline_str or deadline_str == 'N/A':
            return False
        
        try:
            deadline_str = str(deadline_str).strip()
            
            # Essayer différents formats
            formats = [
                '%Y-%m-%d %H:%M:%S.%f',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y',
                '%b %d, %Y',
            ]
            
            for fmt in formats:
                try:
                    deadline_date = datetime.strptime(deadline_str, fmt)
                    return deadline_date < datetime.now()
                except:
                    continue
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking deadline {deadline_str}: {e}")
            return False
    
    def scrape_tenders(self, limit: int = 500) -> List[Dict[str, Any]]:
        """Scrape tenders from dynamic source"""
        try:
            headers = {**self.headers, **self._get_auth_headers()}
            
            if self.source_type == 'html':
                return self._scrape_html(limit, headers)
            else:
                return self._scrape_api(limit, headers)
                
        except Exception as e:
            logger.error(f"Dynamic scraping error for {self.source_name}: {e}")
            return []
    
    def _scrape_api(self, limit: int, headers: Dict) -> List[Dict]:
        """Scrape from API endpoint"""
        try:
            is_post = self.parser_config.get('method', 'GET').upper() == 'POST'
            
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            
            if is_post:
                payload = self.parser_config.get('payload', {})
                if 'pagination' in payload:
                    payload['pagination']['limit'] = limit
                
                logger.info(f"📤 POST request to {self.base_url}")
                response = session.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
            else:
                params = self.parser_config.get('params', {})
                params['length'] = limit
                
                logger.info(f"📤 GET request to {self.base_url}")
                response = session.get(
                    self.base_url,
                    headers=headers,
                    params=params,
                    timeout=30
                )
            
            session.close()
            
            if response.status_code != 200:
                logger.error(f"API error: {response.status_code}")
                return []
            
            data = response.json()
            
            # Find the data path
            path = self.parser_config.get('data_path', '').split('.')
            items = self._get_nested_value(data, path, [])
            
            if not items or not isinstance(items, list):
                logger.warning(f"No items found at data path: {path}")
                return []
            
            # Map fields
            mapping = self.parser_config.get('field_mapping', {})
            
            # Récupérer les champs pour l'URL
            url_template = self.parser_config.get('url_template', '')
            tender_id_field = mapping.get('tender_id', '')
            
            tenders = []
            skipped_expired = 0
            
            for item in items[:limit]:
                # Extraire les champs
                reference = str(self._get_nested_value(item, mapping.get('reference', '').split('.'), ''))
                title = self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title')
                buyer = self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown')
                publication_date = self._get_nested_value(item, mapping.get('publication_date', '').split('.'), '')
                deadline = self._get_nested_value(item, mapping.get('deadline', '').split('.'), '')
                
                # ✅ FILTRER : Vérifier si le tender est expiré
                if self._is_expired(deadline):
                    skipped_expired += 1
                    logger.debug(f"⏰ Skip expired tender {reference} (deadline: {deadline})")
                    continue
                
                # Construire l'URL
                source_url = None
                if url_template and tender_id_field and reference:
                    tender_id = str(self._get_nested_value(item, tender_id_field.split('.'), ''))
                    if tender_id:
                        source_url = url_template.replace('{tender_id}', tender_id).replace('{reference}', reference)
                elif url_template and reference:
                    source_url = url_template.replace('{reference}', reference)
                    if '{tender_id}' in source_url:
                        source_url = None
                
                tender = {
                    'reference': reference,
                    'title': title,
                    'buyer': buyer,
                    'publication_date': publication_date,
                    'deadline': deadline,
                    'source_url': source_url,
                }
                
                if tender['reference']:
                    tenders.append(tender)
            
            if skipped_expired > 0:
                logger.info(f"⏰ Skipped {skipped_expired} expired tenders")
            logger.info(f"✅ Found {len(tenders)} active tenders from {self.source_name}")
            return tenders
            
        except Exception as e:
            logger.error(f"API scraping error: {e}")
            return []
    
    def _scrape_html(self, limit: int, headers: Dict) -> List[Dict]:
        """Scrape from HTML page"""
        try:
            from bs4 import BeautifulSoup
            
            session = requests.Session()
            session.verify = False
            session.trust_env = False
            
            response = session.get(
                self.base_url,
                headers=headers,
                timeout=30
            )
            
            session.close()
            
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            selector = self.parser_config.get('item_selector', 'tr')
            items = soup.select(selector)
            
            mapping = self.parser_config.get('field_mapping', {})
            
            url_selector = self.parser_config.get('url_selector', '')
            url_prefix = self.parser_config.get('url_prefix', '')
            url_template = self.parser_config.get('url_template', '')
            
            tenders = []
            skipped_expired = 0
            
            for item in items[:limit]:
                reference = self._get_html_text(item, mapping.get('reference', ''))
                title = self._get_html_text(item, mapping.get('title', 'No title'))
                buyer = self._get_html_text(item, mapping.get('buyer', 'Unknown'))
                publication_date = self._get_html_text(item, mapping.get('publication_date', ''))
                deadline = self._get_html_text(item, mapping.get('deadline', ''))
                
                # ✅ FILTRER : Vérifier si le tender est expiré
                if self._is_expired(deadline):
                    skipped_expired += 1
                    logger.debug(f"⏰ Skip expired tender {reference} (deadline: {deadline})")
                    continue
                
                source_url = None
                if url_selector:
                    link_element = item.select_one(url_selector)
                    if link_element:
                        href = link_element.get('href')
                        if href:
                            if href.startswith('/') and url_prefix:
                                source_url = f"{url_prefix}{href}"
                            elif href.startswith('http'):
                                source_url = href
                            else:
                                source_url = href
                
                if not source_url and url_template and reference:
                    source_url = url_template.replace('{reference}', reference)
                    if '{tender_id}' in source_url:
                        source_url = None
                
                tender = {
                    'reference': reference,
                    'title': title,
                    'buyer': buyer,
                    'publication_date': publication_date,
                    'deadline': deadline,
                    'source_url': source_url,
                }
                
                if tender['reference']:
                    tenders.append(tender)
            
            if skipped_expired > 0:
                logger.info(f"⏰ Skipped {skipped_expired} expired tenders")
            logger.info(f"✅ Found {len(tenders)} active tenders from {self.source_name}")
            return tenders
            
        except Exception as e:
            logger.error(f"HTML scraping error: {e}")
            return []
    
    def _get_nested_value(self, data: Any, path: List[str], default: Any = None) -> Any:
        """Get nested dictionary value by path"""
        current = data
        for key in path:
            if not key:
                continue
            if isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                try:
                    index = int(key) if key.isdigit() else 0
                    current = current[index] if index < len(current) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default
        return current if current is not None else default
    
    def _get_html_text(self, element, selector: str) -> str:
        """Get text from HTML element using CSS selector"""
        if not selector:
            return ''
        try:
            selected = element.select_one(selector)
            return selected.text.strip() if selected else ''
        except:
            return ''
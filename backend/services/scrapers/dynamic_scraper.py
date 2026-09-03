# # services/scrapers/dynamic_scraper.py
# from services.scrapers.base_scraper import BaseScraper
# import requests
# import json
# from typing import Dict, List, Any, Optional  # Add this import!
# import logging

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
    
#     # def _scrape_api(self, limit: int, headers: Dict) -> List[Dict]:
#     #     """Scrape from API endpoint"""
#     #     try:
#     #         response = requests.get(
#     #             self.base_url,
#     #             headers=headers,
#     #             params=self.parser_config.get('params', {}),
#     #             timeout=30
#     #         )
            
#     #         if response.status_code != 200:
#     #             logger.error(f"API error: {response.status_code}")
#     #             return []
            
#     #         data = response.json()
            
#     #         # Find the data path
#     #         path = self.parser_config.get('data_path', '').split('.')
#     #         items = self._get_nested_value(data, path, [])
            
#     #         if not items or not isinstance(items, list):
#     #             logger.warning("No items found at data path")
#     #             return []
            
#     #         # Map fields
#     #         mapping = self.parser_config.get('field_mapping', {})
#     #         tenders = []
            
#     #         for item in items[:limit]:
#     #             tender = {
#     #                 'reference': str(self._get_nested_value(item, mapping.get('reference', '').split('.'), '')),
#     #                 'title': self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title'),
#     #                 'buyer': self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown'),
#     #                 'publication_date': self._get_nested_value(item, mapping.get('publication_date', '').split('.'), ''),
#     #                 'deadline': self._get_nested_value(item, mapping.get('deadline', '').split('.'), ''),
#     #             }
                
#     #             if tender['reference']:
#     #                 tenders.append(tender)
            
#     #         logger.info(f"Found {len(tenders)} tenders from {self.source_name}")
#     #         return tenders
            
#     #     except Exception as e:
#     #         logger.error(f"API scraping error: {e}")
#     #         return []

#     # services/scrapers/dynamic_scraper.py - Update _scrape_api method

# # services/scrapers/dynamic_scraper.py - Replace the _scrape_api method

#     # services/scrapers/dynamic_scraper.py - Replace the _scrape_api method

#     # services/scrapers/dynamic_scraper.py - Replace the _scrape_api method

# def _scrape_api(self, limit: int, headers: Dict) -> List[Dict]:
#     """Scrape from API endpoint"""
#     try:
#         is_post = self.parser_config.get('method', 'GET').upper() == 'POST'
        
#         if is_post:
#             payload = self.parser_config.get('payload', {})
#             if 'pagination' in payload:
#                 payload['pagination']['limit'] = limit
            
#             logger.info(f"📤 POST request to {self.base_url}")
#             response = requests.post(
#                 self.base_url,
#                 headers=headers,
#                 json=payload,
#                 timeout=30,
#                 verify=False  # ← Add this to bypass SSL verification
#             )
#         else:
#             params = self.parser_config.get('params', {})
#             params['length'] = limit
            
#             logger.info(f"📤 GET request to {self.base_url}")
#             response = requests.get(
#                 self.base_url,
#                 headers=headers,
#                 params=params,
#                 timeout=30,
#                 verify=False  # ← Add this to bypass SSL verification
#             )
        
#         if response.status_code != 200:
#             logger.error(f"API error: {response.status_code}")
#             return []
        
#         data = response.json()
        
#         # Find the data path
#         path = self.parser_config.get('data_path', '').split('.')
#         items = self._get_nested_value(data, path, [])
        
#         if not items or not isinstance(items, list):
#             logger.warning("No items found at data path")
#             return []
        
#         # Map fields
#         mapping = self.parser_config.get('field_mapping', {})
#         tenders = []
        
#         for item in items[:limit]:
#             tender = {
#                 'reference': str(self._get_nested_value(item, mapping.get('reference', '').split('.'), '')),
#                 'title': self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title'),
#                 'buyer': self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown'),
#                 'publication_date': self._get_nested_value(item, mapping.get('publication_date', '').split('.'), ''),
#                 'deadline': self._get_nested_value(item, mapping.get('deadline', '').split('.'), ''),
#             }
            
#             if tender['reference']:
#                 tenders.append(tender)
        
#         logger.info(f"✅ Found {len(tenders)} tenders from {self.source_name}")
#         return tenders
        
#     except Exception as e:
#         logger.error(f"API scraping error: {e}")
#         return []



    
#     def _scrape_html(self, limit: int, headers: Dict) -> List[Dict]:
#         """Scrape from HTML page"""
#         try:
#             from bs4 import BeautifulSoup
            
#             response = requests.get(
#                 self.base_url,
#                 headers=headers,
#                 timeout=30
#             )
            
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


# services/scrapers/dynamic_scraper.py
from services.scrapers.base_scraper import BaseScraper
import requests
import json
from typing import Dict, List, Any, Optional
import logging
import urllib3
import warnings

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
            
            # Create a new session for each request
            session = requests.Session()
            # Disable SSL verification
            session.verify = False
            # Disable SSL warnings for this session
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
            tenders = []
            
            for item in items[:limit]:
                tender = {
                    'reference': str(self._get_nested_value(item, mapping.get('reference', '').split('.'), '')),
                    'title': self._get_nested_value(item, mapping.get('title', '').split('.'), 'No title'),
                    'buyer': self._get_nested_value(item, mapping.get('buyer', '').split('.'), 'Unknown'),
                    'publication_date': self._get_nested_value(item, mapping.get('publication_date', '').split('.'), ''),
                    'deadline': self._get_nested_value(item, mapping.get('deadline', '').split('.'), ''),
                }
                
                if tender['reference']:
                    tenders.append(tender)
            
            logger.info(f"✅ Found {len(tenders)} tenders from {self.source_name}")
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
            tenders = []
            
            for item in items[:limit]:
                tender = {
                    'reference': self._get_html_text(item, mapping.get('reference', '')),
                    'title': self._get_html_text(item, mapping.get('title', 'No title')),
                    'buyer': self._get_html_text(item, mapping.get('buyer', 'Unknown')),
                    'publication_date': self._get_html_text(item, mapping.get('publication_date', '')),
                    'deadline': self._get_html_text(item, mapping.get('deadline', '')),
                }
                
                if tender['reference']:
                    tenders.append(tender)
            
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
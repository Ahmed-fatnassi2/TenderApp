# services/notification_service.py
import logging
from datetime import datetime
from typing import List, Dict, Optional
from models.user import User
from models.user_preferences import UserPreferences
from services.smart_construction_agent import SmartConstructionAgent
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.agent = SmartConstructionAgent()
        self.email_service = EmailService()
    
    def search_tenders_for_user(self, user: User) -> List[Dict]:
        """Search for tenders based on user preferences"""
        # ✅ FIX: Use 'preferences' not 'user_preferences'
        prefs = user.preferences
        
        # Build query from preferences
        query_parts = []
        
        if prefs and prefs.custom_prompt:
            query_parts.append(prefs.custom_prompt)
        
        if prefs and prefs.search_terms:
            search_terms = prefs.get_search_terms_list()
            if search_terms:
                query_parts.extend(search_terms)
        
        # Default if nothing specified
        if not query_parts:
            query_parts.append("IT tenders")
        
        query = ' '.join(query_parts)
        logger.info(f"🔍 Searching for user {user.id} with query: {query}")
        
        # Search using the agent
        result = self.agent.search_tenders(query, top_k=50)
        
        if not result.get('success'):
            return []
        
        documents = result.get('documents', [])
        tenders = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            
            # Apply filters if preferences exist
            if prefs and not self._apply_filters(metadata, prefs):
                continue
            
            tenders.append({
                'title': metadata.get('title', 'Untitled'),
                'reference': metadata.get('reference', 'N/A'),
                'buyer': metadata.get('buyer', 'Unknown'),
                'deadline': metadata.get('deadline', 'N/A'),
                'publication_date': metadata.get('publication_date', 'N/A'),
                'tender_id': metadata.get('tender_id'),
                'source': metadata.get('source', 'Unknown'),
                'content': doc.get('content', '')[:300]
            })
        
        return tenders
    
    def _apply_filters(self, metadata: Dict, prefs: UserPreferences) -> bool:
        """Apply filters from user preferences"""
        # Categories filter
        categories = prefs.get_categories_list()
        if categories:
            tender_categories = metadata.get('categories', '')
            if not any(cat.lower() in str(tender_categories).lower() for cat in categories):
                return False
        
        # Sources filter
        sources = prefs.get_sources_list()
        if sources:
            tender_source = metadata.get('source', '')
            if tender_source and tender_source not in sources:
                return False
        
        # Regions filter
        regions = prefs.get_regions_list()
        if regions:
            tender_region = metadata.get('region', '')
            if tender_region and not any(r.lower() in str(tender_region).lower() for r in regions):
                return False
        
        # Buyers filter
        buyers = prefs.get_buyers_list()
        if buyers:
            tender_buyer = metadata.get('buyer', '')
            if tender_buyer and not any(b.lower() in str(tender_buyer).lower() for b in buyers):
                return False
        
        return True
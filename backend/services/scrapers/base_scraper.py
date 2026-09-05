# # services/scrapers/base_scraper.py
# from abc import ABC, abstractmethod
# from typing import Dict, List, Any, Optional
# import logging
# from sqlalchemy import or_, and_

# logger = logging.getLogger(__name__)

# class BaseScraper(ABC):
#     """Abstract base class for all scrapers"""
    
#     def __init__(self, config: Dict[str, Any]):
#         self.config = config
#         self.source_name = config.get('name', 'unknown')
#         self.display_name = config.get('display_name', self.source_name)
    
#     @abstractmethod
#     def scrape_tenders(self, limit: int = 500) -> List[Dict[str, Any]]:
#         pass
    
#     @abstractmethod
#     def validate_config(self) -> tuple[bool, str]:
#         pass
    
#     @abstractmethod
#     def get_source_info(self) -> Dict[str, str]:
#         pass
    
#     def _check_duplicate(self, db, Tender, tender_data: Dict) -> tuple[bool, str]:
#         """Check if a tender is a duplicate using multiple strategies"""
        
#         reference = tender_data.get('reference', '')
#         title = tender_data.get('title', '')
#         buyer = tender_data.get('buyer', '')
#         deadline = tender_data.get('deadline', '')
#         publication_date = tender_data.get('publication_date', '')
        
#         # Strategy 1: Exact reference match (fastest)
#         if reference:
#             existing = Tender.query.filter_by(reference=reference).first()
#             if existing:
#                 return True, f"Duplicate by reference: {reference}"
        
#         # Strategy 2: Title + Buyer match (most reliable)
#         if title and buyer:
#             # Clean the title and buyer for comparison
#             clean_title = self._clean_text(title)
#             clean_buyer = self._clean_text(buyer)
            
#             existing = Tender.query.filter(
#                 and_(
#                     Tender.title.ilike(f'%{clean_title}%'),
#                     Tender.buyer.ilike(f'%{clean_buyer}%')
#                 )
#             ).first()
            
#             if existing:
#                 return True, f"Duplicate by title+buyer: {title[:50]}..."
        
#         # Strategy 3: Title + Deadline match
#         if title and deadline:
#             clean_title = self._clean_text(title)
            
#             existing = Tender.query.filter(
#                 and_(
#                     Tender.title.ilike(f'%{clean_title}%'),
#                     Tender.deadline == deadline
#                 )
#             ).first()
            
#             if existing:
#                 return True, f"Duplicate by title+deadline: {title[:50]}..."
        
#         # Strategy 4: Reference-like pattern match (for different formats)
#         # e.g., "20260807001" vs "Tender-20260807001"
#         if reference:
#             # Extract numbers from reference
#             ref_numbers = ''.join(filter(str.isdigit, reference))
#             if len(ref_numbers) >= 8:  # At least 8 digits (likely a date-based reference)
#                 existing = Tender.query.filter(
#                     Tender.reference.ilike(f'%{ref_numbers}%')
#                 ).first()
#                 if existing:
#                     return True, f"Duplicate by reference pattern: {ref_numbers}"
        
#         # Strategy 5: Title + Publication Date match
#         if title and publication_date:
#             clean_title = self._clean_text(title)
#             # Extract date part (YYYY-MM-DD)
#             pub_date = publication_date[:10] if publication_date else ''
            
#             if pub_date:
#                 existing = Tender.query.filter(
#                     and_(
#                         Tender.title.ilike(f'%{clean_title}%'),
#                         Tender.publication_date.ilike(f'%{pub_date}%')
#                     )
#                 ).first()
                
#                 if existing:
#                     return True, f"Duplicate by title+publication date: {title[:50]}..."
        
#         return False, "No duplicate found"
    
#     def _clean_text(self, text: str) -> str:
#         """Clean text for comparison"""
#         if not text:
#             return ''
#         # Remove extra spaces, special characters, and convert to lowercase
#         import re
#         text = text.lower()
#         text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
#         text = re.sub(r'\s+', ' ', text)      # Remove extra spaces
#         return text.strip()
    
#     def save_tenders(self, db, Tender, tenders: List[Dict]) -> Dict:
#         """Save scraped tenders to database with smart duplicate detection"""
#         from datetime import datetime
        
#         new_tender_ids = []
#         count_new = 0
#         count_duplicate = 0
#         duplicate_details = []
        
#         for data in tenders:
#             # Check if tender is a duplicate
#             is_duplicate, reason = self._check_duplicate(db, Tender, data)
            
#             if is_duplicate:
#                 count_duplicate += 1
#                 duplicate_details.append({
#                     'reference': data.get('reference', 'unknown'),
#                     'title': data.get('title', '')[:50],
#                     'reason': reason
#                 })
#                 continue
            
#             # Create new tender
#             tender = Tender(
#                 reference=data.get('reference', ''),
#                 buyer=data.get('buyer', 'Unknown')[:200],
#                 publication_date=data.get('publication_date', ''),
#                 title=data.get('title', 'No title')[:500],
#                 deadline=data.get('deadline', ''),
#                 source=self.source_name,
#                 scraped_at=datetime.utcnow()
#             )
            
#             db.session.add(tender)
#             db.session.flush()
#             new_tender_ids.append(tender.id)
#             count_new += 1
        
#         db.session.commit()
        
#         # Log duplicate details
#         if duplicate_details:
#             logger.info(f"🚫 Skipped {len(duplicate_details)} duplicates:")
#             for detail in duplicate_details[:5]:  # Show first 5
#                 logger.info(f"  - {detail['reason']}")
        
#         return {
#             'new': count_new,
#             'duplicates': count_duplicate,
#             'total': Tender.query.count(),
#             'new_tender_ids': new_tender_ids,
#             'source': self.source_name,
#             'duplicate_details': duplicate_details
#         }





# services/scrapers/base_scraper.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging
from sqlalchemy import or_, and_

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Abstract base class for all scrapers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.source_name = config.get('name', 'unknown')
        self.display_name = config.get('display_name', self.source_name)
    
    @abstractmethod
    def scrape_tenders(self, limit: int = 500) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def validate_config(self) -> tuple[bool, str]:
        pass
    
    @abstractmethod
    def get_source_info(self) -> Dict[str, str]:
        pass
    
    def _check_duplicate(self, db, Tender, tender_data: Dict) -> tuple[bool, str]:
        """Check if a tender is a duplicate using multiple strategies"""
        
        reference = tender_data.get('reference', '')
        title = tender_data.get('title', '')
        buyer = tender_data.get('buyer', '')
        deadline = tender_data.get('deadline', '')
        publication_date = tender_data.get('publication_date', '')
        
        # Strategy 1: Exact reference match (fastest)
        if reference:
            existing = Tender.query.filter_by(reference=reference).first()
            if existing:
                return True, f"Duplicate by reference: {reference}"
        
        # Strategy 2: Title + Buyer match (most reliable)
        if title and buyer:
            clean_title = self._clean_text(title)
            clean_buyer = self._clean_text(buyer)
            
            existing = Tender.query.filter(
                and_(
                    Tender.title.ilike(f'%{clean_title}%'),
                    Tender.buyer.ilike(f'%{clean_buyer}%')
                )
            ).first()
            
            if existing:
                return True, f"Duplicate by title+buyer: {title[:50]}..."
        
        # Strategy 3: Title + Deadline match
        if title and deadline:
            clean_title = self._clean_text(title)
            
            existing = Tender.query.filter(
                and_(
                    Tender.title.ilike(f'%{clean_title}%'),
                    Tender.deadline == deadline
                )
            ).first()
            
            if existing:
                return True, f"Duplicate by title+deadline: {title[:50]}..."
        
        # Strategy 4: Reference-like pattern match
        if reference:
            ref_numbers = ''.join(filter(str.isdigit, reference))
            if len(ref_numbers) >= 8:
                existing = Tender.query.filter(
                    Tender.reference.ilike(f'%{ref_numbers}%')
                ).first()
                if existing:
                    return True, f"Duplicate by reference pattern: {ref_numbers}"
        
        # Strategy 5: Title + Publication Date match
        if title and publication_date:
            clean_title = self._clean_text(title)
            pub_date = publication_date[:10] if publication_date else ''
            
            if pub_date:
                existing = Tender.query.filter(
                    and_(
                        Tender.title.ilike(f'%{clean_title}%'),
                        Tender.publication_date.ilike(f'%{pub_date}%')
                    )
                ).first()
                
                if existing:
                    return True, f"Duplicate by title+publication date: {title[:50]}..."
        
        return False, "No duplicate found"
    
    def _clean_text(self, text: str) -> str:
        """Clean text for comparison"""
        if not text:
            return ''
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def save_tenders(self, db, Tender, tenders: List[Dict]) -> Dict:
        """Save scraped tenders to database with smart duplicate detection"""
        from datetime import datetime
        
        new_tender_ids = []
        count_new = 0
        count_duplicate = 0
        duplicate_details = []
        
        for data in tenders:
            # Check if tender is a duplicate
            is_duplicate, reason = self._check_duplicate(db, Tender, data)
            
            if is_duplicate:
                count_duplicate += 1
                duplicate_details.append({
                    'reference': data.get('reference', 'unknown'),
                    'title': data.get('title', '')[:50],
                    'reason': reason
                })
                continue
            
            # ✅ Créer le tender AVEC source_url (colonne existe déjà)
            tender = Tender(
                reference=data.get('reference', ''),
                buyer=data.get('buyer', 'Unknown')[:200],
                publication_date=data.get('publication_date', ''),
                title=data.get('title', 'No title')[:500],
                deadline=data.get('deadline', ''),
                source=self.source_name,
                source_url=data.get('source_url', ''),  # ✅ Utiliser la colonne existante
                scraped_at=datetime.utcnow()
            )
            
            db.session.add(tender)
            db.session.flush()
            new_tender_ids.append(tender.id)
            count_new += 1
        
        db.session.commit()
        
        if duplicate_details:
            logger.info(f"🚫 Skipped {len(duplicate_details)} duplicates:")
            for detail in duplicate_details[:5]:
                logger.info(f"  - {detail['reason']}")
        
        return {
            'new': count_new,
            'duplicates': count_duplicate,
            'total': Tender.query.count(),
            'new_tender_ids': new_tender_ids,
            'source': self.source_name,
            'duplicate_details': duplicate_details
        }
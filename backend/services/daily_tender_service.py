# import os
# import logging
# from datetime import datetime, timedelta
# from typing import List, Dict, Any
# from services.smart_construction_agent import SmartConstructionAgent
# from services.email_service import EmailService
# from dotenv import load_dotenv

# load_dotenv()

# logger = logging.getLogger(__name__)

# class DailyTenderService:
#     def __init__(self):
#         self.agent = SmartConstructionAgent()
#         self.email_service = EmailService()
        
#     def get_tenders_this_month(self) -> List[Dict]:
#         """Get all construction tenders from this month"""
#         try:
#             # Search with multiple construction-related terms
#             search_terms = [
#                 "travaux",
#                 "route",
#                 "génie civil",
#                 "bâtiment",
#                 "infrastructure",
#                 "construction",
#             ]
            
#             all_tenders = []
#             seen_references = set()
#             current_month = datetime.now().month
#             current_year = datetime.now().year
            
#             for term in search_terms:
#                 logger.info(f"🔍 Searching for: {term}")
#                 search_result = self.agent.search_tenders(term, top_k=30)
                
#                 if not search_result.get('success'):
#                     continue
                
#                 documents = search_result.get('documents', [])
                
#                 for doc in documents:
#                     metadata = doc.get('metadata', {})
#                     reference = metadata.get('reference', '')
                    
#                     # Avoid duplicates
#                     if reference in seen_references:
#                         continue
#                     seen_references.add(reference)
                    
#                     # Check if it's from this month
#                     indexed_at_str = metadata.get('indexed_at', '')
#                     include = True
                    
#                     if indexed_at_str:
#                         try:
#                             if 'T' in indexed_at_str:
#                                 date_part = indexed_at_str.split('T')[0]
#                                 pub_date = datetime.strptime(date_part, '%Y-%m-%d')
#                             else:
#                                 pub_date = datetime.strptime(indexed_at_str[:10], '%Y-%m-%d')
                            
#                             # Check if same month and year
#                             if pub_date.month != current_month or pub_date.year != current_year:
#                                 include = False
#                         except:
#                             # If date parsing fails, include it anyway
#                             pass
                    
#                     if include:
#                         # Get title from metadata or fallback
#                         title = metadata.get('title', '')
#                         if not title:
#                             content = doc.get('content', '')
#                             import re
#                             title_match = re.search(r'Title:\s*([^\n]+)', content)
#                             if title_match:
#                                 title = title_match.group(1).strip()
#                             else:
#                                 title = f"Tender {reference or 'N/A'}"
                        
#                         all_tenders.append({
#                             'title': title or 'Untitled',
#                             'reference': reference or 'N/A',
#                             'buyer': metadata.get('buyer', 'Unknown'),
#                             'indexed_at': indexed_at_str or 'Recent',
#                             'deadline': metadata.get('deadline', 'N/A'),
#                             'source': metadata.get('source', 'OpenRAG'),
#                             'tender_id': metadata.get('tender_id', 'N/A')
#                         })
            
#             logger.info(f"📊 Found {len(all_tenders)} unique construction tenders this month")
#             return all_tenders
            
#         except Exception as e:
#             logger.error(f"Error getting tenders: {e}")
#             return []

#     def get_new_tenders_last_24h(self) -> List[Dict]:
#         """Get tenders from the last 24 hours"""
#         try:
#             search_terms = [
#                 "travaux",
#                 "route",
#                 "génie civil",
#                 "bâtiment",
#                 "infrastructure",
#                 "construction",
#             ]
            
#             all_tenders = []
#             seen_references = set()
#             cutoff_time = datetime.now() - timedelta(days=1)
            
#             for term in search_terms:
#                 logger.info(f"🔍 Searching for: {term}")
#                 search_result = self.agent.search_tenders(term, top_k=30)
                
#                 if not search_result.get('success'):
#                     continue
                
#                 documents = search_result.get('documents', [])
                
#                 for doc in documents:
#                     metadata = doc.get('metadata', {})
#                     reference = metadata.get('reference', '')
                    
#                     if reference in seen_references:
#                         continue
#                     seen_references.add(reference)
                    
#                     indexed_at_str = metadata.get('indexed_at', '')
#                     if indexed_at_str:
#                         try:
#                             if 'T' in indexed_at_str:
#                                 date_part = indexed_at_str.split('T')[0]
#                                 pub_date = datetime.strptime(date_part, '%Y-%m-%d')
#                             else:
#                                 pub_date = datetime.strptime(indexed_at_str[:10], '%Y-%m-%d')
                            
#                             if pub_date >= cutoff_time:
#                                 title = metadata.get('title', '')
#                                 if not title:
#                                     content = doc.get('content', '')
#                                     import re
#                                     title_match = re.search(r'Title:\s*([^\n]+)', content)
#                                     if title_match:
#                                         title = title_match.group(1).strip()
#                                     else:
#                                         title = f"Tender {reference or 'N/A'}"
                                
#                                 all_tenders.append({
#                                     'title': title or 'Untitled',
#                                     'reference': reference or 'N/A',
#                                     'buyer': metadata.get('buyer', 'Unknown'),
#                                     'indexed_at': indexed_at_str,
#                                     'deadline': metadata.get('deadline', 'N/A'),
#                                     'source': metadata.get('source', 'OpenRAG'),
#                                     'tender_id': metadata.get('tender_id', 'N/A')
#                                 })
#                         except:
#                             pass
            
#             logger.info(f"📊 Found {len(all_tenders)} unique construction tenders in the last 24 hours")
#             return all_tenders
            
#         except Exception as e:
#             logger.error(f"Error getting new tenders: {e}")
#             return []

#     def send_daily_digest(self, recipient_email: str = None) -> bool:
#         """Send daily digest email"""
#         try:
#             recipient = recipient_email or os.getenv('DAILY_DIGEST_EMAIL')
#             if not recipient:
#                 logger.error("No recipient email configured")
#                 return False
            
#             # First try to get tenders from last 24 hours
#             tenders = self.get_new_tenders_last_24h()
            
#             # If none found, get this month's tenders
#             if not tenders:
#                 logger.info("No tenders in last 24 hours, getting this month's tenders...")
#                 tenders = self.get_tenders_this_month()
            
#             today = datetime.now().strftime('%B %d, %Y')
            
#             if not tenders:
#                 logger.info("No tenders found at all")
#                 html_content = self.email_service.format_tenders_html([], today)
#                 plain_text = f"Construction Tenders - {today}\n\nNo construction tenders found."
#             else:
#                 html_content = self.email_service.format_tenders_html(tenders, today)
#                 plain_text = f"Construction Tenders - {today}\n\n"
#                 plain_text += f"Found {len(tenders)} construction tenders this month.\n\n"
#                 for tender in tenders[:10]:
#                     plain_text += f"- {tender['title']}\n"
#                     plain_text += f"  Reference: {tender['reference']}\n"
#                     plain_text += f"  Buyer: {tender['buyer']}\n"
#                     plain_text += f"  Deadline: {tender['deadline']}\n\n"
            
#             # Send email
#             subject = f"🏗️ Construction Tenders - {today}"
#             success = self.email_service.send_email(
#                 to_email=recipient,
#                 subject=subject,
#                 html_content=html_content,
#                 plain_text=plain_text
#             )
            
#             if success:
#                 logger.info(f"✅ Daily digest sent to {recipient} ({len(tenders)} tenders)")
#             return success
            
#         except Exception as e:
#             logger.error(f"Error sending daily digest: {e}")
#             return False





# services/daily_tender_service.py - Updated with proper messages and dates

import os
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from services.smart_construction_agent import SmartConstructionAgent
from services.email_service import EmailService
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DailyTenderService:
    def __init__(self):
        self.agent = SmartConstructionAgent()
        self.email_service = EmailService()
        
    def get_tenders_this_month(self) -> List[Dict]:
        """Get all construction tenders from this month"""
        try:
            search_terms = [
                "travaux",
                "route",
                "génie civil",
                "bâtiment",
                "infrastructure",
                "construction",
            ]
            
            all_tenders = []
            seen_references = set()
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            for term in search_terms:
                logger.info(f"🔍 Searching for: {term}")
                search_result = self.agent.search_tenders(term, top_k=30)
                
                if not search_result.get('success'):
                    continue
                
                documents = search_result.get('documents', [])
                
                for doc in documents:
                    metadata = doc.get('metadata', {})
                    reference = metadata.get('reference', '')
                    
                    if reference in seen_references:
                        continue
                    seen_references.add(reference)
                    
                    indexed_at_str = metadata.get('indexed_at', '')
                    include = True
                    publication_date = indexed_at_str
                    
                    if indexed_at_str:
                        try:
                            if 'T' in indexed_at_str:
                                date_part = indexed_at_str.split('T')[0]
                                pub_date = datetime.strptime(date_part, '%Y-%m-%d')
                            else:
                                pub_date = datetime.strptime(indexed_at_str[:10], '%Y-%m-%d')
                            
                            # Format date for display
                            publication_date = pub_date.strftime('%d/%m/%Y')
                            
                            # Check if same month and year
                            if pub_date.month != current_month or pub_date.year != current_year:
                                include = False
                        except:
                            # If date parsing fails, use the original string
                            publication_date = indexed_at_str
                    
                    if include:
                        title = metadata.get('title', '')
                        if not title:
                            content = doc.get('content', '')
                            import re
                            title_match = re.search(r'Title:\s*([^\n]+)', content)
                            if title_match:
                                title = title_match.group(1).strip()
                            else:
                                title = f"Tender {reference or 'N/A'}"
                        
                        all_tenders.append({
                            'title': title or 'Untitled',
                            'reference': reference or 'N/A',
                            'buyer': metadata.get('buyer', 'Unknown'),
                            'indexed_at': publication_date,  # Now formatted date
                            'deadline': metadata.get('deadline', 'N/A'),
                            'source': metadata.get('source', 'OpenRAG'),
                            'tender_id': metadata.get('tender_id', 'N/A')
                        })
            
            logger.info(f"📊 Found {len(all_tenders)} unique construction tenders this month")
            return all_tenders
            
        except Exception as e:
            logger.error(f"Error getting tenders: {e}")
            return []

    def get_new_tenders_last_24h(self) -> List[Dict]:
        """Get tenders from the last 24 hours with proper dates"""
        try:
            search_terms = [
                "travaux",
                "route",
                "génie civil",
                "bâtiment",
                "infrastructure",
                "construction",
            ]
            
            all_tenders = []
            seen_references = set()
            cutoff_time = datetime.now() - timedelta(days=1)
            
            for term in search_terms:
                logger.info(f"🔍 Searching for: {term}")
                search_result = self.agent.search_tenders(term, top_k=30)
                
                if not search_result.get('success'):
                    continue
                
                documents = search_result.get('documents', [])
                
                for doc in documents:
                    metadata = doc.get('metadata', {})
                    reference = metadata.get('reference', '')
                    
                    if reference in seen_references:
                        continue
                    seen_references.add(reference)
                    
                    indexed_at_str = metadata.get('indexed_at', '')
                    if indexed_at_str:
                        try:
                            if 'T' in indexed_at_str:
                                date_part = indexed_at_str.split('T')[0]
                                pub_date = datetime.strptime(date_part, '%Y-%m-%d')
                            else:
                                pub_date = datetime.strptime(indexed_at_str[:10], '%Y-%m-%d')
                            
                            # Format date for display
                            publication_date = pub_date.strftime('%d/%m/%Y')
                            
                            if pub_date >= cutoff_time:
                                title = metadata.get('title', '')
                                if not title:
                                    content = doc.get('content', '')
                                    import re
                                    title_match = re.search(r'Title:\s*([^\n]+)', content)
                                    if title_match:
                                        title = title_match.group(1).strip()
                                    else:
                                        title = f"Tender {reference or 'N/A'}"
                                
                                all_tenders.append({
                                    'title': title or 'Untitled',
                                    'reference': reference or 'N/A',
                                    'buyer': metadata.get('buyer', 'Unknown'),
                                    'indexed_at': publication_date,
                                    'deadline': metadata.get('deadline', 'N/A'),
                                    'source': metadata.get('source', 'OpenRAG'),
                                    'tender_id': metadata.get('tender_id', 'N/A')
                                })
                        except:
                            pass
            
            logger.info(f"📊 Found {len(all_tenders)} unique construction tenders in the last 24 hours")
            return all_tenders
            
        except Exception as e:
            logger.error(f"Error getting new tenders: {e}")
            return []

    def send_daily_digest(self, recipient_email: str = None) -> bool:
        """Send daily digest email with clear messaging"""
        try:
            recipient = recipient_email or os.getenv('DAILY_DIGEST_EMAIL')
            if not recipient:
                logger.error("No recipient email configured")
                return False
            
            today = datetime.now().strftime('%B %d, %Y')
            
            # First try to get tenders from last 24 hours
            logger.info("🔍 Looking for tenders from the last 24 hours...")
            tenders_24h = self.get_new_tenders_last_24h()
            
            # Prepare the email content
            html_content = ''
            plain_text = f"Construction Tenders - {today}\n\n"
            
            # Section 1: Last 24 hours
            html_content += f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #1a237e; margin: 0;">📊 New Tenders (Last 24 Hours)</h3>
            </div>
            """
            plain_text += f"{'='*50}\n"
            plain_text += f"📊 NEW TENDERS (LAST 24 HOURS)\n"
            plain_text += f"{'='*50}\n\n"
            
            if tenders_24h:
                html_content += f"""
                <div style="background: #e8f5e9; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #2e7d32; margin: 0;">✅ Found {len(tenders_24h)} new tenders in the last 24 hours</p>
                </div>
                """
                plain_text += f"✅ Found {len(tenders_24h)} new tenders in the last 24 hours\n\n"
                
                # Add the 24h tenders
                for tender in tenders_24h:
                    html_content += self._tender_to_html(tender)
                    plain_text += self._tender_to_text(tender)
            else:
                html_content += """
                <div style="background: #fff3e0; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #e65100; margin: 0;">ℹ️ No new tenders found in the last 24 hours</p>
                </div>
                """
                plain_text += "ℹ️ No new tenders found in the last 24 hours\n\n"
            
            # Section 2: This month's tenders
            html_content += f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #1a237e; margin: 0;">📅 This Month's Tenders ({datetime.now().strftime('%B %Y')})</h3>
            </div>
            """
            plain_text += f"\n{'='*50}\n"
            plain_text += f"📅 THIS MONTH'S TENDERS ({datetime.now().strftime('%B %Y')})\n"
            plain_text += f"{'='*50}\n\n"
            
            # Get this month's tenders
            tenders_month = self.get_tenders_this_month()
            
            if tenders_month:
                html_content += f"""
                <div style="background: #e8f5e9; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #2e7d32; margin: 0;">📊 Found {len(tenders_month)} tenders this month</p>
                </div>
                """
                plain_text += f"📊 Found {len(tenders_month)} tenders this month\n\n"
                
                # Add the month's tenders
                for tender in tenders_month:
                    html_content += self._tender_to_html(tender)
                    plain_text += self._tender_to_text(tender)
            else:
                html_content += """
                <div style="background: #fff3e0; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #e65100; margin: 0;">ℹ️ No tenders found this month</p>
                </div>
                """
                plain_text += "ℹ️ No tenders found this month\n\n"
            
            # Send email
            subject = f"🏗️ Construction Tenders - {today}"
            success = self.email_service.send_email(
                to_email=recipient,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text
            )
            
            if success:
                logger.info(f"✅ Daily digest sent to {recipient} ({len(tenders_24h)} new, {len(tenders_month)} this month)")
            return success
            
        except Exception as e:
            logger.error(f"Error sending daily digest: {e}")
            return False
    
    def _tender_to_html(self, tender: Dict) -> str:
        """Convert a single tender to HTML format"""
        return f"""
        <div style="background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #1a237e;">
            <div style="font-size: 16px; font-weight: bold; color: #1a237e;">{tender.get('title', 'Untitled')}</div>
            <div style="color: #666; font-size: 14px; margin: 5px 0;">
                <strong>Reference:</strong> {tender.get('reference', 'N/A')}
            </div>
            <div style="color: #666; font-size: 14px; margin: 5px 0;">
                <strong>Buyer:</strong> {tender.get('buyer', 'Unknown')}
            </div>
            <div style="color: #666; font-size: 14px; margin: 5px 0;">
                <strong>Publication Date:</strong> {tender.get('indexed_at', 'N/A')}
            </div>
            <div style="color: #d32f2f; font-size: 14px; margin: 5px 0; font-weight: bold;">
                <strong>Deadline:</strong> {tender.get('deadline', 'N/A')}
            </div>
        </div>
        """
    
    def _tender_to_text(self, tender: Dict) -> str:
        """Convert a single tender to plain text"""
        return f"""
Title: {tender.get('title', 'Untitled')}
Reference: {tender.get('reference', 'N/A')}
Buyer: {tender.get('buyer', 'Unknown')}
Publication Date: {tender.get('indexed_at', 'N/A')}
Deadline: {tender.get('deadline', 'N/A')}
{'-'*50}
"""
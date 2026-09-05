# services/it_notification_service.py - COMPLETE WITH 31-DAY FALLBACK
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from models.user import User
from services.agent_service import TenderAgent
from services.email_service import EmailService
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ITNotificationService:
    """Service for sending IT tender notifications based on user preferences"""
    
    def __init__(self):
        print("🔍 [DEBUG] ITNotificationService.__init__ called")
        self.agent = TenderAgent()
        self.email_service = EmailService()
        print(f"🔍 [DEBUG] SMTP_USER: {os.getenv('SMTP_USER')}")
        print(f"🔍 [DEBUG] SMTP_PASSWORD set: {'Yes' if os.getenv('SMTP_PASSWORD') else 'No'}")
    
    def search_it_tenders_for_user(self, user: User, days_back: int = 1) -> List[Dict]:
        """Search for IT tenders based on user preferences"""
        try:
            prefs = user.preferences
            if not prefs:
                logger.info(f"No preferences found for user {user.id}, using default")
                query = "IT tenders software development"
            else:
                query_parts = []
                
                if prefs.custom_prompt:
                    query_parts.append(prefs.custom_prompt)
                
                if prefs.search_terms:
                    search_terms = prefs.get_search_terms_list()
                    if search_terms:
                        query_parts.extend(search_terms)
                
                if not query_parts:
                    query_parts.append("IT tenders")
                
                query = ' '.join(query_parts)
            
            logger.info(f"🔍 Searching for user {user.id} with query: {query}")
            print(f"🔍 [DEBUG] Search query: {query}")
            
            results = self.agent.search_tenders(query)
            
            if not results:
                logger.info(f"No tenders found for user {user.id}")
                return []
            
            cutoff_time = datetime.now() - timedelta(days=days_back)
            filtered_tenders = []
            seen_references = set()
            
            for tender in results:
                # Check if it's IT-related
                is_it = tender.get('is_it', False)
                if not is_it:
                    continue
                
                reference = tender.get('reference', '')
                if reference in seen_references:
                    continue
                seen_references.add(reference)
                
                publication_date = tender.get('publication_date', '')
                if not self._is_within_timeframe(publication_date, cutoff_time):
                    indexed_at = tender.get('indexed_at', '')
                    if not self._is_within_timeframe(indexed_at, cutoff_time):
                        continue
                
                # Format date for display
                display_date = self._format_date(publication_date or indexed_at)
                
                # filtered_tenders.append({
                #     'reference': tender.get('reference', 'N/A'),
                #     'title': tender.get('title', 'Untitled'),
                #     'buyer': tender.get('buyer', 'Unknown'),
                #     'deadline': tender.get('deadline', 'N/A'),
                #     'publication_date': display_date,
                #     'source': tender.get('source', 'Unknown'),
                #     'is_it': is_it,
                #     'it_confidence': tender.get('it_confidence', 'None'),
                #     'ai_score': tender.get('ai_score', 0),
                #     'content': tender.get('content', '')[:300],
                #     'category': tender.get('category', 'other'),
                # })
                filtered_tenders.append({
                    'reference': tender.get('reference', 'N/A'),
                    'title': tender.get('title', 'Untitled'),
                    'buyer': tender.get('buyer', 'Unknown'),
                    'deadline': tender.get('deadline', 'N/A'),
                    'publication_date': display_date,
                    'source': tender.get('source', 'Unknown'),
                    'source_url': tender.get('source_url', ''),  # ✅ AJOUT
                    'is_it': is_it,
                    'it_confidence': tender.get('it_confidence', 'None'),
                    'ai_score': tender.get('ai_score', 0),
                    'content': tender.get('content', '')[:300],
                    'category': tender.get('category', 'other'),
                })
            
            logger.info(f"✅ Found {len(filtered_tenders)} IT tenders from the last {days_back} day(s)")
            print(f"✅ [DEBUG] Found {len(filtered_tenders)} IT tenders")
            return filtered_tenders
            
        except Exception as e:
            logger.error(f"Error searching IT tenders for user {user.id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_tenders_last_31_days(self, user: User) -> List[Dict]:
        """Get all IT tenders from the last 31 days"""
        try:
            prefs = user.preferences
            if not prefs:
                query = "IT tenders software development"
            else:
                query_parts = []
                
                if prefs.custom_prompt:
                    query_parts.append(prefs.custom_prompt)
                
                if prefs.search_terms:
                    search_terms = prefs.get_search_terms_list()
                    if search_terms:
                        query_parts.extend(search_terms)
                
                if not query_parts:
                    query_parts.append("IT tenders")
                
                query = ' '.join(query_parts)
            
            logger.info(f"🔍 Getting IT tenders from last 31 days for user {user.id}")
            print(f"🔍 [DEBUG] 31-day search query: {query}")
            
            results = self.agent.search_tenders(query)
            
            if not results:
                return []
            
            cutoff_time = datetime.now() - timedelta(days=31)
            all_tenders = []
            seen_references = set()
            
            for tender in results:
                is_it = tender.get('is_it', False)
                if not is_it:
                    continue
                
                reference = tender.get('reference', '')
                if reference in seen_references:
                    continue
                seen_references.add(reference)
                
                publication_date = tender.get('publication_date', '')
                indexed_at = tender.get('indexed_at', '')
                date_str = publication_date or indexed_at
                
                include = True
                display_date = 'N/A'
                
                if date_str:
                    try:
                        if 'T' in date_str:
                            date_part = date_str.split('T')[0]
                            pub_date = datetime.strptime(date_part, '%Y-%m-%d')
                        elif '/' in date_str:
                            pub_date = datetime.strptime(date_str, '%d/%m/%Y')
                        else:
                            pub_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
                        
                        display_date = pub_date.strftime('%d/%m/%Y')
                        
                        # Check if within last 31 days
                        if pub_date < cutoff_time.date():
                            include = False
                    except:
                        pass
                
                if include:
                    # all_tenders.append({
                    #     'reference': tender.get('reference', 'N/A'),
                    #     'title': tender.get('title', 'Untitled'),
                    #     'buyer': tender.get('buyer', 'Unknown'),
                    #     'deadline': tender.get('deadline', 'N/A'),
                    #     'publication_date': display_date,
                    #     'source': tender.get('source', 'Unknown'),
                    #     'is_it': is_it,
                    #     'it_confidence': tender.get('it_confidence', 'None'),
                    #     'ai_score': tender.get('ai_score', 0),
                    #     'category': tender.get('category', 'other'),
                    # })
                    all_tenders.append({
                        'reference': tender.get('reference', 'N/A'),
                        'title': tender.get('title', 'Untitled'),
                        'buyer': tender.get('buyer', 'Unknown'),
                        'deadline': tender.get('deadline', 'N/A'),
                        'publication_date': display_date,
                        'source': tender.get('source', 'Unknown'),
                        'source_url': tender.get('source_url', ''),  # ✅ AJOUT
                        'is_it': is_it,
                        'it_confidence': tender.get('it_confidence', 'None'),
                        'ai_score': tender.get('ai_score', 0),
                        'category': tender.get('category', 'other'),
                    })
            
            logger.info(f"📊 Found {len(all_tenders)} IT tenders from the last 31 days")
            print(f"📊 [DEBUG] Found {len(all_tenders)} IT tenders from the last 31 days")
            return all_tenders
            
        except Exception as e:
            logger.error(f"Error getting IT tenders from last 31 days for user {user.id}: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def _is_within_timeframe(self, date_str: str, cutoff_time: datetime) -> bool:
        """Check if a date string is within the timeframe"""
        if not date_str or date_str == 'N/A':
            return False
        
        try:
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
                pub_date = datetime.strptime(date_part, '%Y-%m-%d')
            elif '/' in date_str:
                pub_date = datetime.strptime(date_str, '%d/%m/%Y')
            else:
                pub_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
            
            return pub_date >= cutoff_time.date()
        except Exception as e:
            logger.debug(f"Could not parse date '{date_str}': {e}")
            return False
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        
        try:
            if 'T' in date_str:
                date_part = date_str.split('T')[0]
                pub_date = datetime.strptime(date_part, '%Y-%m-%d')
            elif '/' in date_str:
                pub_date = datetime.strptime(date_str, '%d/%m/%Y')
            else:
                pub_date = datetime.strptime(date_str[:10], '%Y-%m-%d')
            
            return pub_date.strftime('%d/%m/%Y')
        except Exception as e:
            return date_str
    
    def send_daily_digest_for_user(self, user: User) -> bool:
        """Send daily IT tender digest to a specific user with 31-day fallback"""
        try:
            print("=" * 60)
            print(f"🔍 [DEBUG] send_daily_digest_for_user START for user {user.id}")
            print(f"🔍 [DEBUG] User email: {user.email}")
            
            # Check preferences
            if not user.preferences:
                print(f"❌ [DEBUG] No preferences for user {user.id}")
                return False
            
            if not user.preferences.notifications_enabled:
                print(f"❌ [DEBUG] Notifications disabled for user {user.id}")
                return False
            
            today = datetime.now().strftime('%B %d, %Y')
            
            # FIRST: Try to get tenders from last 24 hours
            print(f"🔍 [DEBUG] Looking for IT tenders from the last 24 hours...")
            tenders_24h = self.search_it_tenders_for_user(user, days_back=1)
            print(f"🔍 [DEBUG] Found {len(tenders_24h)} IT tenders in the last 24 hours")
            
            # Build the email content with TWO sections
            html_content = ""
            plain_text = f"💻 IT Tender Digest - {today}\n\n"
            
            # SECTION 1: Last 24 hours
            html_content += f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #1a237e; margin: 0;">📊 New IT Tenders (Last 24 Hours)</h3>
            </div>
            """
            plain_text += f"{'='*50}\n"
            plain_text += f"📊 NEW IT TENDERS (LAST 24 HOURS)\n"
            plain_text += f"{'='*50}\n\n"
            
            if tenders_24h:
                html_content += f"""
                <div style="background: #e8f5e9; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #2e7d32; margin: 0;">✅ Found {len(tenders_24h)} new IT tenders in the last 24 hours</p>
                </div>
                """
                plain_text += f"✅ Found {len(tenders_24h)} new IT tenders in the last 24 hours\n\n"
                
                for tender in tenders_24h:
                    html_content += self._tender_to_html(tender)
                    plain_text += self._tender_to_text(tender)
            else:
                html_content += """
                <div style="background: #fff3e0; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #e65100; margin: 0;">ℹ️ No new IT tenders found in the last 24 hours</p>
                </div>
                """
                plain_text += "ℹ️ No new IT tenders found in the last 24 hours\n\n"
            
            # SECTION 2: Last 31 days (fallback)
            html_content += f"""
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #1a237e; margin: 0;">📅 IT Tenders (Last 31 Days)</h3>
            </div>
            """
            plain_text += f"\n{'='*50}\n"
            plain_text += f"📅 IT TENDERS (LAST 31 DAYS)\n"
            plain_text += f"{'='*50}\n\n"
            
            # Get tenders from last 31 days
            tenders_31d = self.get_tenders_last_31_days(user)
            print(f"🔍 [DEBUG] Found {len(tenders_31d)} IT tenders from the last 31 days")
            
            if tenders_31d:
                # Show only tenders that weren't already shown in the 24h section
                # (Avoid duplicates)
                if tenders_24h:
                    # Get references from 24h tenders
                    refs_24h = {t.get('reference') for t in tenders_24h}
                    # Filter out duplicates
                    additional_tenders = [t for t in tenders_31d if t.get('reference') not in refs_24h]
                else:
                    additional_tenders = tenders_31d
                
                if additional_tenders:
                    html_content += f"""
                    <div style="background: #e8f5e9; padding: 10px; border-radius: 8px; margin: 10px 0;">
                        <p style="color: #2e7d32; margin: 0;">📊 Found {len(additional_tenders)} IT tenders in the last 31 days</p>
                    </div>
                    """
                    plain_text += f"📊 Found {len(additional_tenders)} IT tenders in the last 31 days\n\n"
                    
                    for tender in additional_tenders[:20]:  # Show max 20
                        html_content += self._tender_to_html(tender)
                        plain_text += self._tender_to_text(tender)
                else:
                    html_content += """
                    <div style="background: #fff3e0; padding: 10px; border-radius: 8px; margin: 10px 0;">
                        <p style="color: #e65100; margin: 0;">ℹ️ No additional IT tenders found in the last 31 days</p>
                    </div>
                    """
                    plain_text += "ℹ️ No additional IT tenders found in the last 31 days\n\n"
            else:
                html_content += """
                <div style="background: #fff3e0; padding: 10px; border-radius: 8px; margin: 10px 0;">
                    <p style="color: #e65100; margin: 0;">ℹ️ No IT tenders found in the last 31 days</p>
                </div>
                """
                plain_text += "ℹ️ No IT tenders found in the last 31 days\n\n"
            
            # Wrap the email in the full HTML template
            full_html = self._wrap_email_html(user, html_content, today)
            
            # Update last_sent_at
            if user.preferences:
                print(f"🔍 [DEBUG] Updating last_sent_at...")
                user.preferences.last_sent_at = datetime.now()
                from database import db
                db.session.commit()
                print(f"✅ [DEBUG] Updated last_sent_at")
            
            # Send the email
            subject = f"💻 IT Tender Digest - {today}"
            print(f"📧 [DEBUG] Sending email to {user.email}...")
            
            success = self.email_service.send_email(
                to_email=user.email,
                subject=subject,
                html_content=full_html,
                plain_text=plain_text
            )
            
            print(f"📧 [DEBUG] Email send result: {success}")
            print("=" * 60)
            
            if success:
                logger.info(f"✅ IT tender digest sent to {user.email} ({len(tenders_24h)} new, {len(tenders_31d)} in last 31 days)")
                print(f"✅ IT tender digest sent to {user.email} ({len(tenders_24h)} new, {len(tenders_31d)} in last 31 days)")
                return True
            else:
                logger.error(f"❌ Failed to send IT tender digest to {user.email}")
                return False
            
        except Exception as e:
            logger.error(f"Error sending IT tender digest for user {user.id}: {e}")
            print(f"❌ [DEBUG] Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _wrap_email_html(self, user: User, content: str, today: str) -> str:
        """Wrap the email content in the full HTML template"""
        prefs = user.preferences
        
        search_description = "IT Tenders"
        if prefs and prefs.custom_prompt:
            search_description = prefs.custom_prompt
        elif prefs and prefs.search_terms:
            search_description = f"Search: {prefs.search_terms}"
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #1a237e, #0d47a1); color: white; padding: 20px; border-radius: 8px; }}
        .header h1 {{ margin: 0; }}
        .header p {{ margin: 5px 0 0 0; opacity: 0.9; }}
        .prefs-summary {{ background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; }}
        .prefs-summary h3 {{ margin: 0 0 10px 0; color: #1a237e; }}
        .prefs-summary p {{ margin: 5px 0; }}
        .tender-card {{ background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #0d47a1; }}
        .tender-title {{ font-size: 18px; font-weight: bold; color: #1a237e; }}
        .tender-meta {{ color: #666; font-size: 14px; margin: 5px 0; }}
        .tender-deadline {{ color: #d32f2f; font-weight: bold; }}
        .category-badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; background: #4caf50; color: white; }}
        .it-badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; background: #2196f3; color: white; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💻 Daily IT Tender Digest</h1>
            <p>Your personalized IT tender updates - {today}</p>
        </div>
        
        <div class="prefs-summary">
            <h3>📋 Your Search Preferences</h3>
            <p><strong>Prompt:</strong> {search_description}</p>
            <p><strong>Frequency:</strong> {prefs.frequency if prefs else 'daily'}</p>
        </div>
        
        {content}
        
        <div class="footer">
            <p>This is your personalized daily IT tender digest.</p>
            <p>To adjust your preferences, visit your notification settings.</p>
        </div>
    </div>
</body>
</html>
"""
    
#     def _tender_to_html(self, tender: Dict) -> str:
#         """Convert a single tender to HTML"""
#         category = tender.get('category', 'other')
#         is_it = tender.get('is_it', False)
#         confidence = tender.get('it_confidence', 'None')
#         ai_score = tender.get('ai_score', 0)
        
#         return f"""
#         <div class="tender-card">
#             <div class="tender-title">{tender.get('title', 'Untitled')}</div>
#             <div class="tender-meta">
#                 <strong>Reference:</strong> {tender.get('reference', 'N/A')}
#             </div>
#             <div class="tender-meta">
#                 <strong>Buyer:</strong> {tender.get('buyer', 'Unknown')}
#             </div>
#             <div class="tender-meta">
#                 <strong>Publication Date:</strong> {tender.get('publication_date', 'N/A')}
#             </div>
#             <div class="tender-meta tender-deadline">
#                 <strong>Deadline:</strong> {tender.get('deadline', 'N/A')}
#             </div>
#             <div class="tender-meta">
#                 <span class="category-badge">{category.replace('_', ' ').title()}</span>
#                 {f'<span class="it-badge">IT ({confidence})</span>' if is_it else ''}
#                 <span style="font-size:12px;color:#666;">Relevance: {ai_score:.0%}</span>
#             </div>
#         </div>
#         """
    
#     def _tender_to_text(self, tender: Dict) -> str:
#         """Convert a single tender to plain text"""
#         return f"""
# Title: {tender.get('title', 'Untitled')}
# Reference: {tender.get('reference', 'N/A')}
# Buyer: {tender.get('buyer', 'Unknown')}
# Publication Date: {tender.get('publication_date', 'N/A')}
# Deadline: {tender.get('deadline', 'N/A')}
# Category: {tender.get('category', 'other')}
# {'-'*50}
# """
    def _tender_to_html(self, tender: Dict) -> str:
        """Convert a single tender to HTML with source link"""
        category = tender.get('category', 'other')
        is_it = tender.get('is_it', False)
        confidence = tender.get('it_confidence', 'None')
        ai_score = tender.get('ai_score', 0)
        source_url = tender.get('source_url', '')
        source = tender.get('source', 'TUNEPS')
        reference = tender.get('reference', '')
    
    # Construire le lien si source_url n'existe pas
        if not source_url:
            if source.upper() == 'HAICOP' and reference:
                source_url = f"https://www.marchespublics.gov.tn/fr/appels-doffres/{reference}"
    
        link_html = ''
        if source_url:
            link_html = f'''
        <div class="tender-meta" style="margin-top: 8px;">
            <a href="{source_url}" target="_blank" style="display: inline-block; padding: 6px 16px; background: #1a237e; color: white; border-radius: 4px; text-decoration: none; font-size: 13px;">
                🔗 Voir sur {source}
            </a>
        </div>
        '''
    
        return f"""
    <div class="tender-card">
        <div class="tender-title">{tender.get('title', 'Untitled')}</div>
        <div class="tender-meta">
            <strong>Reference:</strong> {tender.get('reference', 'N/A')}
        </div>
        <div class="tender-meta">
            <strong>Buyer:</strong> {tender.get('buyer', 'Unknown')}
        </div>
        <div class="tender-meta">
            <strong>Publication Date:</strong> {tender.get('publication_date', 'N/A')}
        </div>
        <div class="tender-meta tender-deadline">
            <strong>Deadline:</strong> {tender.get('deadline', 'N/A')}
        </div>
        <div class="tender-meta">
            <span class="category-badge">{category.replace('_', ' ').title()}</span>
            {f'<span class="it-badge">IT ({confidence})</span>' if is_it else ''}
            <span style="font-size:12px;color:#666;">Relevance: {ai_score:.0%}</span>
        </div>
        {link_html}
    </div>
    """

    def _tender_to_text(self, tender: Dict) -> str:
        """Convert a single tender to plain text with source link"""
        source_url = tender.get('source_url', '')
        source = tender.get('source', 'TUNEPS')
        reference = tender.get('reference', '')
    
    # Construire le lien si source_url n'existe pas
        if not source_url:
            if source.upper() == 'HAICOP' and reference:
                source_url = f"https://www.marchespublics.gov.tn/fr/appels-doffres/{reference}"
    
        text = f"""
Title: {tender.get('title', 'Untitled')}
Reference: {tender.get('reference', 'N/A')}
Buyer: {tender.get('buyer', 'Unknown')}
Publication Date: {tender.get('publication_date', 'N/A')}
Deadline: {tender.get('deadline', 'N/A')}
Category: {tender.get('category', 'other')}
"""
    
        if source_url:
            text += f"Source URL: {source_url}\n"
        else:
            text += f"Source: {source}\n"
    
        text += "-" * 50
        return text
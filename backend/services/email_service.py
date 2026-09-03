import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'TenderApp')
        self.from_display = f"{self.from_name} <{self.from_email}>"
        logger.info(f"📧 Email Service configured:")
        logger.info(f"  SMTP Host: {self.smtp_host}")
        logger.info(f"  SMTP Port: {self.smtp_port}")
        logger.info(f"  SMTP User: {self.smtp_user}")
        logger.info(f"  From Email: {self.from_email}")
        logger.info(f"  Password set: {'Yes' if self.smtp_password else 'No'}")
        
    def send_email(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Send an email"""
        try:
            if not self.smtp_user or not self.smtp_password:
                logger.error("❌ Email credentials not configured")
                return False
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_display 
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            if plain_text:
                part1 = MIMEText(plain_text, 'plain')
                msg.attach(part1)
            
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)
            
            logger.info(f"📧 Sending email to {to_email}...")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✅ Email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False

    def format_tenders_html(self, tenders: List[Dict], date_range: str) -> str:
        """Format tenders as HTML email - Removed Source field"""
        template = Template('''
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #1a237e, #0d47a1); color: white; padding: 20px; border-radius: 8px; }
        .tender-card { background: #f5f5f5; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #1a237e; }
        .tender-title { font-size: 18px; font-weight: bold; color: #1a237e; }
        .tender-meta { color: #666; font-size: 14px; margin: 5px 0; }
        .tender-deadline { color: #d32f2f; font-weight: bold; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px; }
        .no-tenders { text-align: center; padding: 40px; color: #666; }
        .stats { display: flex; justify-content: space-around; background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 15px 0; }
        .stat-item { text-align: center; }
        .stat-number { font-size: 24px; font-weight: bold; color: #1a237e; }
        .stat-label { font-size: 12px; color: #666; }
        .badge { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; background: #4caf50; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏗️ Daily Construction Tenders</h1>
            <p>New tenders from the past 24 hours ({{ date_range }})</p>
        </div>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-number">{{ tenders|length }}</div>
                <div class="stat-label">New Tenders</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">{{ tenders|selectattr('deadline')|list|length }}</div>
                <div class="stat-label">With Deadlines</div>
            </div>
        </div>
        
        {% if tenders %}
            {% for tender in tenders %}
            <div class="tender-card">
                <div class="tender-title">{{ tender.title }}</div>
                <div class="tender-meta">
                    <strong>Reference:</strong> {{ tender.reference }}
                </div>
                <div class="tender-meta">
                    <strong>Buyer:</strong> {{ tender.buyer }}
                </div>
                <div class="tender-meta">
                    <strong>Publication Date:</strong> {{ tender.publication_date or tender.indexed_at or 'N/A' }}
                </div>
                <div class="tender-meta tender-deadline">
                    <strong>Deadline:</strong> {{ tender.deadline }}
                </div>
            </div>
            {% endfor %}
        {% else %}
            <div class="no-tenders">
                <h2>😴 No new tenders found today</h2>
                <p>Check back tomorrow for new construction opportunities!</p>
            </div>
        {% endif %}
        
        <div class="footer">
            <p>This is an automated daily digest of construction tenders.</p>
            <p>To unsubscribe or change your preferences, please contact support.</p>
        </div>
    </div>
</body>
</html>
        ''')
        
        return template.render(tenders=tenders, date_range=date_range)

# models/scraper_config.py
from database import db
from datetime import datetime
import json

class ScraperConfig(db.Model):
    """Store scraper configurations for dynamic sources"""
    __tablename__ = 'scraper_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    source_type = db.Column(db.String(20), default='api')  # 'api', 'html'
    
    # Connection settings
    base_url = db.Column(db.String(500), nullable=False)
    headers = db.Column(db.Text, default='{}')
    
    # Authentication
    auth_type = db.Column(db.String(20), default='none')  # 'none', 'bearer', 'api_key', 'basic'
    auth_config = db.Column(db.Text, default='{}')
    
    # Parser settings
    parser_config = db.Column(db.Text, default='{}')
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    last_scraped = db.Column(db.DateTime)
    total_tenders = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'source_type': self.source_type,
            'base_url': self.base_url,
            'headers': json.loads(self.headers) if self.headers else {},
            'auth_type': self.auth_type,
            'auth_config': json.loads(self.auth_config) if self.auth_config else {},
            'parser_config': json.loads(self.parser_config) if self.parser_config else {},
            'is_active': self.is_active,
            'last_scraped': self.last_scraped.isoformat() if self.last_scraped else None,
            'total_tenders': self.total_tenders,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<ScraperConfig {self.name}>"
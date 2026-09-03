# models/user_preferences.py
from datetime import datetime
from database import db
import json

class UserPreferences(db.Model):
    """User preferences for tender notifications"""
    __tablename__ = 'user_preferences'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # ===== NOTIFICATION SETTINGS =====
    notifications_enabled = db.Column(db.Boolean, default=True)
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, immediate
    send_time = db.Column(db.String(10), default='08:00')  # HH:MM format
    last_sent_at = db.Column(db.DateTime)
    
    # ===== SEARCH PREFERENCES (User's custom prompt) =====
    custom_prompt = db.Column(db.Text)  # The main prompt for the IT agent
    search_terms = db.Column(db.Text)   # Comma-separated keywords
    
    # ===== FILTERS =====
    categories = db.Column(db.Text)     # Comma-separated
    min_budget = db.Column(db.Float)
    max_budget = db.Column(db.Float)
    regions = db.Column(db.Text)        # Comma-separated
    buyers = db.Column(db.Text)         # Comma-separated
    sources = db.Column(db.Text)        # Comma-separated (TUNEPS, HAICOP, etc.)
    
    # ===== STATUS =====
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    # user = db.relationship('User', backref='preferences', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'notifications_enabled': self.notifications_enabled,
            'frequency': self.frequency,
            'send_time': self.send_time,
            'custom_prompt': self.custom_prompt,
            'search_terms': self._parse_list(self.search_terms),
            'categories': self._parse_list(self.categories),
            'min_budget': self.min_budget,
            'max_budget': self.max_budget,
            'regions': self._parse_list(self.regions),
            'buyers': self._parse_list(self.buyers),
            'sources': self._parse_list(self.sources),
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def _parse_list(text):
        """Parse comma-separated text into list"""
        if not text:
            return []
        return [item.strip() for item in text.split(',') if item.strip()]
    
    @staticmethod
    def _join_list(items):
        """Join list into comma-separated text"""
        if not items:
            return None
        return ', '.join(items)
    
    def get_search_terms_list(self):
        return self._parse_list(self.search_terms)
    
    def get_categories_list(self):
        return self._parse_list(self.categories)
    
    def get_regions_list(self):
        return self._parse_list(self.regions)
    
    def get_buyers_list(self):
        return self._parse_list(self.buyers)
    
    def get_sources_list(self):
        return self._parse_list(self.sources)
    
    def __repr__(self):
        return f"<UserPreferences user_id={self.user_id}>"
# from datetime import datetime
# from database import db

# class Tender(db.Model):
#     """Tender entity"""
#     __tablename__ = 'tenders'
    
#     id = db.Column(db.Integer, primary_key=True)
#     source_reference = db.Column(db.String(50), unique=True, nullable=False, index=True)
#     title = db.Column(db.String(500), nullable=False)
#     buyer = db.Column(db.String(200))
#     category = db.Column(db.String(100))
#     region = db.Column(db.String(100))
#     estimated_value = db.Column(db.String(50))
#     language = db.Column(db.String(10), default='fr')
#     publication_date = db.Column(db.String(30))
#     deadline = db.Column(db.String(30))
#     description = db.Column(db.Text)
#     source_urls = db.Column(db.Text)
#     source = db.Column(db.String(50), default='TUNEPS')
    
#     matched_topics = db.Column(db.Text)
#     relevance_score = db.Column(db.Float, default=0.0)
#     match_explanation = db.Column(db.Text)
    
#     status = db.Column(db.String(20), default='new')
    
#     first_seen = db.Column(db.DateTime, default=datetime.utcnow)
#     last_seen = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     def to_dict(self):
#         return {
#             'id': self.id,
#             'source_reference': self.source_reference,
#             'title': self.title,
#             'buyer': self.buyer,
#             'category': self.category,
#             'region': self.region,
#             'estimated_value': self.estimated_value,
#             'language': self.language,
#             'publication_date': self.publication_date,
#             'deadline': self.deadline,
#             'description': self.description[:200] + '...' if self.description and len(self.description) > 200 else self.description,
#             'source_urls': self.source_urls.split(',') if self.source_urls else [],
#             'source': self.source,
#             'status': self.status,
#             'relevance_score': self.relevance_score,
#             'matched_topics': self.matched_topics.split(',') if self.matched_topics else [],
#             'first_seen': self.first_seen.isoformat() if self.first_seen else None,
#             'last_seen': self.last_seen.isoformat() if self.last_seen else None,
#             'created_at': self.created_at.isoformat() if self.created_at else None
#         }
    
#     def __repr__(self):
#         return f"<Tender {self.source_reference}>"


from datetime import datetime
from database import db

class Tender(db.Model):
    """Tender entity - 5 fields only"""
    __tablename__ = 'tenders'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 5 fields from TUNEPS
    reference = db.Column(db.String(50), unique=True, nullable=False, index=True)  # N° A.O
    buyer = db.Column(db.String(200))  # Acheteur public
    publication_date = db.Column(db.String(30))  # Date Publication
    title = db.Column(db.Text)  # Objet A.O (full description)
    deadline = db.Column(db.String(50))  # Dernier Délai Soumissions Offres
    
    # Metadata
    source = db.Column(db.String(50), default='TUNEPS')
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'reference': self.reference,
            'buyer': self.buyer,
            'publication_date': self.publication_date,
            'title': self.title,
            'deadline': self.deadline,
            'source': self.source,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None
        }
    
    def __repr__(self):
        return f"<Tender {self.reference}>"
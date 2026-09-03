# models/user.py
from datetime import datetime
from database import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    # EXPLICIT MAPPING - tell SQLAlchemy exactly which column to use
    username = db.Column('username', db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255))
    
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    preferences = db.relationship('UserPreferences', 
                                  backref='user', 
                                  uselist=False, 
                                  cascade='all, delete-orphan')
    
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    def get_preferences(self):
        if not self.preferences:
            from models.user_preferences import UserPreferences
            self.preferences = UserPreferences(user_id=self.id)
            db.session.commit()
        return self.preferences

    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<User {self.username}>"
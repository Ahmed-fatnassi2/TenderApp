# refresh_metadata.py
from app import app
from database import db

with app.app_context():
    # Clear the metadata cache
    db.metadata.clear()
    
    # Import the model to refresh
    from models.user import User
    
    # Force reflection
    db.metadata.reflect(bind=db.engine)
    
    # Print columns to verify
    print("Columns in users table:", User.__table__.columns.keys())
    print("Database URL:", app.config['SQLALCHEMY_DATABASE_URI'])
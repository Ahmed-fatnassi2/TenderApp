# check_users.py
from app import app
from database import db
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables in database: {tables}")
    
    if 'users' in tables:
        columns = inspector.get_columns('users')
        print("\n📊 Users table columns:")
        for col in columns:
            print(f"  - {col['name']}: {col['type']}")
        
        # Check if username exists
        username_exists = any(col['name'] == 'username' for col in columns)
        if username_exists:
            print("\n✅ Username column exists!")
        else:
            print("\n❌ Username column is MISSING!")
#!/usr/bin/env python3
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Update migration tracking to mark first migration as applied
        db.session.execute(text("DELETE FROM alembic_version"))
        db.session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('22c97c0eb2f7')"))
        db.session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('9c0fce5de3bf')"))
        db.session.commit()
        print('Migration versions updated')
        
        # Verify tenders table exists and show its structure
        result = db.session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tenders' ORDER BY ordinal_position"))
        print('\nTenders table columns:')
        for col, dtype in result:
            print(f'  - {col}: {dtype}')
            
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()

#!/usr/bin/env python3
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check current versions
        result = db.session.execute(text('SELECT * FROM alembic_version'))
        versions = [row[0] for row in result]
        print(f'Current versions in alembic_version: {versions}')
        
        # Delete orphaned versions (keep only valid ones)
        valid_versions = ['22c97c0eb2f7', '9c0fce5de3bf']
        for v in versions:
            if v not in valid_versions:
                db.session.execute(text(f"DELETE FROM alembic_version WHERE version_num = '{v}'"))
                print(f'Deleted orphaned version: {v}')
        
        db.session.commit()
        print('Migration cleanup complete')
        
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()

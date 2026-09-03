#!/usr/bin/env python3
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Drop the empty tenders table and recreate it with correct schema
        db.session.execute(text("DROP TABLE IF EXISTS tenders CASCADE"))
        db.session.commit()
        print('Dropped empty tenders table')
        
        # Create tenders table with correct schema (5 fields only)
        sql = """
        CREATE TABLE tenders (
            id SERIAL PRIMARY KEY,
            reference VARCHAR(50) UNIQUE NOT NULL,
            buyer VARCHAR(200),
            publication_date VARCHAR(30),
            title TEXT,
            deadline VARCHAR(50),
            source VARCHAR(50) DEFAULT 'TUNEPS',
            scraped_at TIMESTAMP
        )
        """
        db.session.execute(text(sql))
        db.session.execute(text("CREATE INDEX ix_tenders_reference ON tenders (reference)"))
        db.session.commit()
        print('Created tenders table with correct schema')
        
        # Verify structure
        result = db.session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tenders' ORDER BY ordinal_position"))
        print('\nTenders table columns:')
        for col, dtype in result:
            print(f'  - {col}: {dtype}')
            
    except Exception as e:
        print(f'Error: {e}')
        db.session.rollback()

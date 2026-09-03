#!/usr/bin/env python3
import os
os.environ['DATABASE_URL'] = 'postgresql://postgres:Postgrespwd12345.@localhost:5432/tender_db'

from app import app, db
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Available tables: {tables}')
    
    if 'tenders' in tables:
        result = db.session.execute(text('SELECT COUNT(*) as count FROM tenders'))
        count = result.fetchone()[0]
        print(f'Tenders count: {count}')
        
        # Get first few tenders
        result = db.session.execute(text('SELECT id, reference, title FROM tenders LIMIT 3'))
        for row in result:
            print(f'  - ID: {row[0]}, Reference: {row[1]}, Title: {row[2][:50]}...')
    else:
        print('tenders table does not exist!')

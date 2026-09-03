#!/usr/bin/env python3
"""Direct database table creation without migrations"""
import os
import psycopg2
from psycopg2 import sql

# Connect to PostgreSQL
conn = psycopg2.connect(
    database="tender_db",
    user="postgres",
    password="Postgrespwd12345.",
    host="localhost",
    port="5432"
)
cur = conn.cursor()

try:
    # Create tenders table
    create_sql = """
    CREATE TABLE IF NOT EXISTS tenders (
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
    cur.execute(create_sql)
    
    # Create index
    cur.execute("""
    CREATE INDEX IF NOT EXISTS ix_tenders_reference ON tenders (reference)
    """)
    
    conn.commit()
    print("✅ Tenders table created successfully")
    
    # Check table structure
    cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'tenders' 
    ORDER BY ordinal_position
    """)
    print("\nTable structure:")
    for col_name, data_type in cur.fetchall():
        print(f"  - {col_name}: {data_type}")
    
    # Check for existing tenders
    cur.execute("SELECT COUNT(*) FROM tenders")
    count = cur.fetchone()[0]
    print(f"\nCurrent row count: {count}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()

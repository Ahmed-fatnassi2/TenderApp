#!/usr/bin/env python3
"""Generate sample tender data for testing"""
from app import app, db
from models import Tender
from datetime import datetime, timedelta
import random

# Sample tender data
BUYERS = ["Ministry of Finance", "Ministry of Health", "Ministry of Education", 
          "Ministry of Transport", "Ministry of Interior", "Ministry of Energy"]
SOURCES = ["TUNEPS", "MARCHE", "APPEL"]

def generate_tenders(count=586):
    """Generate sample tenders"""
    with app.app_context():
        tenders = []
        for i in range(1, count + 1):
            tender = Tender(
                reference=f"REF-2024-{i:05d}",
                buyer=random.choice(BUYERS),
                publication_date=f"2024-{random.randint(1,7):02d}-{random.randint(1,28):02d}",
                title=f"Tender for Procurement {i}",
                deadline=f"2024-{random.randint(8,12):02d}-{random.randint(1,28):02d}",
                source=random.choice(SOURCES),
                scraped_at=datetime.utcnow()
            )
            tenders.append(tender)
        
        # Batch insert
        db.session.bulk_save_objects(tenders)
        db.session.commit()
        print(f"✅ Created {count} sample tenders")

if __name__ == "__main__":
    generate_tenders(586)

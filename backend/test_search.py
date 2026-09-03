import os
from pathlib import Path
import sys

# Load .env manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

from services.openrag_client import OpenRAGClient
from datetime import datetime

client = OpenRAGClient()

# Search directly with OpenRAG
print("🔍 Searching for 'travaux'...")
result = client.search("travaux", top_k=10, partition_name="tenders", similarity_threshold=0.3)

if result and 'documents' in result:
    print(f"📊 Found {len(result['documents'])} documents\n")
    
    # Show sample
    for i, doc in enumerate(result['documents'][:5], 1):
        meta = doc.get('metadata', {})
        print(f"{i}. Title: {meta.get('title', 'N/A')[:60]}")
        print(f"   Buyer: {meta.get('buyer', 'N/A')}")
        print(f"   Indexed: {meta.get('indexed_at', 'N/A')}")
        print(f"   Reference: {meta.get('reference', 'N/A')}")
        print()
    
    # Check if any are from this month
    current_month = datetime.now().month
    current_year = datetime.now().year
    this_month_count = 0
    
    for doc in result['documents']:
        meta = doc.get('metadata', {})
        indexed_at = meta.get('indexed_at', '')
        if indexed_at:
            try:
                if 'T' in indexed_at:
                    date_part = indexed_at.split('T')[0]
                    pub_date = datetime.strptime(date_part, '%Y-%m-%d')
                    if pub_date.month == current_month and pub_date.year == current_year:
                        this_month_count += 1
            except:
                pass
    
    print(f"📊 Tenders from this month: {this_month_count}")
    
else:
    print("No results found")

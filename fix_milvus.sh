#!/bin/bash
# Fix Milvus collection schema from within WSL Docker
# This will be executed inside a container that has pymilvus installed

python3 << 'PYTHON_EOF'
from pymilvus import connections, Collection

# Connect to Milvus
print("[1] Connecting to local Milvus...")
try:
    connections.connect("default", host="milvus", port="19530")
    print("✓ Connected to Milvus")
except Exception as e:
    print(f"✗ Failed to connect: {e}")
    exit(1)

# Drop the corrupted collection
print("\n[2] Dropping corrupted tender_db collection...")
try:
    col = Collection("tender_db")
    col.drop()
    print("✓ Dropped tender_db collection")
except Exception as e:
    print(f"✓ No existing collection or already dropped: {e}")

print("\n✅ Collection dropped. OpenRAG will auto-recreate with correct schema on next index.")
print("Next steps:")
print("1. Restart OpenRAG: docker-compose restart compose-openrag-cpu-1")
print("2. Re-index tenders: POST http://localhost:5000/api/openrag/index-all")

PYTHON_EOF

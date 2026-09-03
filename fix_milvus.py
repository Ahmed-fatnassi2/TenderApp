#!/usr/bin/env python3
"""
Fix Milvus collection schema for tender_db
Drop corrupted collection and recreate with correct schema
"""

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# Connect to Milvus in WSL Docker via WSL IP
print("[1] Connecting to Milvus at 172.17.33.70:19530...")
connections.connect("default", host="172.17.33.70", port=19530)
print("✓ Connected to Milvus")

# Drop existing collection if corrupted
print("\n[2] Dropping existing tender_db collection (if exists)...")
try:
    col = Collection("tender_db")
    col.drop()
    print("✓ Dropped existing tender_db collection")
except Exception as e:
    print(f"✓ No existing collection to drop: {e}")

# Define correct schema for tender documents
print("\n[3] Creating new tender_db collection with correct schema...")
fields = [
    FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
    FieldSchema(name="file_id", dtype=DataType.VARCHAR, max_length=256),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048),
    FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
]

schema = CollectionSchema(
    fields=fields,
    description="Tender documents with OpenAI embeddings"
)

collection = Collection(name="tender_db", schema=schema)
print("✓ Created tender_db collection")
print(f"✓ Fields: {[f.name for f in fields]}")
print(f"✓ Vector dimension: 1024 (text-embedding-3-small)")
print(f"✓ Primary key: id (INT64)")

# Create index on vector field for fast search
print("\n[4] Creating index on vector field...")
index_params = {
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {"nlist": 128},
}
collection.create_index(field_name="vector", index_params=index_params)
print("✓ Created IVF_FLAT index on vector field")

# Load collection into memory
print("\n[5] Loading collection into memory...")
collection.load()
print("✓ Collection loaded and ready for searches")

print("\n✅ Milvus collection fixed successfully!")
print(f"Collection name: tender_db")
print(f"Status: Ready for documents")

#!/bin/bash
source /app/.venv/bin/activate
python3 << 'PYEOF'
from pymilvus import connections, Collection
connections.connect(host='milvus', port='19530')
col = Collection('tender_db')
col.load()
print(f"Total documents in Milvus: {col.num_entities}")
PYEOF

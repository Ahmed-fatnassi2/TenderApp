#!/bin/bash
# Monitor Milvus document count every 5 seconds

while true; do
  count=$(docker exec compose-openrag-cpu-1 bash -c "
    source /app/.venv/bin/activate
    python3 << 'PYEOF'
from pymilvus import connections, Collection
try:
    connections.connect(host='milvus', port='19530')
    col = Collection('tender_db')
    col.load()
    print(col.num_entities)
except Exception as e:
    print(0)
PYEOF
  " 2>/dev/null)
  
  timestamp=$(date '+%H:%M:%S')
  echo "[$timestamp] Documents in Milvus: $count"
  sleep 5
done

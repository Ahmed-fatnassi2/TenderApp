#!/usr/bin/env python3
from pymilvus import connections, Collection

# Connect to Milvus
connections.connect('default', host='172.17.33.70', port=19530)

col = Collection('tender_db')
print('=== Collection Schema ===')
print(f'Collection name: {col.name}')
print(f'Number of entities: {col.num_entities}')
print(f'\n=== Fields ===')
for field in col.schema.fields:
    print(f'  - {field.name}: {field.dtype} (is_primary={field.is_primary}, auto_id={field.auto_id})')
print(f'\n=== Dynamic Fields Enabled: {col.schema.enable_dynamic_field} ===')

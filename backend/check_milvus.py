from pymilvus import Collection, connections

# Connect to Milvus
connections.connect(host="127.0.0.1", port=19530)

# Check if collection exists
try:
    collection = Collection(name="tender_db")
    schema = collection.schema
    
    print("Collection 'tender_db' schema:")
    print(f"Primary field: {schema.primary_field.name if schema.primary_field else 'None'}")
    print("\nFields:")
    for field in schema.fields:
        print(f"  - {field.name}: {field.dtype} (is_vector={field.is_vector}, dim={getattr(field, 'params', {}).get('dim', 'N/A')})")
    
    print(f"\nTotal documents: {collection.num_entities}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    connections.disconnect()

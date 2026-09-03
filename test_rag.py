#!/usr/bin/env python
import time
import requests

print("Waiting for OpenRAG to become ready...")
for i in range(60):
    try:
        r = requests.get('http://localhost:8081/health', 
                        headers={'Authorization': 'Bearer sk-openrag-dev'}, 
                        timeout=2)
        print(f"✓ OpenRAG is ready! (Status: {r.status_code})")
        break
    except Exception as e:
        if i % 10 == 0:
            print(f"  Waiting... ({i}s). Last error: {type(e).__name__}")
        time.sleep(1)
else:
    print("✗ OpenRAG did not respond after 60 seconds")

print("\nTesting Flask RAG health endpoint...")
try:
    r = requests.get('http://localhost:5000/api/rag/health')
    import json
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

#!/usr/bin/env python3
"""
Integration test script for TenderApp OpenRAG backend
Tests connectivity between all components
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:5000/api"
OPENRAG_URL = "http://localhost:8081"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(status: str, message: str):
    if status == 'ok':
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")
    elif status == 'error':
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")
    elif status == 'warning':
        print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")
    elif status == 'info':
        print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def test_backend_health():
    """Test if backend is running"""
    print("\n" + "="*50)
    print("Testing Backend Health")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_status('ok', f"Backend is running on port 5000")
            print_status('ok', f"Database: {data.get('database', 'N/A')}")
            return True
        else:
            print_status('error', f"Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status('error', "Could not connect to backend on http://localhost:5000")
        return False
    except Exception as e:
        print_status('error', f"Backend health check failed: {str(e)}")
        return False

def test_rag_health():
    """Test if OpenRAG service is running"""
    print("\n" + "="*50)
    print("Testing OpenRAG Health")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/rag/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get('rag_healthy'):
                print_status('ok', "OpenRAG service is healthy")
                print_status('ok', f"Status: {data.get('status', 'N/A')}")
                print_status('ok', f"Backend: {data.get('backend', 'N/A')}")
                return True
            else:
                print_status('warning', "OpenRAG health check returned unhealthy status")
                print_status('info', f"Status: {data.get('status', 'N/A')}")
                return False
        else:
            print_status('error', f"RAG health endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status('error', "Could not connect to OpenRAG health endpoint")
        return False
    except Exception as e:
        print_status('error', f"OpenRAG health check failed: {str(e)}")
        return False

def test_tenders_endpoint():
    """Test if tenders endpoint works"""
    print("\n" + "="*50)
    print("Testing Tenders Endpoint")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/tenders?page=1&per_page=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('pagination', {}).get('total', 0)
            print_status('ok', f"Tenders endpoint is working")
            print_status('ok', f"Total tenders in database: {total}")
            if total > 0:
                print_status('ok', f"Sample tender: {data['data'][0].get('title', 'N/A')[:50]}...")
            return True
        else:
            print_status('error', f"Tenders endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_status('error', f"Tenders endpoint test failed: {str(e)}")
        return False

def test_tender_count():
    """Test tender count endpoint"""
    print("\n" + "="*50)
    print("Testing Tender Count")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/tenders/count", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = data.get('total', 0)
            print_status('ok', f"Tender count endpoint is working")
            print_status('info', f"Total tenders: {count}")
            return count > 0
        else:
            print_status('error', f"Tender count endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print_status('error', f"Tender count test failed: {str(e)}")
        return False

def test_semantic_search():
    """Test semantic search endpoint"""
    print("\n" + "="*50)
    print("Testing Semantic Search")
    print("="*50)
    
    test_query = "infrastructure projects"
    
    try:
        payload = {
            "query": test_query,
            "top_k": 3,
            "similarity_threshold": 0.5
        }
        
        response = requests.post(
            f"{BASE_URL}/rag/search/semantic",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results_count = len(data.get('results', []))
                print_status('ok', f"Semantic search is working")
                print_status('ok', f"Query: '{test_query}'")
                print_status('info', f"Results found: {results_count}")
                
                if results_count > 0:
                    first_result = data['results'][0]
                    print_status('info', f"Top result score: {first_result.get('score', 0):.4f}")
                
                return True
            else:
                print_status('error', f"Semantic search returned: {data.get('error', 'Unknown error')}")
                return False
        else:
            print_status('warning', f"Semantic search returned status {response.status_code}")
            print_status('info', f"This is expected if RAG hasn't been initialized yet")
            return False
            
    except Exception as e:
        print_status('warning', f"Semantic search test failed: {str(e)}")
        print_status('info', f"This is expected if RAG hasn't been initialized yet")
        return False

def test_openrag_direct():
    """Test direct connection to OpenRAG"""
    print("\n" + "="*50)
    print("Testing Direct OpenRAG Connection")
    print("="*50)
    
    try:
        response = requests.get(f"{OPENRAG_URL}/health_check", timeout=5)
        if response.status_code == 200:
            print_status('ok', "OpenRAG service is accessible on port 8081")
            print_status('ok', f"Response: {response.text}")
            return True
        else:
            print_status('error', f"OpenRAG returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_status('error', "Could not connect to OpenRAG on port 8081")
        print_status('info', "Verify Docker container is running: docker ps | grep openrag")
        return False
    except Exception as e:
        print_status('error', f"OpenRAG direct test failed: {str(e)}")
        return False

def print_summary(results: Dict[str, bool]):
    """Print test summary"""
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = 'ok' if result else 'error'
        print_status(status, f"{test_name}: {'PASSED' if result else 'FAILED'}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print_status('ok', "All systems operational! Ready to use.")
    elif passed >= total - 1:
        print_status('warning', "Most systems operational. Check warnings above.")
    else:
        print_status('error', "Some systems are not working. Check errors above.")

def main():
    """Run all integration tests"""
    print(f"\n{Colors.BLUE}TenderApp Integration Test Suite{Colors.RESET}")
    print("Testing connectivity between frontend, backend, and OpenRAG...\n")
    
    results = {}
    
    # Run tests
    results['Backend Health'] = test_backend_health()
    results['OpenRAG Health (via Backend)'] = test_rag_health()
    results['Direct OpenRAG Connection'] = test_openrag_direct()
    results['Tenders Endpoint'] = test_tenders_endpoint()
    results['Tender Count'] = test_tender_count()
    results['Semantic Search'] = test_semantic_search()
    
    # Print summary
    print_summary(results)
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()

import requests
import json

print("=" * 60)
print("🔍 TESTING PAGINATION FORMATS")
print("=" * 60)

url = "https://www.tuneps.tn/api2/portail/bid/master/data"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Content-Type': 'application/json',
    'Origin': 'https://www.tuneps.tn',
    'Referer': 'https://www.tuneps.tn/portail/offres',
}

# Try different pagination formats
pagination_formats = [
    {"offSet": 200, "limit": 200},
    {"page": 2, "limit": 200},
    {"pageNumber": 2, "pageSize": 200},
    {"page": 2, "size": 200},
    {"currentPage": 2, "itemsPerPage": 200},
]

today = "2026-07-01"
payload_base = {
    "listSort": [],
    "dataSearch": [
        {"key": "publicYn", "value": "Y", "specificSearch": "="},
        {"key": "publicDt", "value": "2026-01-01", "specificSearch": ">="},
        {"key": "bdRecvEndDt", "value": today, "specificSearch": ">="}
    ],
    "listCol": [],
    "sort": {"nameCol": "publicDt", "direction": "desc nulls last"}
}

for i, pagination in enumerate(pagination_formats, 1):
    payload = payload_base.copy()
    payload["pagination"] = pagination
    
    print(f"\n📄 Test {i}: {pagination}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '200':
                payload_data = data.get('payload', {})
                tender_list = payload_data.get('data', [])
                total = payload_data.get('total', 0)
                print(f"  ✅ Status: 200")
                print(f"  📋 Found {len(tender_list)} tenders (Total: {total})")
                if tender_list:
                    print(f"  🔍 First tender: {tender_list[0].get('bidNo', 'N/A')}")
                else:
                    print(f"  ⚠️ No tenders in response (empty data array)")
            else:
                print(f"  ❌ Code: {data.get('code')}")
        else:
            print(f"  ❌ Status: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("-" * 40)

print("\n" + "=" * 60)
print("🔍 TESTING OFFSET VALUES")
print("=" * 60)

# Try different offset values
offset_values = [0, 200, 400, 600, 800, 1000]

for offset in offset_values:
    pagination = {"offSet": offset, "limit": 200}
    payload = payload_base.copy()
    payload["pagination"] = pagination
    
    print(f"\n📄 Offset: {offset}")
    
    try:
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '200':
                payload_data = data.get('payload', {})
                tender_list = payload_data.get('data', [])
                total = payload_data.get('total', 0)
                print(f"  ✅ Found {len(tender_list)} tenders (Total: {total})")
                if tender_list:
                    print(f"  🔍 First tender: {tender_list[0].get('bidNo', 'N/A')}")
                else:
                    print(f"  ⚠️ No tenders in response (empty data array)")
            else:
                print(f"  ❌ Code: {data.get('code')}")
        else:
            print(f"  ❌ Status: {response.status_code}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("🔍 TESTING WITHOUT DATE FILTER")
print("=" * 60)

# Remove the date filter to see if pagination works without it
payload_no_date = {
    "listSort": [],
    "dataSearch": [
        {"key": "publicYn", "value": "Y", "specificSearch": "="},
    ],
    "listCol": [],
    "pagination": {"offSet": 200, "limit": 200},
    "sort": {"nameCol": "publicDt", "direction": "desc nulls last"}
}

print(f"\n📄 Testing without date filter (offset: 200)")

try:
    response = requests.post(url, headers=headers, json=payload_no_date, verify=False, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == '200':
            payload_data = data.get('payload', {})
            tender_list = payload_data.get('data', [])
            total = payload_data.get('total', 0)
            print(f"  ✅ Found {len(tender_list)} tenders (Total: {total})")
            if tender_list:
                print(f"  🔍 First tender: {tender_list[0].get('bidNo', 'N/A')}")
            else:
                print(f"  ⚠️ No tenders in response")
        else:
            print(f"  ❌ Code: {data.get('code')}")
    else:
        print(f"  ❌ Status: {response.status_code}")
except Exception as e:
    print(f"  ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Debug complete!")
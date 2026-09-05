# test_haicop_api.py
import requests
import json
import urllib3
import warnings

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_haicop_api():
    """Tester l'API HAICOP"""
    
    url = "https://www.marchespublics.gov.tn/fr/appels-doffres?draw=1&start=0&length=10&search[value]="
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.marchespublics.gov.tn/fr/appels-doffres",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    print("🔍 Test de l'API HAICOP...")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=30,
            verify=False
        )
        
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n📋 Clés de la réponse: {list(data.keys())}")
            
            if 'data' in data:
                items = data['data']
                print(f"📊 Nombre de tenders: {len(items)}")
                
                if items and len(items) > 0:
                    print("\n📄 Premier tender:")
                    item = items[0]
                    for key, value in item.items():
                        if isinstance(value, str) and len(str(value)) > 80:
                            print(f"  {key}: {str(value)[:80]}...")
                        else:
                            print(f"  {key}: {value}")
                    
                    # ✅ Vérifier si une URL existe
                    print("\n🔍 Recherche d'URL:")
                    if 'url' in item:
                        print(f"  ✅ URL: {item['url']}")
                    if 'link' in item:
                        print(f"  ✅ Link: {item['link']}")
                    if 'id' in item:
                        print(f"  🔑 ID: {item['id']}")
                        print(f"  🔗 URL construite: https://www.marchespublics.gov.tn/fr/appels-doffres/{item['id']}")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_haicop_api()
# test_tuneps_api_response.py
import requests
import json
import urllib3
import warnings

warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_tuneps_api():
    """Tester l'API TUNEPS pour voir ce qu'elle renvoie"""
    
    url = "https://www.tuneps.tn/api2/portail/bid/master/data"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Content-Type": "application/json",
        "Origin": "https://www.tuneps.tn",
        "Referer": "https://www.tuneps.tn/portail/offres"
    }
    
    payload = {
        "listSort": [],
        "dataSearch": [
            {"key": "publicYn", "value": "Y", "specificSearch": "="},
            {"key": "bdRecvEndDt", "value": "2026-08-08", "specificSearch": ">="}
        ],
        "listCol": [],
        "pagination": {"offSet": 0, "limit": 10},
        "sort": {"nameCol": "publicDt", "direction": "desc nulls last"}
    }
    
    print("🔍 Test de l'API TUNEPS...")
    print(f"📡 URL: {url}")
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30,
            verify=False
        )
        
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Afficher la structure
            print(f"\n📋 Clés de la réponse: {list(data.keys())}")
            
            # Naviguer jusqu'aux données
            if 'payload' in data and 'data' in data['payload']:
                items = data['payload']['data']
                print(f"📊 Nombre de tenders: {len(items)}")
                
                if items and len(items) > 0:
                    print("\n📄 Premier tender (structure complète):")
                    item = items[0]
                    for key, value in item.items():
                        if isinstance(value, str) and len(str(value)) > 80:
                            print(f"  {key}: {str(value)[:80]}...")
                        else:
                            print(f"  {key}: {value}")
                    
                    # ✅ Vérifier si une URL existe
                    print("\n🔍 Recherche d'URL ou d'ID:")
                    url_fields = ['url', 'link', 'href', 'detailsUrl', 'publicUrl', 'bidUrl']
                    for field in url_fields:
                        if field in item:
                            print(f"  ✅ {field}: {item[field]}")
                    
                    # Vérifier si un ID existe
                    if 'id' in item:
                        print(f"  🔑 ID trouvé: {item['id']}")
                    
                    if 'bidNo' in item:
                        print(f"  📌 Référence: {item['bidNo']}")
                        
                        # Essayer de construire l'URL
                        if 'id' in item:
                            print(f"  🔗 URL construite: https://www.tuneps.tn/portail/offres/details/{item['id']}/{item['bidNo']}")
            else:
                print(f"Structure inattendue: {data}")
                
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    test_tuneps_api()
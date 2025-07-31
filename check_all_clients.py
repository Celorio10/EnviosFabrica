import requests
import json

def check_all_clients_work_centers():
    """Check all clients for problematic work centers"""
    
    base_url = "https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Login as admin
    login_response = requests.post(f"{api_url}/auth/login", json={
        "username": "admin",
        "password": "ASCb33388091_"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Get all clients
    clients_response = requests.get(f"{api_url}/clientes", headers=headers)
    clients = clients_response.json()
    
    print(f"🔍 Checking {len(clients)} clients for problematic work centers...")
    
    problematic_clients = []
    
    for client in clients:
        client_name = client.get('nombre', 'UNNAMED')
        client_id = client.get('id', 'NO_ID')
        work_centers = client.get('centros_trabajo', [])
        
        print(f"\n📋 Client: {client_name} (ID: {client_id})")
        print(f"   Work centers: {len(work_centers)}")
        
        has_problems = False
        
        for i, wc in enumerate(work_centers):
            wc_id = wc.get('id', None)
            wc_name = wc.get('nombre', None)
            
            print(f"   {i+1}. ID: '{wc_id}' | Name: '{wc_name}'")
            
            # Check for problematic values
            if wc_id is None or wc_id == '' or (isinstance(wc_id, str) and wc_id.strip() == ''):
                print(f"      ❌ PROBLEMATIC ID: '{wc_id}' (type: {type(wc_id)})")
                has_problems = True
            
            if wc_name is None or wc_name == '' or (isinstance(wc_name, str) and wc_name.strip() == ''):
                print(f"      ❌ PROBLEMATIC NAME: '{wc_name}' (type: {type(wc_name)})")
                has_problems = True
        
        if has_problems:
            problematic_clients.append({
                'name': client_name,
                'id': client_id,
                'work_centers': work_centers
            })
    
    print(f"\n📊 Summary:")
    print(f"   Total clients: {len(clients)}")
    print(f"   Clients with problematic work centers: {len(problematic_clients)}")
    
    if problematic_clients:
        print(f"\n⚠️  Problematic clients:")
        for client in problematic_clients:
            print(f"   - {client['name']} (ID: {client['id']})")
            for wc in client['work_centers']:
                wc_id = wc.get('id', None)
                wc_name = wc.get('nombre', None)
                if (wc_id is None or wc_id == '' or (isinstance(wc_id, str) and wc_id.strip() == '')) or \
                   (wc_name is None or wc_name == '' or (isinstance(wc_name, str) and wc_name.strip() == '')):
                    print(f"     * ID: '{wc_id}' | Name: '{wc_name}'")
    else:
        print("✅ No clients with problematic work centers found")

if __name__ == "__main__":
    check_all_clients_work_centers()
import requests
import json

def test_enagas_work_centers():
    """Test the actual work center data for ENAGAS client"""
    
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
    
    # Get all clients to find ENAGAS
    clients_response = requests.get(f"{api_url}/clientes", headers=headers)
    clients = clients_response.json()
    
    enagas_client = None
    for client in clients:
        if "ENAGAS TRANSPORTE" in client.get('nombre', ''):
            enagas_client = client
            break
    
    if not enagas_client:
        print("❌ ENAGAS client not found")
        return
    
    print(f"✅ Found ENAGAS client: {enagas_client['id']}")
    print(f"   Name: {enagas_client['nombre']}")
    
    # Get work centers directly from client data
    print(f"\n📍 Work centers in client data:")
    work_centers_in_client = enagas_client.get('centros_trabajo', [])
    for i, wc in enumerate(work_centers_in_client):
        wc_id = wc.get('id', 'MISSING')
        wc_name = wc.get('nombre', 'MISSING')
        print(f"   {i+1}. ID: '{wc_id}' | Name: '{wc_name}'")
        
        # Check for problematic values
        if not wc_id or wc_id.strip() == '':
            print(f"      ⚠️  PROBLEMATIC: Empty or None ID detected!")
        if not wc_name or wc_name.strip() == '':
            print(f"      ⚠️  PROBLEMATIC: Empty or None name detected!")
    
    # Get work centers via API endpoint
    wc_response = requests.get(f"{api_url}/clientes/{enagas_client['id']}/centros-trabajo", headers=headers)
    work_centers_api = wc_response.json()
    
    print(f"\n📍 Work centers from API endpoint:")
    for i, wc in enumerate(work_centers_api):
        wc_id = wc.get('id', 'MISSING')
        wc_name = wc.get('nombre', 'MISSING')
        print(f"   {i+1}. ID: '{wc_id}' | Name: '{wc_name}'")
        
        # Check for problematic values
        if not wc_id or wc_id.strip() == '':
            print(f"      ⚠️  PROBLEMATIC: Empty or None ID detected!")
        if not wc_name or wc_name.strip() == '':
            print(f"      ⚠️  PROBLEMATIC: Empty or None name detected!")
    
    # Test the filtering logic that should be applied in frontend
    print(f"\n🔍 Testing frontend filtering logic:")
    
    # Simulate the filtering from loadClientWorkCenters
    valid_work_centers = [
        wc for wc in work_centers_api 
        if wc and wc.get('id') and wc.get('id').strip() != '' and wc.get('nombre') and wc.get('nombre').strip() != ''
    ]
    
    print(f"   Original count: {len(work_centers_api)}")
    print(f"   After filtering: {len(valid_work_centers)}")
    
    for i, wc in enumerate(valid_work_centers):
        print(f"   {i+1}. ID: '{wc['id']}' | Name: '{wc['nombre']}'")
    
    # Simulate the rendering filtering
    render_filtered = [
        wc for wc in valid_work_centers
        if wc.get('id') and wc.get('id').strip() != ''
    ]
    
    print(f"   After render filtering: {len(render_filtered)}")
    
    if len(work_centers_api) != len(valid_work_centers):
        print("⚠️  Some work centers were filtered out - this suggests there were problematic entries")
    else:
        print("✅ No work centers were filtered out - all have valid IDs and names")

if __name__ == "__main__":
    test_enagas_work_centers()
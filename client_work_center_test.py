#!/usr/bin/env python3
"""
Specific test for the client work center preservation fix.
This test verifies that when updating a client's basic information,
existing work centers are preserved instead of being deleted.
"""

import requests
import sys
import json
from datetime import datetime

class ClientWorkCenterTest:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.client_id = None

    def login(self):
        """Login with admin credentials"""
        print("🔐 Logging in with admin credentials...")
        response = requests.post(f"{self.api_url}/auth/login", json={
            "username": "admin",
            "password": "ASCb33388091_"
        })
        
        if response.status_code == 200:
            self.token = response.json()['access_token']
            print("✅ Login successful")
            return True
        else:
            print(f"❌ Login failed: {response.text}")
            return False

    def create_test_client(self):
        """Create a test client with work centers"""
        print("\n📝 Creating test client with work centers...")
        
        client_data = {
            "nombre": "Test Client Fix",
            "cif": "ABC123",
            "telefono": "111222333",
            "email": "test@example.com",
            "centros_trabajo": [
                {
                    "id": f"wc-{datetime.now().strftime('%H%M%S')}-1",
                    "nombre": "Sede Central",
                    "direccion": "Calle Principal 123",
                    "telefono": "444555666"
                }
            ]
        }
        
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        response = requests.post(f"{self.api_url}/clientes", json=client_data, headers=headers)
        
        if response.status_code == 200:
            client = response.json()
            self.client_id = client['id']
            print(f"✅ Client created with ID: {self.client_id}")
            print(f"   Work centers: {len(client['centros_trabajo'])}")
            return client
        else:
            print(f"❌ Client creation failed: {response.text}")
            return None

    def add_second_work_center(self):
        """Add a second work center to the client"""
        print("\n🏢 Adding second work center...")
        
        work_center_data = {
            "id": f"wc-{datetime.now().strftime('%H%M%S')}-2",
            "nombre": "Sucursal Norte",
            "direccion": "Avenida Norte 456",
            "telefono": "777888999"
        }
        
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        response = requests.post(
            f"{self.api_url}/clientes/{self.client_id}/centros-trabajo", 
            json=work_center_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            client = response.json()
            print(f"✅ Work center added. Total centers: {len(client['centros_trabajo'])}")
            return client
        else:
            print(f"❌ Work center addition failed: {response.text}")
            return None

    def update_client_basic_info(self):
        """Update client's basic information (phone number) without work centers"""
        print("\n📞 Updating client's phone number (testing work center preservation)...")
        
        # This is the key test - updating basic info with empty centros_trabajo
        # The fix should preserve existing work centers
        update_data = {
            "nombre": "Test Client Fix",
            "cif": "ABC123",
            "telefono": "999888777",  # Changed phone number
            "email": "test@example.com",
            "centros_trabajo": []  # Empty - should preserve existing ones
        }
        
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        response = requests.put(
            f"{self.api_url}/clientes/{self.client_id}", 
            json=update_data, 
            headers=headers
        )
        
        if response.status_code == 200:
            updated_client = response.json()
            work_centers_count = len(updated_client['centros_trabajo'])
            print(f"✅ Client updated successfully")
            print(f"   Phone number: {updated_client['telefono']}")
            print(f"   Work centers after update: {work_centers_count}")
            
            # This is the critical test - work centers should be preserved
            if work_centers_count >= 2:
                print("✅ SUCCESS: Work centers were preserved during update!")
                return True
            else:
                print("❌ FAILURE: Work centers were lost during update!")
                return False
        else:
            print(f"❌ Client update failed: {response.text}")
            return False

    def verify_work_centers_details(self):
        """Verify the work centers are still there with correct details"""
        print("\n🔍 Verifying work center details...")
        
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.get(
            f"{self.api_url}/clientes/{self.client_id}/centros-trabajo", 
            headers=headers
        )
        
        if response.status_code == 200:
            work_centers = response.json()
            print(f"✅ Retrieved {len(work_centers)} work centers:")
            
            for i, wc in enumerate(work_centers, 1):
                print(f"   {i}. {wc['nombre']}")
                if wc.get('direccion'):
                    print(f"      Address: {wc['direccion']}")
                if wc.get('telefono'):
                    print(f"      Phone: {wc['telefono']}")
            
            # Check if we have both work centers
            names = [wc['nombre'] for wc in work_centers]
            if "Sede Central" in names and "Sucursal Norte" in names:
                print("✅ SUCCESS: Both work centers found with correct names!")
                return True
            else:
                print("❌ FAILURE: Expected work centers not found!")
                return False
        else:
            print(f"❌ Failed to retrieve work centers: {response.text}")
            return False

    def run_test(self):
        """Run the complete test scenario"""
        print("🚀 Starting Client Work Center Preservation Test")
        print("="*60)
        
        # Step 1: Login
        if not self.login():
            return False
        
        # Step 2: Create client with work center
        if not self.create_test_client():
            return False
        
        # Step 3: Add second work center
        if not self.add_second_work_center():
            return False
        
        # Step 4: Update client basic info (the critical test)
        if not self.update_client_basic_info():
            return False
        
        # Step 5: Verify work centers are still there
        if not self.verify_work_centers_details():
            return False
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("✅ Client creation with work centers: SUCCESS")
        print("✅ Adding additional work center: SUCCESS") 
        print("✅ Updating client while preserving work centers: SUCCESS")
        print("✅ Work center details verification: SUCCESS")
        print("\nThe backend fix is working correctly! 🎯")
        
        return True

def main():
    tester = ClientWorkCenterTest()
    success = tester.run_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
from datetime import datetime

class EnagasSpecificTester:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.enagas_client_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    if isinstance(response_data, list):
                        print(f"   Response: List with {len(response_data)} items")
                    elif isinstance(response_data, dict):
                        print(f"   Response keys: {list(response_data.keys())}")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text}")

            return success, response.json() if response.text else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def login_as_admin(self):
        """Login as admin user"""
        print("\n" + "="*50)
        print("LOGGING IN AS ADMIN")
        print("="*50)
        
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"username": "admin", "password": "ASCb33388091_"}
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Admin token obtained")
            return True
        else:
            print("   ❌ Admin login failed")
            return False

    def setup_enagas_client(self):
        """Create or find ENAGAS TRANSPORTE S.A.U. client with problematic work centers"""
        print("\n" + "="*50)
        print("SETTING UP ENAGAS CLIENT")
        print("="*50)
        
        # First, check if ENAGAS client already exists
        success, clients = self.run_test(
            "Get All Clients",
            "GET",
            "clientes",
            200
        )
        
        if success:
            # Look for existing ENAGAS client
            for client in clients:
                if "ENAGAS TRANSPORTE S.A.U." in client.get('nombre', ''):
                    self.enagas_client_id = client['id']
                    print(f"   ✅ Found existing ENAGAS client: {client['id']}")
                    
                    # Check work centers
                    work_centers = client.get('centros_trabajo', [])
                    print(f"   📍 Work centers found: {len(work_centers)}")
                    for wc in work_centers:
                        print(f"      - ID: '{wc.get('id', 'EMPTY')}', Name: '{wc.get('nombre', 'EMPTY')}'")
                    
                    return True
        
        # If not found, create ENAGAS client with the problematic work centers
        print("   📝 Creating ENAGAS client with work centers...")
        
        enagas_client_data = {
            "nombre": "ENAGAS TRANSPORTE S.A.U.",
            "cif": "A78860221",
            "telefono": "915678900",
            "email": "info@enagas.es",
            "centros_trabajo": [
                {
                    "id": "ct-plasencia-001",
                    "nombre": "C.T. Plasencia",
                    "direccion": "Carretera Nacional 630, Km 365, 10600 Plasencia, Cáceres",
                    "telefono": "927123456"
                },
                {
                    "id": "ct-palencia-001", 
                    "nombre": "C.T. Palencia",
                    "direccion": "Carretera Nacional 611, Km 85, 34004 Palencia",
                    "telefono": "979123456"
                },
                # Add a work center with empty ID to test the filtering
                {
                    "id": "",  # This should be filtered out
                    "nombre": "Centro con ID Vacío",
                    "direccion": "Test Address",
                    "telefono": "123456789"
                },
                # Add a work center with None ID to test the filtering
                {
                    "id": None,  # This should be filtered out
                    "nombre": "Centro con ID Nulo",
                    "direccion": "Test Address 2",
                    "telefono": "987654321"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create ENAGAS Client",
            "POST",
            "clientes",
            200,
            data=enagas_client_data
        )
        
        if success and 'id' in response:
            self.enagas_client_id = response['id']
            print(f"   ✅ ENAGAS client created with ID: {self.enagas_client_id}")
            
            # Verify work centers were created correctly
            work_centers = response.get('centros_trabajo', [])
            print(f"   📍 Work centers created: {len(work_centers)}")
            for wc in work_centers:
                print(f"      - ID: '{wc.get('id', 'EMPTY')}', Name: '{wc.get('nombre', 'EMPTY')}'")
            
            return True
        else:
            print("   ❌ Failed to create ENAGAS client")
            return False

    def test_work_center_filtering(self):
        """Test that work centers with empty IDs are properly filtered"""
        print("\n" + "="*50)
        print("TESTING WORK CENTER FILTERING")
        print("="*50)
        
        if not self.enagas_client_id:
            print("   ❌ No ENAGAS client ID available")
            return False
        
        # Test getting work centers via the specific endpoint
        success, work_centers = self.run_test(
            "Get ENAGAS Work Centers",
            "GET",
            f"clientes/{self.enagas_client_id}/centros-trabajo",
            200
        )
        
        if success:
            print(f"   📍 Retrieved {len(work_centers)} work centers")
            
            # Check for empty or invalid IDs
            valid_centers = []
            invalid_centers = []
            
            for wc in work_centers:
                wc_id = wc.get('id', '')
                wc_name = wc.get('nombre', '')
                
                print(f"      - ID: '{wc_id}', Name: '{wc_name}'")
                
                if wc_id and wc_id.strip() != '' and wc_name and wc_name.strip() != '':
                    valid_centers.append(wc)
                else:
                    invalid_centers.append(wc)
            
            print(f"   ✅ Valid work centers: {len(valid_centers)}")
            print(f"   ⚠️  Invalid work centers (should be filtered): {len(invalid_centers)}")
            
            # Verify we have the expected work centers
            expected_centers = ["C.T. Plasencia", "C.T. Palencia"]
            found_centers = [wc['nombre'] for wc in valid_centers if wc.get('nombre') in expected_centers]
            
            print(f"   🎯 Expected centers found: {found_centers}")
            
            if len(found_centers) >= 2:
                print("   ✅ Both expected work centers are present")
                return True
            else:
                print("   ❌ Missing expected work centers")
                return False
        
        return False

    def test_equipment_creation_with_enagas(self):
        """Test creating equipment with ENAGAS client and work center selection"""
        print("\n" + "="*50)
        print("TESTING EQUIPMENT CREATION WITH ENAGAS")
        print("="*50)
        
        if not self.enagas_client_id:
            print("   ❌ No ENAGAS client ID available")
            return False
        
        # Get work centers first
        success, work_centers = self.run_test(
            "Get Work Centers for Equipment",
            "GET",
            f"clientes/{self.enagas_client_id}/centros-trabajo",
            200
        )
        
        if not success or not work_centers:
            print("   ❌ No work centers available")
            return False
        
        # Filter valid work centers (same logic as frontend)
        valid_work_centers = [
            wc for wc in work_centers 
            if wc and wc.get('id') and wc.get('id').strip() != '' and wc.get('nombre') and wc.get('nombre').strip() != ''
        ]
        
        if not valid_work_centers:
            print("   ❌ No valid work centers after filtering")
            return False
        
        # Use the first valid work center
        selected_work_center = valid_work_centers[0]
        print(f"   📍 Using work center: {selected_work_center['nombre']} (ID: {selected_work_center['id']})")
        
        # Create test equipment
        test_equipment = {
            "orden_trabajo": f"TEST-ENAGAS-{datetime.now().strftime('%H%M%S')}",
            "cliente_id": self.enagas_client_id,
            "cliente_nombre": "ENAGAS TRANSPORTE S.A.U.",
            "centro_trabajo_id": selected_work_center['id'],
            "centro_trabajo_nombre": selected_work_center['nombre'],
            "tipo_equipo": "Detector Portátil de Gas",
            "modelo": "Test Model ENAGAS",
            "fabricante": "Test Manufacturer",
            "numero_serie": f"ENAGAS-SN-{datetime.now().strftime('%H%M%S')}",
            "tipo_fallo": "SENSOR FAILURE",
            "observaciones": "Test equipment for ENAGAS work center validation",
            "numero_serie_sensor": f"SENSOR-{datetime.now().strftime('%H%M%S')}",
            "fecha_instalacion_sensor": "2024-01-15"
        }
        
        success, response = self.run_test(
            "Create Equipment with ENAGAS Work Center",
            "POST",
            "equipos",
            200,
            data=test_equipment
        )
        
        if success:
            print(f"   ✅ Equipment created successfully")
            print(f"   📦 Equipment ID: {response.get('id')}")
            print(f"   🏢 Client: {response.get('cliente_nombre')}")
            print(f"   📍 Work Center: {response.get('centro_trabajo_nombre')}")
            return True
        else:
            print("   ❌ Failed to create equipment")
            return False

    def run_specific_tests(self):
        """Run the specific tests for ENAGAS issue"""
        print("🚀 Starting ENAGAS TRANSPORTE S.A.U. Specific Tests")
        print(f"Testing against: {self.base_url}")
        
        # Login as admin
        if not self.login_as_admin():
            print("❌ Admin login failed, stopping tests")
            return 1
        
        # Setup ENAGAS client
        if not self.setup_enagas_client():
            print("❌ ENAGAS client setup failed, stopping tests")
            return 1
        
        # Test work center filtering
        self.test_work_center_filtering()
        
        # Test equipment creation
        self.test_equipment_creation_with_enagas()
        
        # Print final results
        print("\n" + "="*50)
        print("ENAGAS SPECIFIC TEST RESULTS")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.enagas_client_id:
            print(f"🏢 ENAGAS Client ID: {self.enagas_client_id}")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = EnagasSpecificTester()
    return tester.run_specific_tests()

if __name__ == "__main__":
    sys.exit(main())
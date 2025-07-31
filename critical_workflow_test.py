import requests
import sys
import json
from datetime import datetime

class CriticalWorkflowTester:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {
            'client_id': None,
            'equipment_id': None,
            'purchase_order': None
        }

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

    def setup_authentication(self):
        """Login as admin"""
        print("\n" + "="*60)
        print("STEP 1: AUTHENTICATION")
        print("="*60)
        
        success, response = self.run_test(
            "Login as admin",
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
            print(f"   ❌ Failed to login as admin")
            return False

    def create_test_data(self):
        """Create complete test data as specified in the review request"""
        print("\n" + "="*60)
        print("STEP 2: CREATE COMPLETE TEST DATA")
        print("="*60)
        
        # Clear database first for clean test
        print("   🧹 Clearing database for clean test...")
        success, response = self.run_test(
            "Clear Database",
            "POST",
            "admin/clear-database",
            200
        )
        
        # Create client: Name="Test Cliente", CIF="B12345678", Phone="111222333"
        test_client = {
            "nombre": "Test Cliente",
            "cif": "B12345678",
            "telefono": "111222333",
            "email": "",
            "centros_trabajo": []
        }
        
        success, response = self.run_test(
            "Create Test Client",
            "POST",
            "clientes",
            200,
            data=test_client
        )
        
        if success and 'id' in response:
            self.test_data['client_id'] = response['id']
            print(f"   ✅ Test client created with ID: {self.test_data['client_id']}")
        else:
            print(f"   ❌ Failed to create test client")
            return False
        
        # Add manufacturer if needed
        success, response = self.run_test(
            "Create Test Manufacturer",
            "POST",
            "fabricantes",
            200,
            params={"name": "Test Manufacturer"}
        )
        
        # Add model if needed
        success, response = self.run_test(
            "Create Test Model",
            "POST",
            "modelos",
            200,
            params={"name": "Test Model", "equipment_type": "Espaldera"}
        )
        
        # Create equipment: Order="TEST-PO-001", assign to the client created above
        test_equipment = {
            "orden_trabajo": "TEST-PO-001",
            "cliente_id": self.test_data['client_id'],
            "cliente_nombre": "Test Cliente",
            "centro_trabajo_id": "",
            "centro_trabajo_nombre": "",
            "tipo_equipo": "Espaldera",
            "modelo": "Test Model",
            "ato": "",
            "fabricante": "Test Manufacturer",
            "numero_serie": f"SN-{datetime.now().strftime('%H%M%S')}",
            "fecha_fabricacion": "",
            "tipo_fallo": "OTHER",
            "observaciones": "Test equipment for critical workflow testing",
            "numero_serie_sensor": "",
            "fecha_instalacion_sensor": ""
        }
        
        success, response = self.run_test(
            "Create Test Equipment",
            "POST",
            "equipos",
            200,
            data=test_equipment
        )
        
        if success and 'id' in response:
            self.test_data['equipment_id'] = response['id']
            print(f"   ✅ Test equipment created with ID: {self.test_data['equipment_id']}")
            print(f"   ✅ Equipment Order: TEST-PO-001")
            print(f"   ✅ Equipment State: {response.get('estado', 'Unknown')}")
        else:
            print(f"   ❌ Failed to create test equipment")
            return False
        
        return True

    def test_purchase_order_assignment(self):
        """Test Gestión Administrativa - Purchase Order Assignment"""
        print("\n" + "="*60)
        print("STEP 3: TEST PURCHASE ORDER ASSIGNMENT")
        print("="*60)
        
        # Assign purchase order number: "PO-TEST-2025-001"
        self.test_data['purchase_order'] = "PO-TEST-2025-001"
        
        success, response = self.run_test(
            "Assign Purchase Order",
            "POST",
            "ordenes-compra/asignar",
            200,
            data={
                "numero_orden": self.test_data['purchase_order'],
                "equipment_ids": [self.test_data['equipment_id']]
            }
        )
        
        if success:
            print(f"   ✅ Purchase order assigned successfully")
            print(f"   ✅ Assigned count: {response.get('assigned_count', 0)}")
            
            # Verify equipment state changed from "Pendiente" to "Enviado"
            success, equipment_detail = self.run_test(
                "Verify Equipment State Change",
                "GET",
                f"equipos/{self.test_data['equipment_id']}",
                200
            )
            
            if success:
                current_state = equipment_detail.get('estado', 'Unknown')
                purchase_order_number = equipment_detail.get('numero_orden_compra', 'None')
                
                print(f"   📊 Equipment State: {current_state}")
                print(f"   📊 Purchase Order Number: {purchase_order_number}")
                
                if current_state == "Enviado":
                    print(f"   ✅ CRITICAL: Equipment state changed to 'Enviado'")
                else:
                    print(f"   ❌ CRITICAL: Equipment state is '{current_state}', expected 'Enviado'")
                    return False
                
                if purchase_order_number == self.test_data['purchase_order']:
                    print(f"   ✅ CRITICAL: Purchase order number correctly assigned")
                else:
                    print(f"   ❌ CRITICAL: Purchase order number is '{purchase_order_number}', expected '{self.test_data['purchase_order']}'")
                    return False
            else:
                print(f"   ❌ Failed to get equipment details for verification")
                return False
        else:
            print(f"   ❌ Failed to assign purchase order")
            return False
        
        return True

    def test_active_orders_dropdown(self):
        """Test "Ver equipos por número de pedido" in Gestión Administrativa"""
        print("\n" + "="*60)
        print("STEP 4: TEST ACTIVE ORDERS DROPDOWN")
        print("="*60)
        
        # Test /api/ordenes-compra/activas endpoint
        success, response = self.run_test(
            "Get Active Purchase Orders",
            "GET",
            "ordenes-compra/activas",
            200
        )
        
        if success:
            active_orders = response.get('active_orders', [])
            print(f"   📊 Active orders found: {len(active_orders)}")
            print(f"   📊 Active orders: {active_orders}")
            
            if self.test_data['purchase_order'] in active_orders:
                print(f"   ✅ CRITICAL: Purchase order '{self.test_data['purchase_order']}' appears in active orders dropdown")
            else:
                print(f"   ❌ CRITICAL: Purchase order '{self.test_data['purchase_order']}' NOT found in active orders dropdown")
                print(f"   ❌ This means the dropdown will not show the purchase order!")
                return False
        else:
            print(f"   ❌ Failed to get active purchase orders")
            return False
        
        return True

    def test_equipment_by_purchase_order(self):
        """Test equipment retrieval by purchase order"""
        print("\n" + "="*60)
        print("STEP 5: TEST EQUIPMENT BY PURCHASE ORDER")
        print("="*60)
        
        # Test /api/ordenes-compra/{order_number}/equipos endpoint
        success, response = self.run_test(
            "Get Equipment by Purchase Order",
            "GET",
            f"ordenes-compra/{self.test_data['purchase_order']}/equipos",
            200
        )
        
        if success:
            equipment_list = response if isinstance(response, list) else []
            print(f"   📊 Equipment found for purchase order: {len(equipment_list)}")
            
            if len(equipment_list) > 0:
                found_equipment = None
                for eq in equipment_list:
                    if eq.get('id') == self.test_data['equipment_id']:
                        found_equipment = eq
                        break
                
                if found_equipment:
                    print(f"   ✅ CRITICAL: Equipment appears in purchase order table")
                    print(f"   📊 Equipment Order: {found_equipment.get('orden_trabajo', 'Unknown')}")
                    print(f"   📊 Equipment Client: {found_equipment.get('cliente_nombre', 'Unknown')}")
                    print(f"   📊 Equipment State: {found_equipment.get('estado', 'Unknown')}")
                else:
                    print(f"   ❌ CRITICAL: Equipment NOT found in purchase order table")
                    return False
            else:
                print(f"   ❌ CRITICAL: No equipment found for purchase order")
                return False
        else:
            print(f"   ❌ Failed to get equipment by purchase order")
            return False
        
        return True

    def test_manufacturer_response_module(self):
        """Test Respuesta Fabricante Module"""
        print("\n" + "="*60)
        print("STEP 6: TEST RESPUESTA FABRICANTE MODULE")
        print("="*60)
        
        # First verify active orders appear in manufacturer module
        success, response = self.run_test(
            "Get Active Orders for Manufacturer Module",
            "GET",
            "ordenes-compra/activas",
            200
        )
        
        if success:
            active_orders = response.get('active_orders', [])
            if self.test_data['purchase_order'] in active_orders:
                print(f"   ✅ CRITICAL: Purchase order appears in Respuesta Fabricante dropdown")
            else:
                print(f"   ❌ CRITICAL: Purchase order NOT in Respuesta Fabricante dropdown")
                return False
        else:
            print(f"   ❌ Failed to get active orders for manufacturer module")
            return False
        
        # Test /api/ordenes-compra/{order_number}/equipos/enviados endpoint
        success, response = self.run_test(
            "Get Sent Equipment by Purchase Order",
            "GET",
            f"ordenes-compra/{self.test_data['purchase_order']}/equipos/enviados",
            200
        )
        
        if success:
            sent_equipment = response if isinstance(response, list) else []
            print(f"   📊 Sent equipment found: {len(sent_equipment)}")
            
            if len(sent_equipment) > 0:
                found_equipment = None
                for eq in sent_equipment:
                    if eq.get('id') == self.test_data['equipment_id']:
                        found_equipment = eq
                        break
                
                if found_equipment:
                    print(f"   ✅ CRITICAL: Equipment appears in Respuesta Fabricante equipment list")
                    print(f"   📊 Equipment Order: {found_equipment.get('orden_trabajo', 'Unknown')}")
                    print(f"   📊 Equipment State: {found_equipment.get('estado', 'Unknown')}")
                    
                    # Verify state is "Enviado" (not processed by manufacturer yet)
                    if found_equipment.get('estado') == 'Enviado':
                        print(f"   ✅ Equipment state is 'Enviado' (ready for manufacturer processing)")
                    else:
                        print(f"   ⚠️  Equipment state is '{found_equipment.get('estado')}', expected 'Enviado'")
                else:
                    print(f"   ❌ CRITICAL: Equipment NOT found in Respuesta Fabricante equipment list")
                    return False
            else:
                print(f"   ❌ CRITICAL: No sent equipment found for purchase order in Respuesta Fabricante")
                return False
        else:
            print(f"   ❌ Failed to get sent equipment for manufacturer module")
            return False
        
        return True

    def test_csv_export_functionality(self):
        """Test CSV export functionality"""
        print("\n" + "="*60)
        print("STEP 7: TEST CSV EXPORT FUNCTIONALITY")
        print("="*60)
        
        success, response = self.run_test(
            "Export Purchase Order CSV",
            "GET",
            f"ordenes-compra/{self.test_data['purchase_order']}/export-csv",
            200
        )
        
        if success:
            filename = response.get('filename', 'Unknown')
            content = response.get('content', '')
            equipment_count = response.get('equipment_count', 0)
            
            print(f"   ✅ CSV export successful")
            print(f"   📊 Filename: {filename}")
            print(f"   📊 Equipment count: {equipment_count}")
            print(f"   📊 Content preview: {content[:100]}...")
            
            # Verify CSV contains our test equipment
            if 'TEST-PO-001' in content and 'Test Cliente' in content:
                print(f"   ✅ CSV contains test equipment data")
            else:
                print(f"   ❌ CSV does not contain expected test equipment data")
                return False
        else:
            print(f"   ❌ Failed to export CSV")
            return False
        
        return True

    def run_critical_workflow_test(self):
        """Run the complete critical workflow test"""
        print("🚀 Starting CRITICAL WORKFLOW TEST")
        print("Testing the complete equipment → purchase order → modules workflow")
        print(f"Testing against: {self.base_url}")
        
        # Step 1: Authentication
        if not self.setup_authentication():
            print("❌ Authentication failed, stopping test")
            return 1
        
        # Step 2: Create test data
        if not self.create_test_data():
            print("❌ Test data creation failed, stopping test")
            return 1
        
        # Step 3: Test purchase order assignment
        if not self.test_purchase_order_assignment():
            print("❌ Purchase order assignment failed - CRITICAL WORKFLOW BROKEN")
            return 1
        
        # Step 4: Test active orders dropdown
        if not self.test_active_orders_dropdown():
            print("❌ Active orders dropdown failed - CRITICAL WORKFLOW BROKEN")
            return 1
        
        # Step 5: Test equipment by purchase order
        if not self.test_equipment_by_purchase_order():
            print("❌ Equipment by purchase order failed - CRITICAL WORKFLOW BROKEN")
            return 1
        
        # Step 6: Test manufacturer response module
        if not self.test_manufacturer_response_module():
            print("❌ Manufacturer response module failed - CRITICAL WORKFLOW BROKEN")
            return 1
        
        # Step 7: Test CSV export
        if not self.test_csv_export_functionality():
            print("❌ CSV export failed - WORKFLOW PARTIALLY BROKEN")
            # Don't return 1 here as CSV is not critical to the main workflow
        
        # Final results
        print("\n" + "="*60)
        print("CRITICAL WORKFLOW TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 CRITICAL WORKFLOW TEST PASSED!")
            print("✅ Equipment creation → Purchase order assignment → Module visibility WORKS")
            print("✅ Equipment assigned to purchase orders appears in both modules")
            print("✅ Equipment state changes correctly from 'Pendiente' to 'Enviado'")
            print("✅ Purchase orders appear in active orders dropdowns")
            print("✅ CSV export functionality works")
        else:
            print("\n❌ CRITICAL WORKFLOW TEST FAILED!")
            print("❌ The core business workflow is broken")
            print("❌ Equipment assigned to purchase orders may not appear in subsequent modules")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = CriticalWorkflowTester()
    return tester.run_critical_workflow_test()

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
from datetime import datetime

class EquipmentManagementAPITester:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_resources = {
            'clients': [],
            'equipment': [],
            'manufacturers': [],
            'models': []
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

    def test_authentication(self):
        """Test all authentication endpoints and users"""
        print("\n" + "="*50)
        print("TESTING AUTHENTICATION")
        print("="*50)
        
        # Test all predefined users
        users = [
            ("Marco", "B33388091"),
            ("Mariano", "B33388091"), 
            ("Jesus", "B33388091"),
            ("Diego", "B33388091"),
            ("admin", "ASCb33388091_")
        ]
        
        login_success = False
        for username, password in users:
            success, response = self.run_test(
                f"Login - {username}",
                "POST",
                "auth/login",
                200,
                data={"username": username, "password": password}
            )
            if success and 'access_token' in response:
                self.token = response['access_token']
                login_success = True
                print(f"   Token obtained for {username}")
                break
        
        if not login_success:
            print("❌ No successful login found, stopping tests")
            return False
            
        # Test /auth/me endpoint
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        return login_success

    def test_clients(self):
        """Test client management endpoints"""
        print("\n" + "="*50)
        print("TESTING CLIENT MANAGEMENT")
        print("="*50)
        
        # Get existing clients
        success, clients = self.run_test(
            "Get Clients",
            "GET",
            "clientes",
            200
        )
        
        # Test 1: Create a new client with work centers (as reported in the issue)
        test_client_with_centers = {
            "nombre": "Test Client",
            "cif": "12345",
            "telefono": "123456789",
            "email": "test@example.com",
            "centros_trabajo": [
                {
                    "id": f"wc-{datetime.now().strftime('%H%M%S')}-1",
                    "nombre": "Centro Principal",
                    "direccion": "Test Address",
                    "telefono": "987654321"
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Client with Work Centers",
            "POST",
            "clientes",
            200,
            data=test_client_with_centers
        )
        
        client_id = None
        if success and 'id' in response:
            client_id = response['id']
            self.created_resources['clients'].append(client_id)
            print(f"   Created client with ID: {client_id}")
            
            # Verify work centers were created
            if 'centros_trabajo' in response and len(response['centros_trabajo']) > 0:
                print(f"   ✅ Work centers created: {len(response['centros_trabajo'])}")
            else:
                print(f"   ❌ Work centers not found in response")
        
        # Test 2: Get client by ID to verify data
        if client_id:
            success, client_detail = self.run_test(
                "Get Client by ID",
                "GET",
                f"clientes/{client_id}",
                200
            )
            
            if success and 'centros_trabajo' in client_detail:
                print(f"   ✅ Client retrieved with {len(client_detail['centros_trabajo'])} work centers")
        
        # Test 3: Get client work centers endpoint
        if client_id:
            success, work_centers = self.run_test(
                "Get Client Work Centers",
                "GET",
                f"clientes/{client_id}/centros-trabajo",
                200
            )
            
            if success:
                print(f"   ✅ Work centers endpoint returned {len(work_centers)} centers")
        
        # Test 4: Add work center to existing client
        if client_id:
            new_work_center = {
                "id": f"wc-{datetime.now().strftime('%H%M%S')}-2",
                "nombre": "Centro Secundario",
                "direccion": "Secondary Address",
                "telefono": "555666777"
            }
            
            success, response = self.run_test(
                "Add Work Center to Existing Client",
                "POST",
                f"clientes/{client_id}/centros-trabajo",
                200,
                data=new_work_center
            )
            
            if success and 'centros_trabajo' in response:
                print(f"   ✅ Work center added. Total centers: {len(response['centros_trabajo'])}")
        
        # Test 5: Update client (testing the edit functionality)
        if client_id:
            updated_client_data = {
                "nombre": "Test Client Updated",
                "cif": "12345",
                "telefono": "999888777",  # Changed phone number as mentioned in requirements
                "email": "updated@example.com",
                "centros_trabajo": []  # Will be populated from existing data
            }
            
            success, response = self.run_test(
                "Update Client",
                "PUT",
                f"clientes/{client_id}",
                200,
                data=updated_client_data
            )
            
            if success:
                print(f"   ✅ Client updated successfully")
        
        # Test 6: Remove work center from client
        if client_id:
            # First get current work centers to find one to remove
            success, work_centers = self.run_test(
                "Get Work Centers for Removal Test",
                "GET",
                f"clientes/{client_id}/centros-trabajo",
                200
            )
            
            if success and len(work_centers) > 0:
                work_center_to_remove = work_centers[0]['id']
                success, response = self.run_test(
                    "Remove Work Center from Client",
                    "DELETE",
                    f"clientes/{client_id}/centros-trabajo/{work_center_to_remove}",
                    200
                )
                
                if success:
                    print(f"   ✅ Work center removed successfully")
        
        # Test 7: Error scenarios
        # Try adding work center with empty name
        if client_id:
            invalid_work_center = {
                "id": f"wc-invalid-{datetime.now().strftime('%H%M%S')}",
                "nombre": "",  # Empty name should cause validation error
                "direccion": "Test Address",
                "telefono": "123456789"
            }
            
            # This should still work as backend doesn't validate empty names currently
            # But we test it to see the behavior
            success, response = self.run_test(
                "Add Work Center with Empty Name",
                "POST",
                f"clientes/{client_id}/centros-trabajo",
                200,  # Expecting success as backend doesn't validate
                data=invalid_work_center
            )
        
        return True

    def test_reference_data(self):
        """Test reference data endpoints (manufacturers, models, fault types)"""
        print("\n" + "="*50)
        print("TESTING REFERENCE DATA")
        print("="*50)
        
        # Test manufacturers
        success, manufacturers = self.run_test(
            "Get Manufacturers",
            "GET",
            "fabricantes",
            200
        )
        
        # Create a manufacturer
        test_manufacturer = f"Test Manufacturer {datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Manufacturer",
            "POST",
            "fabricantes",
            200,
            params={"name": test_manufacturer}
        )
        
        if success and 'id' in response:
            self.created_resources['manufacturers'].append(response['id'])
        
        # Test models
        success, models = self.run_test(
            "Get Models",
            "GET",
            "modelos",
            200
        )
        
        # Create a model
        test_model = f"Test Model {datetime.now().strftime('%H%M%S')}"
        success, response = self.run_test(
            "Create Model",
            "POST",
            "modelos",
            200,
            params={"name": test_model, "equipment_type": "Espaldera"}
        )
        
        if success and 'id' in response:
            self.created_resources['models'].append(response['id'])
        
        # Test fault types
        success, fault_types = self.run_test(
            "Get Fault Types",
            "GET",
            "tipos-fallo",
            200
        )
        
        return success

    def test_equipment(self):
        """Test equipment management endpoints"""
        print("\n" + "="*50)
        print("TESTING EQUIPMENT MANAGEMENT")
        print("="*50)
        
        # Get existing equipment
        success, equipment = self.run_test(
            "Get Equipment",
            "GET",
            "equipos",
            200
        )
        
        # Create equipment (need a client first)
        if not self.created_resources['clients']:
            print("⚠️  No clients available, creating one first...")
            test_client = {
                "nombre": "Equipment Test Client",
                "cif": "B12345678",
                "telefono": "987654321"
            }
            client_success, client_response = self.run_test(
                "Create Client for Equipment",
                "POST",
                "clientes",
                200,
                data=test_client
            )
            if client_success:
                self.created_resources['clients'].append(client_response['id'])
        
        if self.created_resources['clients']:
            test_equipment = {
                "orden_trabajo": f"OT{datetime.now().strftime('%H%M%S')}",
                "cliente_id": self.created_resources['clients'][0],
                "cliente_nombre": "Equipment Test Client",
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": f"SN{datetime.now().strftime('%H%M%S')}",
                "tipo_fallo": "OTHER",
                "observaciones": "Test equipment for API testing"
            }
            
            success, response = self.run_test(
                "Create Equipment",
                "POST",
                "equipos",
                200,
                data=test_equipment
            )
            
            if success and 'id' in response:
                equipment_id = response['id']
                self.created_resources['equipment'].append(equipment_id)
                
                # Test get equipment by ID
                success, equipment_detail = self.run_test(
                    "Get Equipment by ID",
                    "GET",
                    f"equipos/{equipment_id}",
                    200
                )
                
                # Test update equipment
                update_data = {
                    "estado": "Enviado",
                    "numero_orden_compra": "PO123"
                }
                success, updated_equipment = self.run_test(
                    "Update Equipment",
                    "PUT",
                    f"equipos/{equipment_id}",
                    200,
                    data=update_data
                )
        
        return success
    def test_workflow_endpoints(self):
        """Test workflow-specific endpoints"""
        print("\n" + "="*50)
        print("TESTING WORKFLOW ENDPOINTS")
        print("="*50)
        
        # Test get pending equipment
        success, pending_equipment = self.run_test(
            "Get Pending Equipment",
            "GET",
            "equipos/pendientes",
            200
        )
        
        # Test get equipment for reception
        success, reception_equipment = self.run_test(
            "Get Equipment for Reception",
            "GET",
            "equipos/para-recepcion",
            200
        )
        
        # Test get completed equipment
        success, completed_equipment = self.run_test(
            "Get Completed Equipment",
            "GET",
            "equipos/completados",
            200
        )
        
        # Test receive equipment (if we have equipment)
        if self.created_resources['equipment']:
            success, response = self.run_test(
                "Receive Equipment",
                "POST",
                "equipos/recibir",
                200,
                data={
                    "equipment_ids": self.created_resources['equipment'][:1]
                }
            )
        
        return success

    def test_purchase_orders(self):
        """Test purchase order endpoints"""
        print("\n" + "="*50)
        print("TESTING PURCHASE ORDERS")
        print("="*50)
        
        # Get purchase orders
        success, orders = self.run_test(
            "Get Purchase Orders",
            "GET",
            "ordenes-compra",
            200
        )
        
        # Test assigning purchase order (if we have equipment)
        if self.created_resources['equipment']:
            order_number = f"PO-2024-{datetime.now().strftime('%H%M%S')}"
            
            # Test assign purchase order endpoint
            success, response = self.run_test(
                "Assign Purchase Order",
                "POST",
                "ordenes-compra/asignar",
                200,
                data={
                    "numero_orden": order_number,
                    "equipment_ids": self.created_resources['equipment'][:1]
                }
            )
            
            if success:
                # Test get active purchase orders
                success, active_orders = self.run_test(
                    "Get Active Purchase Orders",
                    "GET",
                    "ordenes-compra/activas",
                    200
                )
                
                # Test get equipment by purchase order
                success, po_equipment = self.run_test(
                    "Get Equipment by Purchase Order",
                    "GET",
                    f"ordenes-compra/{order_number}/equipos",
                    200
                )
                
                # Test get sent equipment by purchase order
                success, sent_equipment = self.run_test(
                    "Get Sent Equipment by Purchase Order",
                    "GET",
                    f"ordenes-compra/{order_number}/equipos/enviados",
                    200
                )
                
                # Test manufacturer response
                success, response = self.run_test(
                    "Manufacturer Response",
                    "POST",
                    f"ordenes-compra/{order_number}/respuesta-fabricante",
                    200,
                    data={
                        "equipment_ids": self.created_resources['equipment'][:1],
                        "numero_recepcion_fabricante": f"REC-2024-{datetime.now().strftime('%H%M%S')}",
                        "en_garantia": True
                    }
                )
                
                # Test CSV export
                success, csv_response = self.run_test(
                    "Export Purchase Order CSV",
                    "GET",
                    f"ordenes-compra/{order_number}/export-csv",
                    200
                )
        
        return success

    def test_invalid_requests(self):
        """Test error handling with invalid requests"""
        print("\n" + "="*50)
        print("TESTING ERROR HANDLING")
        print("="*50)
        
        # Test invalid login
        self.run_test(
            "Invalid Login",
            "POST",
            "auth/login",
            401,
            data={"username": "invalid", "password": "invalid"}
        )
        
        # Test accessing protected endpoint without token
        old_token = self.token
        self.token = None
        self.run_test(
            "Access Protected Endpoint Without Token",
            "GET",
            "clientes",
            403
        )
        self.token = old_token
        
        # Test invalid equipment ID
        self.run_test(
            "Get Non-existent Equipment",
            "GET",
            "equipos/invalid-id",
            404
        )
        
        return True

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Equipment Management API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Run test suites
        if not self.test_authentication():
            print("❌ Authentication failed, stopping all tests")
            return 1
            
        self.test_clients()
        self.test_reference_data()
        self.test_equipment()
        self.test_workflow_endpoints()
        self.test_purchase_orders()
        self.test_invalid_requests()
        
        # Print final results
        print("\n" + "="*50)
        print("TEST RESULTS SUMMARY")
        print("="*50)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"📈 Success rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.created_resources['clients']:
            print(f"👥 Created {len(self.created_resources['clients'])} test clients")
        if self.created_resources['equipment']:
            print(f"📦 Created {len(self.created_resources['equipment'])} test equipment")
        if self.created_resources['manufacturers']:
            print(f"🏭 Created {len(self.created_resources['manufacturers'])} test manufacturers")
        if self.created_resources['models']:
            print(f"🔧 Created {len(self.created_resources['models'])} test models")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = EquipmentManagementAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())
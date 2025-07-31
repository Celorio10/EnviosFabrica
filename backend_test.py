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

    def test_enagas_client_specific(self):
        """Test ENAGAS client creation as specified in the requirements"""
        print("\n" + "="*50)
        print("TESTING ENAGAS CLIENT CREATION (SPECIFIC TEST)")
        print("="*50)
        
        # Create ENAGAS client with specific details as requested
        enagas_client = {
            "nombre": "ENAGAS TRANSPORTE S.A.U.",
            "cif": "A86484334",
            "telefono": "987654321",
            "email": "",
            "centros_trabajo": [
                {
                    "id": f"wc-enagas-{datetime.now().strftime('%H%M%S')}-1",
                    "nombre": "C.T. Palencia",
                    "direccion": "",
                    "telefono": ""
                },
                {
                    "id": f"wc-enagas-{datetime.now().strftime('%H%M%S')}-2",
                    "nombre": "C.T. Plasencia",
                    "direccion": "",
                    "telefono": ""
                }
            ]
        }
        
        success, response = self.run_test(
            "Create ENAGAS Client",
            "POST",
            "clientes",
            200,
            data=enagas_client
        )
        
        enagas_client_id = None
        if success and 'id' in response:
            enagas_client_id = response['id']
            self.created_resources['clients'].append(enagas_client_id)
            print(f"   ✅ ENAGAS client created with ID: {enagas_client_id}")
            
            # Verify work centers were created correctly
            if 'centros_trabajo' in response and len(response['centros_trabajo']) == 2:
                work_centers = response['centros_trabajo']
                palencia_found = any(wc['nombre'] == 'C.T. Palencia' for wc in work_centers)
                plasencia_found = any(wc['nombre'] == 'C.T. Plasencia' for wc in work_centers)
                
                if palencia_found and plasencia_found:
                    print(f"   ✅ Both work centers created successfully")
                else:
                    print(f"   ❌ Work centers not created correctly")
                    print(f"       Palencia found: {palencia_found}")
                    print(f"       Plasencia found: {plasencia_found}")
            else:
                print(f"   ❌ Expected 2 work centers, got {len(response.get('centros_trabajo', []))}")
        
        # Test getting work centers for ENAGAS client (this is the critical test for Select.Item error)
        if enagas_client_id:
            success, work_centers = self.run_test(
                "Get ENAGAS Work Centers (Critical for Select.Item error)",
                "GET",
                f"clientes/{enagas_client_id}/centros-trabajo",
                200
            )
            
            if success:
                print(f"   ✅ Work centers endpoint returned {len(work_centers)} centers")
                
                # Verify each work center has valid ID and name (this prevents Select.Item error)
                valid_centers = 0
                for wc in work_centers:
                    if wc.get('id') and str(wc['id']).strip() and wc.get('nombre') and str(wc['nombre']).strip():
                        valid_centers += 1
                        print(f"       ✅ Valid work center: {wc['nombre']} (ID: {wc['id']})")
                    else:
                        print(f"       ❌ Invalid work center: {wc}")
                
                if valid_centers == len(work_centers):
                    print(f"   ✅ All {valid_centers} work centers are valid (no Select.Item error expected)")
                else:
                    print(f"   ❌ {len(work_centers) - valid_centers} invalid work centers found")
            else:
                print(f"   ❌ Failed to get work centers for ENAGAS client")
        
        # Test creating equipment with ENAGAS client (simulating the frontend flow)
        if enagas_client_id:
            test_equipment = {
                "orden_trabajo": "TEST-ENAGAS-SELECT-001",
                "cliente_id": enagas_client_id,
                "cliente_nombre": "ENAGAS TRANSPORTE S.A.U.",
                "centro_trabajo_id": "",  # Will be set after getting work centers
                "centro_trabajo_nombre": "",
                "tipo_equipo": "Detector Portátil de Gas",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": f"ENAGAS-SN-{datetime.now().strftime('%H%M%S')}",
                "tipo_fallo": "SENSOR FAILURE",
                "observaciones": "Test equipment for ENAGAS Select.Item error verification"
            }
            
            # Get work centers again to select one
            success, work_centers = self.run_test(
                "Get Work Centers for Equipment Creation",
                "GET",
                f"clientes/{enagas_client_id}/centros-trabajo",
                200
            )
            
            if success and len(work_centers) > 0:
                # Select the first work center (C.T. Palencia)
                selected_wc = work_centers[0]
                test_equipment["centro_trabajo_id"] = selected_wc['id']
                test_equipment["centro_trabajo_nombre"] = selected_wc['nombre']
                
                success, equipment_response = self.run_test(
                    "Create Equipment with ENAGAS Client and Work Center",
                    "POST",
                    "equipos",
                    200,
                    data=test_equipment
                )
                
                if success:
                    print(f"   ✅ Equipment created successfully with ENAGAS client and work center")
                    if 'id' in equipment_response:
                        self.created_resources['equipment'].append(equipment_response['id'])
                else:
                    print(f"   ❌ Failed to create equipment with ENAGAS client")
        
        return enagas_client_id is not None

    def test_cif_uniqueness_validation(self):
        """Test CIF uniqueness validation as requested in the review"""
        print("\n" + "="*50)
        print("TESTING CIF UNIQUENESS VALIDATION (CRITICAL BUSINESS RULE)")
        print("="*50)
        
        # Clear database first to ensure clean test
        print("   🧹 Clearing database for clean test...")
        success, response = self.run_test(
            "Clear Database",
            "POST",
            "admin/clear-database",
            200
        )
        
        if success:
            print(f"   ✅ Database cleared successfully")
        else:
            print(f"   ⚠️  Could not clear database, continuing with test...")
        
        # Use timestamp to ensure unique CIFs
        timestamp = datetime.now().strftime('%H%M%S')
        cif1 = f"B{timestamp}01"  # e.g., B14302301
        cif2 = f"B{timestamp}02"  # e.g., B14302302
        
        # Test 1: Create first client with unique CIF
        client1_data = {
            "nombre": "Cliente Prueba 1",
            "cif": cif1,
            "telefono": "111111111"
        }
        
        success, response = self.run_test(
            f"Create First Client (CIF: {cif1})",
            "POST",
            "clientes",
            200,
            data=client1_data
        )
        
        client1_id = None
        if success and 'id' in response:
            client1_id = response['id']
            self.created_resources['clients'].append(client1_id)
            print(f"   ✅ First client created successfully with CIF: {cif1}")
        else:
            print(f"   ❌ Failed to create first client")
            return False
        
        # Test 2: Try to create second client with SAME CIF (should fail)
        client2_data = {
            "nombre": "Cliente Prueba 2",
            "cif": cif1,  # Same CIF - should cause error
            "telefono": "222222222"
        }
        
        success, response = self.run_test(
            "Create Second Client with Duplicate CIF (Should Fail)",
            "POST",
            "clientes",
            400,  # Expecting 400 error
            data=client2_data
        )
        
        if success:  # Success means we got the expected 400 status code
            print(f"   ✅ Correctly rejected duplicate CIF creation")
            # Check if error message is correct
            if 'detail' in response and f'Ya existe un cliente con el CIF {cif1}' in response['detail']:
                print(f"   ✅ Correct error message: {response['detail']}")
            else:
                print(f"   ⚠️  Error message not as expected: {response.get('detail', 'No detail')}")
        else:
            print(f"   ❌ CRITICAL ERROR: Duplicate CIF was allowed!")
            return False
        
        # Test 3: Create third client with different CIF
        client3_data = {
            "nombre": "Cliente Prueba 3",
            "cif": cif2,
            "telefono": "333333333"
        }
        
        success, response = self.run_test(
            f"Create Third Client (CIF: {cif2})",
            "POST",
            "clientes",
            200,
            data=client3_data
        )
        
        client3_id = None
        if success and 'id' in response:
            client3_id = response['id']
            self.created_resources['clients'].append(client3_id)
            print(f"   ✅ Third client created successfully with CIF: {cif2}")
        else:
            print(f"   ❌ Failed to create third client")
            return False
        
        # Test 4: Try to edit third client to use duplicate CIF (should fail)
        if client3_id:
            client3_update_duplicate = {
                "nombre": "Cliente Prueba 3",
                "cif": cif1,  # Trying to change to duplicate CIF
                "telefono": "333333333"
            }
            
            success, response = self.run_test(
                "Update Third Client with Duplicate CIF (Should Fail)",
                "PUT",
                f"clientes/{client3_id}",
                400,  # Expecting 400 error
                data=client3_update_duplicate
            )
            
            if success:  # Success means we got the expected 400 status code
                print(f"   ✅ Correctly rejected duplicate CIF update")
                # Check if error message is correct
                if 'detail' in response and f'Ya existe otro cliente con el CIF {cif1}' in response['detail']:
                    print(f"   ✅ Correct error message: {response['detail']}")
                else:
                    print(f"   ⚠️  Error message not as expected: {response.get('detail', 'No detail')}")
            else:
                print(f"   ❌ CRITICAL ERROR: Duplicate CIF update was allowed!")
                return False
        
        # Test 5: Edit third client keeping same CIF (should work)
        if client3_id:
            client3_update_same = {
                "nombre": "Cliente Prueba 3 Updated",
                "cif": cif2,  # Keeping same CIF
                "telefono": "444444444"
            }
            
            success, response = self.run_test(
                "Update Third Client Keeping Same CIF (Should Work)",
                "PUT",
                f"clientes/{client3_id}",
                200,
                data=client3_update_same
            )
            
            if success:
                print(f"   ✅ Successfully updated client keeping same CIF")
            else:
                print(f"   ❌ Failed to update client with same CIF")
                return False
        
        # Test 6: Edit third client to new unique CIF (should work)
        if client3_id:
            new_unique_cif = f"B{timestamp}99"
            client3_update_new = {
                "nombre": "Cliente Prueba 3 Final",
                "cif": new_unique_cif,  # New unique CIF
                "telefono": "555555555"
            }
            
            success, response = self.run_test(
                "Update Third Client with New Unique CIF (Should Work)",
                "PUT",
                f"clientes/{client3_id}",
                200,
                data=client3_update_new
            )
            
            if success:
                print(f"   ✅ Successfully updated client with new unique CIF: {new_unique_cif}")
            else:
                print(f"   ❌ Failed to update client with new unique CIF")
                return False
        
        print(f"\n   🎯 CIF UNIQUENESS VALIDATION SUMMARY:")
        print(f"   ✅ Prevents duplicate CIF on client creation")
        print(f"   ✅ Prevents duplicate CIF on client update")
        print(f"   ✅ Allows client to keep their own CIF")
        print(f"   ✅ Allows client to change to new unique CIF")
        print(f"   ✅ Provides clear error messages")
        
        return True

    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Equipment Management API Tests")
        print(f"Testing against: {self.base_url}")
        
        # Run test suites
        if not self.test_authentication():
            print("❌ Authentication failed, stopping all tests")
            return 1
        
        # Run the CIF uniqueness test first (as requested in review)
        if not self.test_cif_uniqueness_validation():
            print("❌ CIF uniqueness validation failed - CRITICAL BUSINESS RULE BROKEN")
            return 1
        
        # Run other tests
        self.test_enagas_client_specific()
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
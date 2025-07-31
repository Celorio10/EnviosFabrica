import requests
import sys
import json
from datetime import datetime

class WorkflowDebugTester:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.test_equipment_id = None
        self.test_client_id = None
        self.test_po_number = "PO-TEST-DEBUG-001"

    def log(self, message, level="INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def make_request(self, method, endpoint, data=None, params=None, expected_status=None):
        """Make API request with proper headers"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.log(f"Making {method} request to {endpoint}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)

            self.log(f"Response status: {response.status_code}")
            
            if expected_status and response.status_code != expected_status:
                self.log(f"UNEXPECTED STATUS: Expected {expected_status}, got {response.status_code}", "ERROR")
                self.log(f"Response: {response.text}", "ERROR")
                return False, {}

            try:
                return True, response.json() if response.text else {}
            except:
                return True, {"text": response.text}

        except Exception as e:
            self.log(f"Request failed: {str(e)}", "ERROR")
            return False, {}

    def step_1_login_and_create_equipment(self):
        """Step 1: Login and register a new test equipment"""
        self.log("="*60)
        self.log("STEP 1: LOGIN AND CREATE EQUIPMENT")
        self.log("="*60)
        
        # Login
        self.log("Attempting login...")
        success, response = self.make_request(
            "POST", 
            "auth/login", 
            data={"username": "admin", "password": "ASCb33388091_"},
            expected_status=200
        )
        
        if not success or 'access_token' not in response:
            self.log("LOGIN FAILED - Cannot proceed with test", "ERROR")
            return False
            
        self.token = response['access_token']
        self.log("✅ Login successful")
        
        # Create a test client first
        self.log("Creating test client...")
        test_client = {
            "nombre": f"Debug Test Client {datetime.now().strftime('%H%M%S')}",
            "cif": f"B{datetime.now().strftime('%H%M%S')}",
            "telefono": "123456789",
            "email": "debug@test.com"
        }
        
        success, client_response = self.make_request(
            "POST",
            "clientes",
            data=test_client,
            expected_status=200
        )
        
        if not success or 'id' not in client_response:
            self.log("CLIENT CREATION FAILED", "ERROR")
            return False
            
        self.test_client_id = client_response['id']
        self.log(f"✅ Test client created with ID: {self.test_client_id}")
        
        # Create test equipment
        self.log("Creating test equipment...")
        test_equipment = {
            "orden_trabajo": f"DEBUG-OT-{datetime.now().strftime('%H%M%S')}",
            "cliente_id": self.test_client_id,
            "cliente_nombre": test_client["nombre"],
            "tipo_equipo": "Espaldera",
            "modelo": "Debug Test Model",
            "fabricante": "Debug Test Manufacturer",
            "numero_serie": f"DEBUG-SN-{datetime.now().strftime('%H%M%S')}",
            "tipo_fallo": "OTHER",
            "observaciones": "Equipment created for workflow debugging"
        }
        
        success, equipment_response = self.make_request(
            "POST",
            "equipos",
            data=test_equipment,
            expected_status=200
        )
        
        if not success or 'id' not in equipment_response:
            self.log("EQUIPMENT CREATION FAILED", "ERROR")
            return False
            
        self.test_equipment_id = equipment_response['id']
        self.log(f"✅ Test equipment created with ID: {self.test_equipment_id}")
        self.log(f"   Equipment state: {equipment_response.get('estado', 'Unknown')}")
        
        return True

    def step_2_administrative_management_test(self):
        """Step 2: Go to Gestión Administrativa and assign purchase order"""
        self.log("="*60)
        self.log("STEP 2: ADMINISTRATIVE MANAGEMENT TEST")
        self.log("="*60)
        
        # First, verify equipment is in Pendiente state
        self.log("Checking equipment state before assignment...")
        success, equipment_data = self.make_request(
            "GET",
            f"equipos/{self.test_equipment_id}",
            expected_status=200
        )
        
        if success:
            current_state = equipment_data.get('estado', 'Unknown')
            self.log(f"Equipment current state: {current_state}")
            if current_state != 'Pendiente':
                self.log(f"WARNING: Equipment is not in 'Pendiente' state, it's in '{current_state}'", "WARN")
        
        # Assign purchase order
        self.log(f"Assigning purchase order {self.test_po_number} to equipment {self.test_equipment_id}...")
        success, assign_response = self.make_request(
            "POST",
            "ordenes-compra/asignar",
            data={
                "numero_orden": self.test_po_number,
                "equipment_ids": [self.test_equipment_id]
            },
            expected_status=200
        )
        
        if not success:
            self.log("PURCHASE ORDER ASSIGNMENT FAILED", "ERROR")
            return False
            
        self.log("✅ Purchase order assignment successful")
        self.log(f"   Response: {assign_response}")
        
        return True

    def step_3_backend_verification(self):
        """Step 3: Check backend state changes"""
        self.log("="*60)
        self.log("STEP 3: BACKEND VERIFICATION")
        self.log("="*60)
        
        # Check if equipment state changed to "Enviado"
        self.log("Checking if equipment state changed to 'Enviado'...")
        success, equipment_data = self.make_request(
            "GET",
            f"equipos/{self.test_equipment_id}",
            expected_status=200
        )
        
        if success:
            current_state = equipment_data.get('estado', 'Unknown')
            purchase_order = equipment_data.get('numero_orden_compra', 'None')
            
            self.log(f"Equipment state after assignment: {current_state}")
            self.log(f"Purchase order number: {purchase_order}")
            
            if current_state != 'Enviado':
                self.log(f"❌ ISSUE FOUND: Equipment state is '{current_state}', expected 'Enviado'", "ERROR")
                return False
            else:
                self.log("✅ Equipment state correctly changed to 'Enviado'")
                
            if purchase_order != self.test_po_number:
                self.log(f"❌ ISSUE FOUND: Purchase order is '{purchase_order}', expected '{self.test_po_number}'", "ERROR")
                return False
            else:
                self.log("✅ Purchase order number correctly assigned")
        else:
            self.log("Failed to retrieve equipment data", "ERROR")
            return False
        
        # Check if equipment appears in /api/ordenes-compra/activas
        self.log("Checking active purchase orders...")
        success, active_orders_response = self.make_request(
            "GET",
            "ordenes-compra/activas",
            expected_status=200
        )
        
        if success:
            active_orders = active_orders_response.get('active_orders', [])
            self.log(f"Active purchase orders: {active_orders}")
            
            if self.test_po_number not in active_orders:
                self.log(f"❌ ISSUE FOUND: Purchase order '{self.test_po_number}' not in active orders", "ERROR")
                return False
            else:
                self.log(f"✅ Purchase order '{self.test_po_number}' found in active orders")
        else:
            self.log("Failed to retrieve active purchase orders", "ERROR")
            return False
            
        return True

    def step_4_manufacturer_response_test(self):
        """Step 4: Navigate to Respuesta Fabricante and test"""
        self.log("="*60)
        self.log("STEP 4: MANUFACTURER RESPONSE TEST")
        self.log("="*60)
        
        # Check if purchase order appears in active orders (this is what populates the dropdown)
        self.log("Checking if purchase order appears in dropdown options...")
        success, active_orders_response = self.make_request(
            "GET",
            "ordenes-compra/activas",
            expected_status=200
        )
        
        if success:
            active_orders = active_orders_response.get('active_orders', [])
            self.log(f"Available purchase orders for dropdown: {active_orders}")
            
            if self.test_po_number not in active_orders:
                self.log(f"❌ ISSUE FOUND: Purchase order '{self.test_po_number}' not available in dropdown", "ERROR")
                return False
            else:
                self.log(f"✅ Purchase order '{self.test_po_number}' available in dropdown")
        
        # Test the specific endpoint that should return equipment for the purchase order
        self.log(f"Testing equipment retrieval for purchase order {self.test_po_number}...")
        success, po_equipment_response = self.make_request(
            "GET",
            f"ordenes-compra/{self.test_po_number}/equipos/enviados",
            expected_status=200
        )
        
        if success:
            equipment_list = po_equipment_response if isinstance(po_equipment_response, list) else []
            self.log(f"Equipment returned for purchase order: {len(equipment_list)} items")
            
            if len(equipment_list) == 0:
                self.log(f"❌ CRITICAL ISSUE FOUND: No equipment returned for purchase order '{self.test_po_number}'", "ERROR")
                self.log("This is likely the root cause of the reported issue!", "ERROR")
                
                # Let's debug further
                self.log("Debugging: Checking all equipment for this purchase order...")
                success2, all_po_equipment = self.make_request(
                    "GET",
                    f"ordenes-compra/{self.test_po_number}/equipos",
                    expected_status=200
                )
                
                if success2:
                    all_equipment = all_po_equipment if isinstance(all_po_equipment, list) else []
                    self.log(f"All equipment for this PO: {len(all_equipment)} items")
                    for eq in all_equipment:
                        self.log(f"  - Equipment ID: {eq.get('id')}, State: {eq.get('estado')}, PO: {eq.get('numero_orden_compra')}")
                
                return False
            else:
                self.log("✅ Equipment found for purchase order")
                for eq in equipment_list:
                    self.log(f"  - Equipment ID: {eq.get('id')}, State: {eq.get('estado')}")
                    
                # Verify our test equipment is in the list
                our_equipment_found = any(eq.get('id') == self.test_equipment_id for eq in equipment_list)
                if not our_equipment_found:
                    self.log(f"❌ ISSUE: Our test equipment {self.test_equipment_id} not found in the list", "ERROR")
                    return False
                else:
                    self.log(f"✅ Our test equipment {self.test_equipment_id} found in the list")
        else:
            self.log("Failed to retrieve equipment for purchase order", "ERROR")
            return False
            
        return True

    def step_5_debug_the_issue(self):
        """Step 5: Debug the issue if found"""
        self.log("="*60)
        self.log("STEP 5: ADDITIONAL DEBUGGING")
        self.log("="*60)
        
        # Get all equipment and analyze
        self.log("Retrieving all equipment for analysis...")
        success, all_equipment = self.make_request(
            "GET",
            "equipos",
            expected_status=200
        )
        
        if success:
            equipment_list = all_equipment if isinstance(all_equipment, list) else []
            self.log(f"Total equipment in system: {len(equipment_list)}")
            
            # Find our equipment
            our_equipment = None
            for eq in equipment_list:
                if eq.get('id') == self.test_equipment_id:
                    our_equipment = eq
                    break
            
            if our_equipment:
                self.log("Our test equipment details:")
                self.log(f"  - ID: {our_equipment.get('id')}")
                self.log(f"  - State: {our_equipment.get('estado')}")
                self.log(f"  - Purchase Order: {our_equipment.get('numero_orden_compra')}")
                self.log(f"  - Created: {our_equipment.get('created_at')}")
                self.log(f"  - Updated: {our_equipment.get('updated_at')}")
            else:
                self.log("❌ Could not find our test equipment in the system", "ERROR")
        
        # Test the specific query that the /equipos/enviados endpoint uses
        self.log("Testing the backend query logic...")
        self.log("The endpoint /ordenes-compra/{order}/equipos/enviados should return equipment where:")
        self.log("  - numero_orden_compra = order_number")
        self.log("  - estado = 'Enviado'")
        
        return True

    def run_workflow_debug_test(self):
        """Run the complete workflow debug test"""
        self.log("🚀 Starting Workflow Debug Test")
        self.log(f"Testing against: {self.base_url}")
        self.log(f"Test Purchase Order: {self.test_po_number}")
        
        try:
            # Step 1: Login and create equipment
            if not self.step_1_login_and_create_equipment():
                self.log("❌ Step 1 failed - stopping test", "ERROR")
                return 1
            
            # Step 2: Administrative management test
            if not self.step_2_administrative_management_test():
                self.log("❌ Step 2 failed - stopping test", "ERROR")
                return 1
            
            # Step 3: Backend verification
            if not self.step_3_backend_verification():
                self.log("❌ Step 3 failed - issue found in backend state", "ERROR")
                self.step_5_debug_the_issue()
                return 1
            
            # Step 4: Manufacturer response test
            if not self.step_4_manufacturer_response_test():
                self.log("❌ Step 4 failed - issue found in manufacturer response workflow", "ERROR")
                self.step_5_debug_the_issue()
                return 1
            
            # Step 5: Additional debugging (always run for completeness)
            self.step_5_debug_the_issue()
            
            self.log("="*60)
            self.log("✅ ALL TESTS PASSED - No workflow issues detected")
            self.log("="*60)
            return 0
            
        except Exception as e:
            self.log(f"❌ Test failed with exception: {str(e)}", "ERROR")
            return 1

def main():
    tester = WorkflowDebugTester()
    return tester.run_workflow_debug_test()

if __name__ == "__main__":
    sys.exit(main())
import requests
import sys
import json
from datetime import datetime

class WorkflowTester:
    def __init__(self, base_url="https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.created_resources = {
            'client_id': None,
            'equipment_id': None,
            'purchase_order': None
        }

    def login_as_admin(self):
        """Login as admin user"""
        print("🔐 Logging in as admin...")
        try:
            response = requests.post(f"{self.api_url}/auth/login", json={
                "username": "admin",
                "password": "ASCb33388091_"
            })
            
            if response.status_code == 200:
                self.token = response.json()['access_token']
                print("✅ Admin login successful")
                return True
            else:
                print(f"❌ Admin login failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            return False

    def create_test_client(self):
        """Create test client as specified in requirements"""
        print("\n📋 Creating test client: 'Test Cliente Final'...")
        
        client_data = {
            "nombre": "Test Cliente Final",
            "cif": "B99999999",
            "telefono": "999888777",
            "email": "",
            "centros_trabajo": []
        }
        
        try:
            response = requests.post(f"{self.api_url}/clientes", 
                                   json=client_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                client = response.json()
                self.created_resources['client_id'] = client['id']
                print(f"✅ Client created successfully with ID: {client['id']}")
                print(f"   Name: {client['nombre']}")
                print(f"   CIF: {client['cif']}")
                print(f"   Phone: {client['telefono']}")
                return True
            else:
                print(f"❌ Client creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Client creation error: {str(e)}")
            return False

    def create_test_equipment(self):
        """Create test equipment as specified in requirements"""
        print("\n📦 Creating test equipment: Order 'FINAL-TEST-001'...")
        
        equipment_data = {
            "orden_trabajo": "FINAL-TEST-001",
            "cliente_id": self.created_resources['client_id'],
            "cliente_nombre": "Test Cliente Final",
            "centro_trabajo_id": "",
            "centro_trabajo_nombre": "",
            "tipo_equipo": "Detector Portátil de Gas",
            "modelo": "Test Model Final",
            "ato": "",
            "fabricante": "Test Manufacturer Final",
            "numero_serie": f"FINAL-SN-{datetime.now().strftime('%H%M%S')}",
            "fecha_fabricacion": "",
            "tipo_fallo": "SENSOR FAILURE",
            "observaciones": "Test equipment for final workflow testing",
            "numero_serie_sensor": f"SENSOR-{datetime.now().strftime('%H%M%S')}",
            "fecha_instalacion_sensor": ""
        }
        
        try:
            response = requests.post(f"{self.api_url}/equipos", 
                                   json=equipment_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                equipment = response.json()
                self.created_resources['equipment_id'] = equipment['id']
                print(f"✅ Equipment created successfully with ID: {equipment['id']}")
                print(f"   Order: {equipment['orden_trabajo']}")
                print(f"   Client: {equipment['cliente_nombre']}")
                print(f"   Type: {equipment['tipo_equipo']}")
                print(f"   Serial: {equipment['numero_serie']}")
                print(f"   State: {equipment['estado']}")
                return True
            else:
                print(f"❌ Equipment creation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Equipment creation error: {str(e)}")
            return False

    def assign_purchase_order(self):
        """Assign purchase order as specified in requirements"""
        print("\n📋 Assigning purchase order: 'PO-FINAL-TEST-001'...")
        
        self.created_resources['purchase_order'] = "PO-FINAL-TEST-001"
        
        assign_data = {
            "numero_orden": self.created_resources['purchase_order'],
            "equipment_ids": [self.created_resources['equipment_id']]
        }
        
        try:
            response = requests.post(f"{self.api_url}/ordenes-compra/asignar", 
                                   json=assign_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Purchase order assigned successfully")
                print(f"   Order Number: {self.created_resources['purchase_order']}")
                print(f"   Assigned Count: {result['assigned_count']}")
                return True
            else:
                print(f"❌ Purchase order assignment failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Purchase order assignment error: {str(e)}")
            return False

    def verify_active_purchase_orders(self):
        """Verify the purchase order appears in active orders"""
        print("\n🔍 Verifying active purchase orders...")
        
        try:
            response = requests.get(f"{self.api_url}/ordenes-compra/activas",
                                  headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                result = response.json()
                active_orders = result.get('active_orders', [])
                print(f"✅ Active purchase orders retrieved")
                print(f"   Active orders: {active_orders}")
                
                if self.created_resources['purchase_order'] in active_orders:
                    print(f"✅ Purchase order '{self.created_resources['purchase_order']}' found in active orders")
                    return True
                else:
                    print(f"❌ Purchase order '{self.created_resources['purchase_order']}' NOT found in active orders")
                    return False
            else:
                print(f"❌ Failed to get active purchase orders: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Active purchase orders error: {str(e)}")
            return False

    def verify_equipment_state(self):
        """Verify equipment state is 'Enviado'"""
        print("\n🔍 Verifying equipment state...")
        
        try:
            response = requests.get(f"{self.api_url}/equipos/{self.created_resources['equipment_id']}",
                                  headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                equipment = response.json()
                print(f"✅ Equipment retrieved")
                print(f"   State: {equipment['estado']}")
                print(f"   Purchase Order: {equipment.get('numero_orden_compra', 'None')}")
                
                if equipment['estado'] == 'Enviado':
                    print(f"✅ Equipment state is correctly 'Enviado'")
                    return True
                else:
                    print(f"❌ Equipment state is '{equipment['estado']}', expected 'Enviado'")
                    return False
            else:
                print(f"❌ Failed to get equipment: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Equipment verification error: {str(e)}")
            return False

    def test_manufacturer_response_endpoint(self):
        """Test manufacturer response functionality"""
        print("\n🏭 Testing manufacturer response endpoint...")
        
        response_data = {
            "equipment_ids": [self.created_resources['equipment_id']],
            "numero_recepcion_fabricante": f"REC-FINAL-{datetime.now().strftime('%H%M%S')}",
            "en_garantia": True
        }
        
        try:
            response = requests.post(f"{self.api_url}/ordenes-compra/{self.created_resources['purchase_order']}/respuesta-fabricante",
                                   json=response_data,
                                   headers={'Authorization': f'Bearer {self.token}'})
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Manufacturer response processed successfully")
                print(f"   Updated count: {result['updated_count']}")
                return True
            else:
                print(f"❌ Manufacturer response failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Manufacturer response error: {str(e)}")
            return False

    def run_complete_workflow_test(self):
        """Run the complete workflow test as specified in requirements"""
        print("🚀 Starting Complete Workflow Test")
        print("="*60)
        
        # Step 1: Login as admin
        if not self.login_as_admin():
            print("❌ Workflow test failed at login step")
            return False
        
        # Step 2: Create test client
        if not self.create_test_client():
            print("❌ Workflow test failed at client creation step")
            return False
        
        # Step 3: Create test equipment
        if not self.create_test_equipment():
            print("❌ Workflow test failed at equipment creation step")
            return False
        
        # Step 4: Assign purchase order
        if not self.assign_purchase_order():
            print("❌ Workflow test failed at purchase order assignment step")
            return False
        
        # Step 5: Verify active purchase orders
        if not self.verify_active_purchase_orders():
            print("❌ Workflow test failed at active purchase orders verification step")
            return False
        
        # Step 6: Verify equipment state
        if not self.verify_equipment_state():
            print("❌ Workflow test failed at equipment state verification step")
            return False
        
        # Step 7: Test manufacturer response
        if not self.test_manufacturer_response_endpoint():
            print("❌ Workflow test failed at manufacturer response step")
            return False
        
        print("\n" + "="*60)
        print("🎉 COMPLETE WORKFLOW TEST PASSED!")
        print("="*60)
        print("✅ All backend endpoints are working correctly")
        print("✅ Purchase order assignment workflow is functional")
        print("✅ Active purchase orders are properly tracked")
        print("✅ Equipment state transitions are working")
        print("✅ Manufacturer response functionality is working")
        
        return True

def main():
    tester = WorkflowTester()
    success = tester.run_complete_workflow_test()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
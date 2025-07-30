#!/usr/bin/env python3
"""
Specific test for equipment registration with date fields
Testing the fix for 422 errors when creating equipment with date fields
"""

import requests
import json
from datetime import datetime

BACKEND_URL = "https://fea6ae7e-0d8d-447f-8adc-aa2455539ce2.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

def login():
    """Login and get token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "username": "Marco",
        "password": "B33388091"
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Login failed: {response.text}")

def create_test_client(token):
    """Create a test client"""
    headers = {"Authorization": f"Bearer {token}"}
    client_data = {
        "nombre": "Test Client for Date Testing",
        "cif": "B99999999",
        "telefono": "123456789"
    }
    response = requests.post(f"{API_URL}/clientes", json=client_data, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Client creation failed: {response.text}")

def test_equipment_with_dates():
    """Test equipment creation with various date scenarios"""
    print("🧪 Testing Equipment Registration with Date Fields")
    print("=" * 60)
    
    token = login()
    print("✅ Login successful")
    
    client = create_test_client(token)
    print(f"✅ Test client created: {client['id']}")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test scenarios
    test_cases = [
        {
            "name": "Equipment with valid dates",
            "data": {
                "orden_trabajo": "TEST-001",
                "cliente_id": client["id"],
                "cliente_nombre": client["nombre"],
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": "SN-TEST-001",
                "fecha_fabricacion": "2024-01-15",
                "tipo_fallo": "OTHER",
                "observaciones": "Test with valid dates",
                "fecha_instalacion_sensor": "2024-02-01"
            }
        },
        {
            "name": "Equipment with empty date fields",
            "data": {
                "orden_trabajo": "TEST-002",
                "cliente_id": client["id"],
                "cliente_nombre": client["nombre"],
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": "SN-TEST-002",
                "fecha_fabricacion": "",
                "tipo_fallo": "OTHER",
                "observaciones": "Test with empty dates",
                "fecha_instalacion_sensor": ""
            }
        },
        {
            "name": "Equipment with null date fields",
            "data": {
                "orden_trabajo": "TEST-003",
                "cliente_id": client["id"],
                "cliente_nombre": client["nombre"],
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": "SN-TEST-003",
                "fecha_fabricacion": None,
                "tipo_fallo": "OTHER",
                "observaciones": "Test with null dates",
                "fecha_instalacion_sensor": None
            }
        },
        {
            "name": "Equipment without date fields",
            "data": {
                "orden_trabajo": "TEST-004",
                "cliente_id": client["id"],
                "cliente_nombre": client["nombre"],
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": "SN-TEST-004",
                "tipo_fallo": "OTHER",
                "observaciones": "Test without date fields"
            }
        },
        {
            "name": "Equipment with ISO datetime string",
            "data": {
                "orden_trabajo": "TEST-005",
                "cliente_id": client["id"],
                "cliente_nombre": client["nombre"],
                "tipo_equipo": "Espaldera",
                "modelo": "Test Model",
                "fabricante": "Test Manufacturer",
                "numero_serie": "SN-TEST-005",
                "fecha_fabricacion": "2024-01-15T10:30:00Z",
                "tipo_fallo": "OTHER",
                "observaciones": "Test with ISO datetime",
                "fecha_instalacion_sensor": "2024-02-01T14:45:00Z"
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['name']}")
        
        response = requests.post(f"{API_URL}/equipos", json=test_case["data"], headers=headers)
        
        if response.status_code == 200:
            print(f"✅ SUCCESS - Status: {response.status_code}")
            equipment = response.json()
            print(f"   Equipment ID: {equipment['id']}")
            print(f"   Fecha Fabricación: {equipment.get('fecha_fabricacion', 'None')}")
            print(f"   Fecha Instalación Sensor: {equipment.get('fecha_instalacion_sensor', 'None')}")
            results.append({"test": test_case["name"], "status": "PASS", "equipment_id": equipment["id"]})
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            results.append({"test": test_case["name"], "status": "FAIL", "error": response.text})
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    
    print(f"📊 Tests passed: {passed}/{total}")
    print(f"📈 Success rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All date field tests PASSED! The 422 error fix is working correctly.")
    else:
        print("⚠️  Some tests failed. The date field handling may still have issues.")
        
    for result in results:
        status_icon = "✅" if result["status"] == "PASS" else "❌"
        print(f"{status_icon} {result['test']}")
        if result["status"] == "FAIL":
            print(f"    Error: {result.get('error', 'Unknown error')}")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = test_equipment_with_dates()
        exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        exit(1)
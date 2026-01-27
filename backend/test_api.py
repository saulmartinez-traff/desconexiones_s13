"""
API Testing Script - Desconexiones S13
Tests endpoints with actual HTTP requests
"""

import requests
import json
from datetime import datetime

class S13APITester:
    """Test suite for S13 Desconexiones API"""
    
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url
        self.token = None
        self.headers = {
            'Content-Type': 'application/json'
        }
    
    def login(self, username="admin", password="admin123"):
        """Authenticate and get JWT token"""
        url = f"{self.base_url}/auth/token/"
        
        try:
            response = requests.post(url, json={
                "username": username,
                "password": password
            })
            
            if response.status_code == 200:
                data = response.json()
                self.token = data['access']
                self.headers['Authorization'] = f"Bearer {self.token}"
                print(f"✅ Login successful - Token: {self.token[:50]}...")
                return True
            else:
                print(f"❌ Login failed: {response.status_code}")
                print(response.text)
                return False
        
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure Django server is running.")
            return False
    
    def test_organization_endpoints(self):
        """Test Organization endpoints"""
        print("\n" + "="*50)
        print("🧪 TESTING ORGANIZATION ENDPOINTS")
        print("="*50)
        
        # Test 1: Get my profile
        print("\n1️⃣  GET /organization/users/me/")
        response = requests.get(
            f"{self.base_url}/v1/organization/users/me/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"✅ User: {response.json()['username']}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: List distribuidores
        print("\n2️⃣  GET /organization/distribuidores/")
        response = requests.get(
            f"{self.base_url}/v1/organization/distribuidores/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('results', data))} distribuidores")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: List groups
        print("\n3️⃣  GET /organization/groups/")
        response = requests.get(
            f"{self.base_url}/v1/organization/groups/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            groups = data.get('results', data)
            print(f"✅ Found {len(groups)} groups")
        else:
            print(f"❌ Error: {response.text}")
    
    def test_vehicle_endpoints(self):
        """Test Vehicle endpoints"""
        print("\n" + "="*50)
        print("🚗 TESTING VEHICLE ENDPOINTS")
        print("="*50)
        
        # Test 1: List vehicles
        print("\n1️⃣  GET /vehicles/vehicles/")
        response = requests.get(
            f"{self.base_url}/v1/vehicles/vehicles/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            vehicles = data.get('results', data)
            print(f"✅ Found {len(vehicles)} vehicles")
            
            # Test vehicle detail if available
            if vehicles:
                vehicle_id = vehicles[0]['id']
                print(f"\n2️⃣  GET /vehicles/vehicles/{vehicle_id}/")
                response = requests.get(
                    f"{self.base_url}/v1/vehicles/vehicles/{vehicle_id}/",
                    headers=self.headers
                )
                print(f"Status: {response.status_code}")
                if response.status_code == 200:
                    vehicle = response.json()
                    print(f"✅ Vehicle: {vehicle.get('vin', 'N/A')}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: List geofences
        print("\n3️⃣  GET /vehicles/geofences/")
        response = requests.get(
            f"{self.base_url}/v1/vehicles/geofences/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            geofences = data.get('results', data)
            print(f"✅ Found {len(geofences)} geofences")
        else:
            print(f"❌ Error: {response.text}")
    
    def test_register_endpoints(self):
        """Test Register endpoints"""
        print("\n" + "="*50)
        print("📋 TESTING REGISTER ENDPOINTS")
        print("="*50)
        
        # Test 1: List registers
        print("\n1️⃣  GET /registers/registers/")
        response = requests.get(
            f"{self.base_url}/v1/registers/registers/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            registers = data.get('results', data)
            print(f"✅ Found {len(registers)} registers")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: Get register by status
        print("\n2️⃣  GET /registers/registers/by_status/")
        response = requests.get(
            f"{self.base_url}/v1/registers/registers/by_status/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            status_counts = response.json()
            print(f"✅ Status counts: {status_counts}")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 3: Get editable registers
        print("\n3️⃣  GET /registers/registers/editable/")
        response = requests.get(
            f"{self.base_url}/v1/registers/registers/editable/",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {len(data.get('results', data))} editable registers")
        else:
            print(f"❌ Error: {response.text}")
    
    def test_filter_endpoints(self):
        """Test filtering and search"""
        print("\n" + "="*50)
        print("🔍 TESTING FILTERS & SEARCH")
        print("="*50)
        
        # Test 1: Filter vehicles by is_connected
        print("\n1️⃣  GET /vehicles/vehicles/?is_connected=true")
        response = requests.get(
            f"{self.base_url}/v1/vehicles/vehicles/?is_connected=true",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            vehicles = data.get('results', data)
            print(f"✅ Found {len(vehicles)} connected vehicles")
        else:
            print(f"❌ Error: {response.text}")
        
        # Test 2: Search registers
        print("\n2️⃣  GET /registers/registers/?search=KL5")
        response = requests.get(
            f"{self.base_url}/v1/registers/registers/?search=KL5",
            headers=self.headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            registers = data.get('results', data)
            print(f"✅ Found {len(registers)} registers matching search")
        else:
            print(f"❌ Error: {response.text}")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n🚀 STARTING S13 API TEST SUITE")
        print(f"Base URL: {self.base_url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        
        # Login first
        if not self.login():
            print("\n❌ Cannot proceed without authentication")
            return
        
        # Run tests
        self.test_organization_endpoints()
        self.test_vehicle_endpoints()
        self.test_register_endpoints()
        self.test_filter_endpoints()
        
        print("\n" + "="*50)
        print("✅ TEST SUITE COMPLETED")
        print("="*50)


if __name__ == "__main__":
    # Create tester instance
    tester = S13APITester(base_url="http://localhost:8000/api")
    
    # Run all tests
    tester.run_all_tests()

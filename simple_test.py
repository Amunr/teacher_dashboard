#!/usr/bin/env python3
"""
Simple test script for maintenance page fixes
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_endpoints():
    """Test the maintenance page API endpoints"""
    
    print("Testing maintenance page fixes...")
    print("=" * 50)
    
    try:
        # Test 1: Check config status endpoint
        print("1. Testing config status...")
        response = requests.get(f"{BASE_URL}/api/sheets/config/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Config status: {data}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    
        # Test 2: Test connection endpoint
        print("\n2. Testing connection...")
        response = requests.get(f"{BASE_URL}/api/sheets/test-connection")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Test connection: {data}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    
        # Test 3: Check service status
        print("\n3. Testing service status...")
        response = requests.get(f"{BASE_URL}/api/sheets/service/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Service status: {data}")
        else:
            print(f"   ✗ Failed: {response.status_code}")
    
        # Test 4: Test set last row endpoint
        print("\n4. Testing set last row...")
        test_data = {"last_row": 5}
        response = requests.post(f"{BASE_URL}/api/sheets/config/last-row", 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Set last row: {data}")
        else:
            print(f"   ✗ Failed: {response.status_code} - {response.text}")
    
        print("\n" + "=" * 50)
        print("Test completed! Check the maintenance page at:")
        print(f"{BASE_URL}/maintenance")
        
    except requests.exceptions.ConnectionError:
        print("✗ Failed to connect to Flask app. Make sure it's running on port 5000.")
    except Exception as e:
        print(f"✗ Error during testing: {e}")

if __name__ == "__main__":
    test_endpoints()

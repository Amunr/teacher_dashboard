import requests
import subprocess
import sys

def quick_test():
    base_url = "http://localhost:5000"
    
    print("🔧 QUICK MAINTENANCE TEST")
    print("Testing individual endpoints...")
    
    # Test 1: Config status
    try:
        print("\n1. Config Status:")
        response = requests.get(f"{base_url}/api/sheets/config/status", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Configured: {data.get('configured', 'Unknown')}")
            print(f"   Active: {data.get('active', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Service status
    try:
        print("\n2. Service Status:")
        response = requests.get(f"{base_url}/api/sheets/service/status", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Running: {data.get('running', 'Unknown')}")
            print(f"   Count: {data.get('count', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Test connection
    try:
        print("\n3. Test Connection:")
        response = requests.get(f"{base_url}/api/sheets/test-connection", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: {data.get('success', 'Unknown')}")
            print(f"   Total rows: {data.get('total_rows', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Database check
    try:
        print("\n4. Database Check:")
        import sqlite3
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM responses")
        count = cursor.fetchone()[0]
        print(f"   Responses in DB: {count}")
        conn.close()
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    quick_test()

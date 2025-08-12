#!/usr/bin/env python3
"""
Comprehensive test script with timeouts for maintenance page issues
"""
import requests
import json
import time
import sys
import subprocess

BASE_URL = "http://localhost:5000"

def test_with_timeout(test_name, test_func, timeout_seconds=120):
    """Run a test function with timeout"""
    print(f"\n{'=' * 50}")
    print(f"Testing: {test_name}")
    print(f"{'=' * 50}")
    
    try:
        start_time = time.time()
        result = test_func()
        elapsed = time.time() - start_time
        if elapsed > timeout_seconds:
            print(f"⚠️  Test took {elapsed:.1f}s (may be slow)")
        return result
    except Exception as e:
        print(f"❌ Test '{test_name}' failed: {e}")
        return False

def test_config_status():
    """Test 1: Check if config status endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/api/sheets/config/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Config status endpoint works")
            print(f"   Response: {data}")
            return data.get('configured', False)
        else:
            print(f"❌ Config status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Config status error: {e}")
        return False

def test_service_endpoints():
    """Test 2: Check service control endpoints"""
    tests = [
        ('/api/sheets/service/status', 'GET', 'Service Status'),
        ('/api/sheets/service/start', 'POST', 'Service Start'),
        ('/api/sheets/service/stop', 'POST', 'Service Stop'),
    ]
    
    results = {}
    for endpoint, method, name in tests:
        try:
            if method == 'GET':
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name} endpoint works")
                print(f"   Response: {data}")
                results[name] = True
            else:
                print(f"❌ {name} failed: {response.status_code}")
                results[name] = False
        except Exception as e:
            print(f"❌ {name} error: {e}")
            results[name] = False
    
    return all(results.values())

def test_test_connection():
    """Test 3: Check test connection endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/sheets/test-connection", timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Test connection works")
            print(f"   Response: {data}")
            return data.get('success', False)
        else:
            print(f"❌ Test connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Test connection error: {e}")
        return False

def test_set_last_row():
    """Test 4: Check set last row endpoint"""
    try:
        test_data = {"last_row": 2}
        response = requests.post(
            f"{BASE_URL}/api/sheets/config/last-row", 
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Set last row works")
            print(f"   Response: {data}")
            return data.get('success', False)
        else:
            print(f"❌ Set last row failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Set last row error: {e}")
        return False

def test_sheets_poller_manual():
    """Test 5: Run sheets poller manually to check data insertion"""
    try:
        print("🔄 Running sheets poller with 2-minute timeout...")
        result = subprocess.run(
            ['python', 'sheets_poller.py', '--mode', 'once'],
            capture_output=True,
            text=True,
            timeout=120  # 2-minute timeout
        )
        
        print(f"✅ Sheets poller executed")
        print(f"   Exit code: {result.returncode}")
        if result.stdout:
            print(f"   Output: {result.stdout}")
        if result.stderr:
            print(f"   Errors: {result.stderr}")
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"❌ Sheets poller timed out after 2 minutes")
        return False
    except Exception as e:
        print(f"❌ Sheets poller error: {e}")
        return False

def check_database_responses():
    """Test 6: Check if responses were actually inserted into database"""
    try:
        import sqlite3
        
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Check responses count
        cursor.execute("SELECT COUNT(*) FROM responses")
        count = cursor.fetchone()[0]
        
        print(f"✅ Database accessible")
        print(f"   Responses in database: {count}")
        
        if count > 0:
            # Get sample response
            cursor.execute("SELECT * FROM responses LIMIT 1")
            sample = cursor.fetchone()
            print(f"   Sample response: {sample}")
        
        conn.close()
        return count > 0
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return False

def main():
    """Run all tests with timeouts"""
    print("🔧 COMPREHENSIVE MAINTENANCE TEST SUITE")
    print("Each test has a 2-minute timeout")
    
    # Wait a moment for Flask app to be ready
    print("\n⏳ Waiting for Flask app to be ready...")
    time.sleep(3)
    
    test_results = {}
    
    # Test 1: Config Status
    test_results['Config Status'] = test_with_timeout(
        "Config Status Endpoint", 
        test_config_status
    )
    
    # Test 2: Service Endpoints
    test_results['Service Endpoints'] = test_with_timeout(
        "Service Control Endpoints", 
        test_service_endpoints
    )
    
    # Test 3: Test Connection
    test_results['Test Connection'] = test_with_timeout(
        "Test Connection Endpoint", 
        test_test_connection
    )
    
    # Test 4: Set Last Row
    test_results['Set Last Row'] = test_with_timeout(
        "Set Last Row Endpoint", 
        test_set_last_row
    )
    
    # Test 5: Manual Poller
    test_results['Manual Poller'] = test_with_timeout(
        "Manual Sheets Poller", 
        test_sheets_poller_manual
    )
    
    # Test 6: Database Check
    test_results['Database Check'] = test_with_timeout(
        "Database Response Check", 
        check_database_responses
    )
    
    # Summary
    print(f"\n{'=' * 60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'=' * 60}")
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests PASSED!")
    else:
        print("⚠️  Some tests FAILED - check individual results above")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")
        sys.exit(1)

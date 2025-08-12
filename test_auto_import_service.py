#!/usr/bin/env python3
"""
Test the fixed auto import service
"""

import requests
import time
import json

def test_service_management():
    """Test starting, checking status, and stopping the service"""
    
    base_url = "http://localhost:5000/api/sheets"
    
    print("=== TESTING AUTO IMPORT SERVICE FIXES ===")
    
    # 1. Check initial status
    print("\n1. Checking initial service status...")
    try:
        response = requests.get(f"{base_url}/service/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   Initial status: {data}")
        else:
            print(f"   Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   Status check error: {e}")
    
    # 2. Start the service
    print("\n2. Starting the auto import service...")
    try:
        response = requests.post(f"{base_url}/service/start")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Service started: {data['message']}")
            print(f"   PID: {data.get('pid')}")
            print(f"   Poll interval: {data.get('poll_interval')} minutes")
        else:
            print(f"   ❌ Failed to start service: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Start service error: {e}")
    
    # 3. Wait a moment and check detailed status
    print("\n3. Waiting 10 seconds then checking detailed status...")
    time.sleep(10)
    
    try:
        response = requests.get(f"{base_url}/service/detailed-status")
        if response.status_code == 200:
            data = response.json()
            print(f"   Service running: {data.get('process_running')}")
            print(f"   Status message: {data.get('status_message')}")
            print(f"   Minutes until next run: {data.get('minutes_until_next_run')}")
            print(f"   Next run time: {data.get('next_run_time')}")
            
            if data.get('status_data'):
                status = data['status_data']
                print(f"   Cycle count: {status.get('cycle_count', 0)}")
                print(f"   Last poll result: {status.get('last_poll_result', {}).get('status', 'unknown')}")
        else:
            print(f"   Detailed status check failed: {response.status_code}")
    except Exception as e:
        print(f"   Detailed status error: {e}")
    
    # 4. Check config status
    print("\n4. Checking config status...")
    try:
        response = requests.get(f"{base_url}/config/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   Configured: {data.get('configured')}")
            print(f"   Active: {data.get('active')}")
            print(f"   Poll interval: {data.get('poll_interval')} minutes")
        else:
            print(f"   Config status check failed: {response.status_code}")
    except Exception as e:
        print(f"   Config status error: {e}")
    
    # 5. Wait for first poll cycle to complete (2+ minutes)
    print(f"\n5. Waiting 3 minutes to see if auto polling works...")
    print("   (This will test if the 2-minute timer actually works)")
    
    for i in range(18):  # 18 * 10 seconds = 3 minutes
        time.sleep(10)
        
        # Check status every 30 seconds
        if i % 3 == 0:
            try:
                response = requests.get(f"{base_url}/service/detailed-status")
                if response.status_code == 200:
                    data = response.json()
                    minutes_left = data.get('minutes_until_next_run', 'unknown')
                    cycle_count = data.get('status_data', {}).get('cycle_count', 0)
                    print(f"   └─ {i*10//60}:{(i*10)%60:02d} - Next run in {minutes_left} min, Cycles: {cycle_count}")
            except:
                pass
    
    # 6. Final status check
    print("\n6. Final status check...")
    try:
        response = requests.get(f"{base_url}/service/detailed-status")
        if response.status_code == 200:
            data = response.json()
            cycle_count = data.get('status_data', {}).get('cycle_count', 0)
            if cycle_count > 0:
                print(f"   ✅ SUCCESS: Auto polling worked! Completed {cycle_count} cycles")
            else:
                print(f"   ❌ ISSUE: No polling cycles completed after 3 minutes")
            
            print(f"   Final status: {data.get('status_message')}")
        else:
            print(f"   Final status check failed: {response.status_code}")
    except Exception as e:
        print(f"   Final status error: {e}")
    
    # 7. Stop the service
    print("\n7. Stopping the service...")
    try:
        response = requests.post(f"{base_url}/service/stop")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Service stopped: {data['message']}")
        else:
            print(f"   ❌ Failed to stop service: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stop service error: {e}")

if __name__ == "__main__":
    print("Make sure the Flask app is running on localhost:5000")
    print("Testing auto import service fixes...")
    
    test_service_management()

#!/usr/bin/env python3
"""
Test what the maintenance API returns to debug the UI issues
"""
import requests
import json

print("Testing maintenance API data...")

try:
    # Test the maintenance page data
    response = requests.get('http://localhost:5000/maintenance', timeout=10)
    print(f"Maintenance page status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Maintenance page loads successfully")
        # Check if it contains recent data
        if 'res-id 513' in response.text or 'res-id 514' in response.text:
            print("✅ Recent manual import data found in maintenance page")
        else:
            print("❌ Recent manual import data NOT found in maintenance page")
    else:
        print(f"❌ Maintenance page failed: {response.status_code}")
        print(response.text[:500])

except Exception as e:
    print(f"❌ Error testing maintenance: {e}")

print("Test completed.")

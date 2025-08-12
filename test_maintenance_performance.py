#!/usr/bin/env python3
"""
Test the optimized maintenance page performance
"""
import requests
import time

print("Testing optimized maintenance page performance...")

try:
    start_time = time.time()
    
    # Test the maintenance page 
    response = requests.get('http://localhost:5000/maintenance', timeout=30)
    
    end_time = time.time()
    load_time = end_time - start_time
    
    print(f"✅ Maintenance page loaded in {load_time:.2f} seconds")
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        # Check if recent data is visible
        content = response.text
        
        # Look for recent res-ids
        recent_indicators = ['513', '514', 'Shaziya Banu', 'GHPS D K Bagilu', 'Junaid', 'Pallavi']
        found_indicators = [indicator for indicator in recent_indicators if indicator in content]
        
        print(f"Recent data indicators found: {len(found_indicators)}/{len(recent_indicators)}")
        for indicator in found_indicators:
            print(f"  ✅ Found: {indicator}")
        
        if len(found_indicators) >= 3:
            print("✅ Recent manual import data appears to be visible in maintenance page")
        else:
            print("❌ Recent manual import data may not be visible")
    
except Exception as e:
    print(f"❌ Error testing maintenance page: {e}")

print("Performance test completed.")

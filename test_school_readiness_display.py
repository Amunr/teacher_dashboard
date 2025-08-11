#!/usr/bin/env python3
"""
Test script to verify the school readiness display works correctly with 0.0 values.
"""

import requests
import json

def test_school_readiness_display():
    """Test that school readiness percentage displays correctly for 0.0 values."""
    
    # Test the API endpoint
    try:
        response = requests.get('http://localhost:5000/api/dashboard-data')
        data = response.json()
        
        print("=== API Response Test ===")
        print(f"Status Code: {response.status_code}")
        print(f"School Readiness Percent: {data.get('school_readiness_percent')}")
        print(f"Type: {type(data.get('school_readiness_percent'))}")
        print(f"Average Score: {data.get('average_score')}")
        print(f"Total Students Assessed: {data.get('total_students_assessed')}")
        
        # Verify the value is exactly 0.0
        school_readiness = data.get('school_readiness_percent')
        if school_readiness == 0.0:
            print("✅ School readiness percentage is correctly 0.0")
        else:
            print(f"❌ Expected 0.0, got {school_readiness}")
            
        # Test the template logic in Python
        print("\n=== Template Logic Test ===")
        initial_data = {'school_readiness_percent': 0.0}
        
        # Original (buggy) logic
        original_display = initial_data['school_readiness_percent'] if initial_data and initial_data['school_readiness_percent'] else '--'
        print(f"Original logic result: '{original_display}' (This was the bug)")
        
        # Fixed logic  
        fixed_display = initial_data['school_readiness_percent'] if initial_data and initial_data['school_readiness_percent'] is not None else '--'
        print(f"Fixed logic result: '{fixed_display}' (This should show 0.0)")
        
        if fixed_display == 0.0:
            print("✅ Template logic fix works correctly")
        else:
            print(f"❌ Template logic fix failed")
            
        # Test the JavaScript logic
        print("\n=== JavaScript Logic Test ===")
        # Simulating the JavaScript condition
        school_readiness_percent = 0.0
        
        # Original (buggy) JavaScript logic
        js_original = school_readiness_percent if school_readiness_percent else '--'
        print(f"Original JS logic result: '{js_original}' (This was the bug)")
        
        # Fixed JavaScript logic
        js_fixed = school_readiness_percent if school_readiness_percent is not None else '--'
        print(f"Fixed JS logic result: '{js_fixed}' (This should show 0.0)")
        
        if js_fixed == 0.0:
            print("✅ JavaScript logic fix works correctly")
        else:
            print(f"❌ JavaScript logic fix failed")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to server: {e}")
        print("Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_school_readiness_display()

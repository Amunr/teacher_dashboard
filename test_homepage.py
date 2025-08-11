#!/usr/bin/env python3
"""
Test script to check if the homepage renders with server-side data
"""

import requests
from bs4 import BeautifulSoup

def test_homepage():
    """Test the homepage to see if it has server-side data"""
    try:
        # Make request to the homepage
        response = requests.get('http://127.0.0.1:5000')
        if response.status_code == 200:
            print("✅ Homepage loads successfully")
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for specific data elements
            readiness = soup.find(id='readinessPercentage')
            total_students = soup.find(id='totalStudents')
            avg_score = soup.find(id='classAvgScore')
            
            print(f"📊 School Readiness: {readiness.text if readiness else 'Not found'}")
            print(f"👥 Total Students: {total_students.text if total_students else 'Not found'}")
            print(f"📈 Average Score: {avg_score.text if avg_score else 'Not found'}")
            
            # Check if JavaScript notice is present
            js_notice = soup.find(id='jsNotice')
            if js_notice:
                print("ℹ️  JavaScript notice is present (good for fallback)")
            
            # Look for any error messages
            alerts = soup.find_all(class_='alert-danger')
            if alerts:
                print("❌ Error alerts found:")
                for alert in alerts:
                    print(f"   {alert.get_text(strip=True)}")
            else:
                print("✅ No error alerts found")
                
        else:
            print(f"❌ Homepage request failed: {response.status_code}")
            print(response.text[:500])
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is it running on http://127.0.0.1:5000?")
    except Exception as e:
        print(f"❌ Error testing homepage: {e}")

if __name__ == "__main__":
    test_homepage()

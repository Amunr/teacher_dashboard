#!/usr/bin/env python3
"""
Debug what's actually in the Google Sheets CSV
"""
import csv
import requests
import sys
from datetime import datetime
from io import StringIO

timeout_seconds = 30
start_time = datetime.now()

def check_timeout():
    elapsed = (datetime.now() - start_time).total_seconds()
    if elapsed > timeout_seconds:
        print(f'Timeout after {elapsed:.1f} seconds')
        sys.exit(1)
    return elapsed

try:
    check_timeout()
    
    # The same URL from sheets_config
    sheet_url = "https://docs.google.com/spreadsheets/d/1d0SSQbJuu2S4FZfR4184aLn3dK4m7EVEEW0DeKZrCSw/edit?gid=1095086620#gid=1095086620"
    
    # Convert to CSV export URL
    if "/edit" in sheet_url:
        csv_url = sheet_url.replace("/edit", "/export").split("#")[0] + "&format=csv"
    else:
        csv_url = sheet_url + "&format=csv"
    
    print(f"Fetching CSV from: {csv_url}")
    
    check_timeout()
    response = requests.get(csv_url, timeout=20)
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch CSV: HTTP {response.status_code}")
        print(f"Response content: {response.text[:500]}")
        sys.exit(1)
    
    # Parse CSV with large field size limit
    csv.field_size_limit(1000000)
    csv_content = StringIO(response.text)
    reader = csv.reader(csv_content)
    
    print(f"\n=== FIRST 5 ROWS OF CSV DATA ===")
    
    for row_num, row in enumerate(reader, 1):
        check_timeout()
        
        if row_num <= 5:
            print(f"\nRow {row_num} ({len(row)} columns):")
            for col_num, cell in enumerate(row[:10]):  # Show first 10 columns
                content = str(cell)[:100]  # Truncate long content
                print(f"  Col {col_num+1}: '{content}{'...' if len(str(cell)) > 100 else ''}'")
        
        if row_num > 10:  # Just process first 10 rows
            break
    
    elapsed = check_timeout()
    print(f'\nCSV inspection completed in {elapsed:.1f} seconds')
    
except Exception as e:
    elapsed = (datetime.now() - start_time).total_seconds()
    print(f'Error after {elapsed:.1f} seconds: {e}')
    sys.exit(1)

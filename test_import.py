#!/usr/bin/env python3
"""Test the fixed import functionality"""

import sys
import os
sys.path.append('.')

from app.models.database import DatabaseManager, SheetsImportService

def test_import():
    """Test importing data with the fixed CSV URL conversion"""
    try:
        print("🧪 Testing import with fixed CSV URL conversion...")
        
        # Initialize database and import service
        db_manager = DatabaseManager('sqlite:///data.db')
        db_manager.initialize_database()  # This is the missing initialization!
        import_service = SheetsImportService(db_manager)
        
        # Test sheet URL
        sheet_url = 'https://docs.google.com/spreadsheets/d/1d0SSQbJuu2S4FZfR4184aLn3dK4m7EVEEW0DeKZrCSw/edit?gid=1095086620#gid=1095086620'
        
        print(f"📋 Sheet URL: {sheet_url}")
        
        # Test CSV conversion
        csv_url = import_service.convert_sheets_url_to_csv(sheet_url)
        print(f"🔗 CSV URL: {csv_url}")
        
        # Test import
        result = import_service.fetch_and_process_new_rows(sheet_url, 0)
        print(f"📊 Import result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_import()

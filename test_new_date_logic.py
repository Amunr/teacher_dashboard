#!/usr/bin/env python3
"""
Test the new date logic that uses Column A as timestamp
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.database import DatabaseManager, SheetsImportService
from config.config import Config
from datetime import datetime, date

def test_new_date_logic():
    print("Testing new date logic with Column A as timestamp...")
    
    # Initialize database
    db_manager = DatabaseManager(Config.DATABASE_URL)
    db_manager.initialize_database()
    
    # Initialize import service
    import_service = SheetsImportService(db_manager)
    
    # Test row data simulating Google Sheets CSV
    # Column A = timestamp, other columns = various data
    test_row = [
        "7/1/2025 10:15:12",  # Column A: Form timestamp (DD/MM/YYYY HH:MM:SS)
        "",                    # Column B: Empty
        "John Teacher",        # Column C: Teacher name
        "Test School",         # Column D: School
        "Jane Student",        # Column E: Student name
        "",                    # Column F: Empty
        "31/1/2019",          # Column G: Student birthday (DD/MM/YYYY)
        "1",                   # Column H: Some response
        "0.5",                 # Column I: Another response
        "achieved"             # Column J: Text response
    ]
    
    print(f"Test row data: {test_row}")
    
    try:
        # Process the row
        res_id = import_service.process_sheet_row(test_row, 2)  # Row 2 (after header)
        print(f"✅ Successfully processed row, res_id: {res_id}")
        
        # Verify the data was inserted correctly
        with db_manager.get_connection() as conn:
            from sqlalchemy import text
            query = text("SELECT * FROM responses WHERE [res-id] = :res_id")
            results = conn.execute(query, {"res_id": res_id}).fetchall()
            
            print(f"\n📊 Inserted {len(results)} response records:")
            for row in results:
                print(f"  Index_ID: {row[7]}, Response: {row[8]}, Date: {row[6]}")
                print(f"  School: {row[1]}, Teacher: {row[3]}, Student: {row[5]}")
            
    except Exception as e:
        print(f"❌ Error processing row: {e}")
        return False
    
    return True

def test_invalid_timestamp():
    print("\nTesting invalid timestamp handling...")
    
    # Initialize database
    db_manager = DatabaseManager(Config.DATABASE_URL)
    db_manager.initialize_database()
    
    # Initialize import service
    import_service = SheetsImportService(db_manager)
    
    # Test row with invalid timestamp
    test_row = [
        "invalid_date",        # Column A: Invalid timestamp
        "",                    # Column B: Empty
        "John Teacher",        # Column C: Teacher name
        "Test School",         # Column D: School
        "Jane Student",        # Column E: Student name
    ]
    
    print(f"Test row with invalid timestamp: {test_row}")
    
    try:
        # This should fail
        res_id = import_service.process_sheet_row(test_row, 3)
        print(f"❌ Unexpected success - should have failed!")
        return False
        
    except ValueError as e:
        print(f"✅ Correctly rejected invalid timestamp: {e}")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_no_valid_layout():
    print("\nTesting rejection when no valid layout exists for date...")
    
    # Initialize database
    db_manager = DatabaseManager(Config.DATABASE_URL)
    db_manager.initialize_database()
    
    # Initialize import service
    import_service = SheetsImportService(db_manager)
    
    # Test row with timestamp far in the future (no layout should exist)
    test_row = [
        "1/1/2030 10:15:12",   # Column A: Future timestamp
        "",                    # Column B: Empty
        "John Teacher",        # Column C: Teacher name
        "Test School",         # Column D: School
        "Jane Student",        # Column E: Student name
        "",                    # Column F: Empty
        "31/1/2019",          # Column G: Student birthday
        "1",                   # Column H: Some response
    ]
    
    print(f"Test row with future timestamp: {test_row}")
    
    try:
        # This should fail due to no valid layout
        res_id = import_service.process_sheet_row(test_row, 4)
        print(f"❌ Unexpected success - should have failed due to no valid layout!")
        return False
        
    except ValueError as e:
        if "No valid layout" in str(e):
            print(f"✅ Correctly rejected due to no valid layout: {e}")
            return True
        else:
            print(f"❌ Failed for wrong reason: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing new date logic implementation...")
    
    tests = [
        test_new_date_logic,
        test_invalid_timestamp,
        test_no_valid_layout
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print("-" * 50)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            print("-" * 50)
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️  Some tests failed!")

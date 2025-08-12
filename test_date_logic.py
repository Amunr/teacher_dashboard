#!/usr/bin/env python3
"""
Test the hardcoded Column A date logic.

This script tests that:
1. Column A is always used as the date source
2. Hour/minute/second are dropped from the timestamp
3. Layouts are found based on the Column A date, not student birthday
4. No orphaned responses are created
"""

import sys
import os
from datetime import date
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import DatabaseManager, SheetsImportService
from config.config import Config

def test_hardcoded_date_logic():
    """Test that Column A date is hardcoded correctly."""
    print("Testing hardcoded Column A date logic...")
    
    try:
        # Initialize database
        config = Config()
        db = DatabaseManager(config.DATABASE_URL)
        db.initialize_database()
        
        import_service = SheetsImportService(db)
        
        # Test data: Create a row with data in the correct Index_ID positions
        # Based on the valid Index_IDs from the layout, we need columns 17-34
        test_row = [""] * 60  # Create empty row with 60 columns to be safe
        
        # Column A (Index_ID 1) - form timestamp (should be used as Date)
        test_row[0] = "1/7/2025 10:15:12"
        
        # Metadata columns
        test_row[2] = "Teacher A"      # Index_ID 3 - Teacher
        test_row[3] = "School X"       # Index_ID 4 - School  
        test_row[4] = "Student Name"   # Index_ID 5 - Student Name
        test_row[55] = "Year 3"        # Index_ID 56 - Grade
        test_row[56] = "Assessment A"  # Index_ID 57 - Assessment Type
        
        # Some actual question responses (Index_IDs 17-34)
        test_row[16] = "4"             # Index_ID 17 - Walk In a ZIG-ZAG
        test_row[17] = "5"             # Index_ID 18 - Climb Stairs
        test_row[18] = "3"             # Index_ID 19 - throw a ball
        test_row[19] = "4"             # Index_ID 20 - hop 5 times
        
        # Student birthday (not used for Date field anymore)
        test_row[6] = "15/12/2010"     # Index_ID 7 - student birthday
        
        print(f"Test row length: {len(test_row)}")
        print(f"Column A (timestamp): {test_row[0]}")
        print(f"Column G (student birthday): {test_row[6]}")
        print(f"Sample responses: Index_ID 17={test_row[16]}, Index_ID 18={test_row[17]}")
        print(f"Metadata: Teacher={test_row[2]}, School={test_row[3]}, Grade={test_row[55]}")
        
        # Process the row
        res_id = import_service.process_sheet_row(test_row, 1)
        print(f"✅ Successfully processed row, created res_id: {res_id}")
        
        # Check what date was actually stored
        with db.get_connection() as conn:
            from sqlalchemy import select, text
            query = text("SELECT DISTINCT Date FROM responses WHERE \"res-id\" = :res_id")
            result = conn.execute(query, {"res_id": res_id}).fetchall()
            
            if result:
                stored_date = result[0][0]
                print(f"📅 Date stored in database: {stored_date}")
                
                # The stored date should be 2025-07-01 (from "1/7/2025")
                expected_date = date(2025, 7, 1)
                if str(stored_date) == str(expected_date):
                    print("✅ CORRECT: Column A date was used (not student birthday)")
                    return True
                else:
                    print(f"❌ WRONG: Expected {expected_date}, got {stored_date}")
                    return False
            else:
                print("❌ No date found in database")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_orphaned_responses():
    """Test that no orphaned responses are created."""
    print("\nTesting for orphaned responses...")
    
    try:
        config = Config()
        db = DatabaseManager(config.DATABASE_URL)
        db.initialize_database()  # Initialize database
        
        with db.get_connection() as conn:
            from sqlalchemy import text
            
            # Check for orphaned responses
            orphan_query = text("""
                SELECT COUNT(*) as orphan_count 
                FROM responses r 
                WHERE NOT EXISTS (
                    SELECT 1 FROM questions q 
                    WHERE q.Index_ID = r.Index_ID
                )
            """)
            result = conn.execute(orphan_query).fetchone()
            orphan_count = result[0]
            
            print(f"Orphaned responses found: {orphan_count}")
            
            if orphan_count == 0:
                print("✅ CORRECT: No orphaned responses")
                return True
            else:
                print(f"❌ WRONG: Found {orphan_count} orphaned responses")
                
                # Show details of orphaned responses
                detail_query = text("""
                    SELECT r.\"res-id\", r.Index_ID, r.Response, r.Date
                    FROM responses r 
                    WHERE NOT EXISTS (
                        SELECT 1 FROM questions q 
                        WHERE q.Index_ID = r.Index_ID
                    )
                    LIMIT 5
                """)
                details = conn.execute(detail_query).fetchall()
                print("Sample orphaned responses:")
                for row in details:
                    print(f"  res_id: {row[0]}, Index_ID: {row[1]}, Response: {row[2]}, Date: {row[3]}")
                
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_layout_validation():
    """Test that layouts are found correctly based on Column A date."""
    print("\nTesting layout validation...")
    
    try:
        config = Config()
        db = DatabaseManager(config.DATABASE_URL)
        db.initialize_database()  # Initialize database
        
        # Check what layouts exist and their date ranges
        with db.get_connection() as conn:
            from sqlalchemy import text
            
            layout_query = text("""
                SELECT DISTINCT year_start, year_end, COUNT(Index_ID) as question_count
                FROM questions 
                WHERE Domain != 'MetaData'
                GROUP BY year_start, year_end
                ORDER BY year_start
            """)
            layouts = conn.execute(layout_query).fetchall()
            
            print("Available layouts:")
            for layout in layouts:
                print(f"  {layout[0]} to {layout[1]}: {layout[2]} questions")
            
            # Test date: 2025-07-01 (from "1/7/2025")
            test_date = date(2025, 7, 1)
            
            # Find which layout should match this date
            valid_query = text("""
                SELECT COUNT(DISTINCT Index_ID) as valid_questions
                FROM questions 
                WHERE year_start <= :test_date 
                AND year_end >= :test_date 
                AND Domain != 'MetaData'
            """)
            result = conn.execute(valid_query, {"test_date": test_date}).fetchone()
            valid_count = result[0]
            
            print(f"For test date {test_date}: {valid_count} valid questions found")
            
            if valid_count > 0:
                print("✅ CORRECT: Layout found for Column A date")
                return True
            else:
                print("❌ WRONG: No layout found for Column A date")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("HARDCODED COLUMN A DATE LOGIC TESTS")
    print("=" * 60)
    
    tests = [
        ("Date Logic Test", test_hardcoded_date_logic),
        ("Orphaned Responses Test", test_orphaned_responses),
        ("Layout Validation Test", test_layout_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<30} {status}")
    
    print(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Column A date logic is working correctly.")
    else:
        print("⚠️ Some tests failed. The hardcoded date logic needs fixing.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

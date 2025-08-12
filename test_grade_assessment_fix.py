#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import ResponseModel, DatabaseManager
from datetime import date

def test_grade_assessment_fix():
    """Test the fixed Grade and Assessment extraction"""
    
    # Create test data similar to what would come from CSV
    test_data = {
        1: '01/07/2025 10:15:12',  # Column A: Date
        3: 'Test Teacher',         # Column C: Teacher
        4: 'Test School',          # Column D: School  
        5: 'Test Student',         # Column E: Student Name
        17: '1',                   # Sample question response
        18: '0.5',                 # Sample question response
        19: '0',                   # Sample question response
        '_actual_form_date': date(2025, 7, 1)  # Parsed from Column A
    }
    
    print("=== TESTING GRADE AND ASSESSMENT FIX ===")
    print(f"Test data: {test_data}")
    
    try:
        # Initialize database manager and response model
        from config.config import Config
        config = Config()
        db_manager = DatabaseManager(config.DATABASE_URL)
        db_manager.initialize_database()
        response_model = ResponseModel(db_manager)
        
        # Create response
        res_id = response_model.create_response(test_data)
        print(f"✅ Created response with res_id: {res_id}")
        
        # Check the created response
        import sqlite3
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT [res-id], School, Grade, Teacher, Assessment, Name, Date, Index_ID, Response
            FROM responses 
            WHERE [res-id] = ?
            ORDER BY Index_ID
        """, (res_id,))
        
        responses = cursor.fetchall()
        print(f"\nCreated response data:")
        
        # Group by common metadata
        metadata_shown = False
        for res_id_val, school, grade, teacher, assessment, name, date_val, index_id, response in responses:
            if not metadata_shown:
                print(f"  Metadata: School='{school}', Grade='{grade}', Teacher='{teacher}', Assessment='{assessment}', Name='{name}', Date='{date_val}'")
                metadata_shown = True
            print(f"  Index_ID {index_id}: Response='{response}'")
        
        # Check if Grade and Assessment are now populated
        if responses:
            sample_response = responses[0]
            school, grade, teacher, assessment, name, date_val = sample_response[1:7]
            
            if grade and assessment:
                print(f"\n✅ SUCCESS: Grade='{grade}' and Assessment='{assessment}' are now populated!")
            else:
                print(f"\n❌ FAILED: Grade='{grade}' and Assessment='{assessment}' are still empty")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing fix: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_grade_assessment_fix()

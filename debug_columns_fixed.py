#!/usr/bin/env python3

import sqlite3
import csv
import os

def check_actual_sheet_data():
    """Check what's actually in the CSV data for columns that map to Grade and Assessment"""
    
    # Get the most recent CSV file
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found!")
        return
    
    latest_csv = max(csv_files, key=os.path.getctime)
    print(f"Checking CSV file: {latest_csv}")
    
    with open(latest_csv, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    print(f"Total rows in CSV: {len(rows)}")
    print(f"Total columns in first row: {len(rows[0]) if rows else 0}")
    
    # Show first row (headers)
    if rows:
        print(f"\nFirst few columns: {rows[0][:10]}")
        
        # Look for Grade and Assessment related columns
        for i, header in enumerate(rows[0]):
            if 'grade' in header.lower() or 'class' in header.lower():
                print(f"Potential Grade column at index {i}: '{header}'")
            if 'assessment' in header.lower() or 'test' in header.lower() or 'exam' in header.lower():
                print(f"Potential Assessment column at index {i}: '{header}'")
    
    # Check if we have enough columns for Index_IDs 56 and 57
    if rows and len(rows[0]) >= 57:
        print(f"\nColumn at index 55 (Index_ID 56): '{rows[0][55] if len(rows[0]) > 55 else 'NOT FOUND'}'")
        print(f"Column at index 56 (Index_ID 57): '{rows[0][56] if len(rows[0]) > 56 else 'NOT FOUND'}'")
        
        # Check first few data rows
        print("\nFirst few data rows:")
        for i, row in enumerate(rows[1:6], 1):  # First 5 data rows
            if len(row) > 56:
                grade_val = row[55] if len(row) > 55 else "N/A"
                assessment_val = row[56] if len(row) > 56 else "N/A"
                print(f"  Row {i}: Index55='{grade_val}', Index56='{assessment_val}'")
            else:
                print(f"  Row {i}: Not enough columns ({len(row)})")
    else:
        print("CSV doesn't have enough columns for Index_IDs 56 and 57")

def check_database_questions():
    """Check what questions exist for Index_IDs 56 and 57"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT Index_ID, Name, layout_id 
        FROM questions 
        WHERE Index_ID IN (56, 57)
        ORDER BY Index_ID
    """)
    
    questions = cursor.fetchall()
    print(f"\nQuestions for Grade/Assessment Index_IDs:")
    for index_id, name, layout_id in questions:
        print(f"  Index_ID {index_id} (Layout {layout_id}): '{name}'")
    
    # Also check what Index_IDs exist
    cursor.execute("""
        SELECT DISTINCT Index_ID 
        FROM questions 
        ORDER BY Index_ID
    """)
    
    all_indexes = cursor.fetchall()
    print(f"\nAll Index_IDs in questions table: {[row[0] for row in all_indexes]}")
    
    conn.close()

def check_response_creation_logic():
    """Check how responses are being created"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Get the most recent response
    cursor.execute("""
        SELECT MAX([res-id]) FROM responses
    """)
    
    max_res_id = cursor.fetchone()[0]
    print(f"\nMost recent res_id: {max_res_id}")
    
    cursor.execute("""
        SELECT [res-id], Index_ID, Response, School, Grade, Teacher, Assessment, Name, Date
        FROM responses 
        WHERE [res-id] = ?
        ORDER BY Index_ID
    """, (max_res_id,))
    
    responses = cursor.fetchall()
    print(f"\nMost recent response data:")
    for res_id, index_id, response, school, grade, teacher, assessment, name, date in responses:
        print(f"  Index_ID {index_id}: Response='{response}', Grade='{grade}', Assessment='{assessment}'")
    
    conn.close()

def check_metadata_fields():
    """Check what's stored in Grade and Assessment fields"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT Grade, Assessment
        FROM responses
        WHERE Grade != '' OR Assessment != ''
    """)
    
    metadata = cursor.fetchall()
    print(f"\nNon-empty Grade/Assessment values:")
    for grade, assessment in metadata:
        print(f"  Grade: '{grade}', Assessment: '{assessment}'")
    
    if not metadata:
        print("  No non-empty Grade/Assessment values found!")
    
    conn.close()

if __name__ == "__main__":
    print("=== DEBUGGING GRADE AND ASSESSMENT COLUMNS ===")
    check_actual_sheet_data()
    check_database_questions()
    check_response_creation_logic()
    check_metadata_fields()

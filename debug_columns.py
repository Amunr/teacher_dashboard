#!/usr/bin/env python3

import sqlite3
import csv
import os

def check_actual_sheet_data():
    """Check what's actually in the CSV data for Index_IDs 56 and 57"""
    
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
    
    # Check if we have enough columns
    if rows and len(rows[0]) >= 57:
        print(f"\nColumn 56 (Grade) header: '{rows[0][55] if len(rows[0]) > 55 else 'NOT FOUND'}'")
        print(f"Column 57 (Assessment) header: '{rows[0][56] if len(rows[0]) > 56 else 'NOT FOUND'}'")
        
        # Check first few data rows
        print("\nFirst few data rows:")
        for i, row in enumerate(rows[1:6], 1):  # First 5 data rows
            if len(row) > 56:
                grade_val = row[55] if len(row) > 55 else "N/A"
                assessment_val = row[56] if len(row) > 56 else "N/A"
                print(f"  Row {i}: Grade='{grade_val}', Assessment='{assessment_val}'")
            else:
                print(f"  Row {i}: Not enough columns ({len(row)})")
    else:
        print("CSV doesn't have enough columns for Index_IDs 56 and 57")

def check_database_questions():
    """Check what questions exist for Index_IDs 56 and 57"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT q.Index_ID, q.Question_Text, q.layout_id 
        FROM questions q 
        WHERE q.Index_ID IN (56, 57)
        ORDER BY q.Index_ID
    """)
    
    questions = cursor.fetchall()
    print(f"\nQuestions for Grade/Assessment Index_IDs:")
    for index_id, question_text, layout_id in questions:
        print(f"  Index_ID {index_id} (Layout {layout_id}): '{question_text}'")
    
    conn.close()

def check_response_creation_logic():
    """Check how responses are being created"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Get the most recent response
    cursor.execute("""
        SELECT r.res_id, r.Index_ID, r.Response, q.Question_Text
        FROM responses r
        JOIN questions q ON r.Index_ID = q.Index_ID AND r.layout_id = q.layout_id
        WHERE r.res_id = (SELECT MAX(res_id) FROM responses)
        ORDER BY r.Index_ID
    """)
    
    responses = cursor.fetchall()
    print(f"\nMost recent response data:")
    for res_id, index_id, response, question_text in responses:
        if index_id in [56, 57]:
            print(f"  Index_ID {index_id}: Response='{response}', Question='{question_text}'")
    
    conn.close()

if __name__ == "__main__":
    print("=== DEBUGGING GRADE AND ASSESSMENT COLUMNS ===")
    check_actual_sheet_data()
    check_database_questions()
    check_response_creation_logic()

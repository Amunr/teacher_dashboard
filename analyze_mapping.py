#!/usr/bin/env python3

import sqlite3

def analyze_column_mapping():
    """Analyze the relationship between CSV columns and metadata"""
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    print("=== COMPLETE METADATA ANALYSIS ===")
    
    # Get all metadata Index_IDs and their names
    cursor.execute("""
        SELECT Index_ID, Name, Domain, SubDomain
        FROM questions 
        WHERE Domain = 'MetaData'
        ORDER BY Index_ID
    """)
    
    metadata_questions = cursor.fetchall()
    print("MetaData Index_IDs:")
    for index_id, name, domain, subdomain in metadata_questions:
        print(f"  Index_ID {index_id}: '{name}' (Domain: {domain}, SubDomain: '{subdomain}')")
    
    # Based on existing hardcoded logic, here's what we know:
    print("\n=== CURRENT HARDCODED COLUMN MAPPING ===")
    print("From create_response() method:")
    print("  Column 1 (Index_ID 1): Date (hardcoded from Column A)")
    print("  Column 3 (Index_ID 3): Teacher Name")
    print("  Column 4 (Index_ID 4): School")
    print("  Column 5 (Index_ID 5): Student Name")
    print("  Column ? (Index_ID 56): Grade - UNKNOWN COLUMN")
    print("  Column ? (Index_ID 57): Assessment Type - UNKNOWN COLUMN")
    
    # Check sample data to understand structure
    cursor.execute("""
        SELECT [res-id], School, Grade, Teacher, Assessment, Name, Date, Index_ID, Response
        FROM responses 
        WHERE [res-id] = (SELECT MAX([res-id]) FROM responses)
        ORDER BY Index_ID
        LIMIT 5
    """)
    
    sample_responses = cursor.fetchall()
    print(f"\n=== SAMPLE RESPONSE DATA ===")
    print("Recent response data:")
    for res_id, school, grade, teacher, assessment, name, date, index_id, response in sample_responses:
        print(f"  Index_ID {index_id}: Response='{response}', School='{school}', Grade='{grade}', Teacher='{teacher}', Assessment='{assessment}', Name='{name}', Date='{date}'")
    
    conn.close()

def suggest_fix():
    """Suggest the fix for Grade and Assessment column mapping"""
    print("\n=== PROBLEM DIAGNOSIS ===")
    print("The issue is that Grade and Assessment fields are empty because:")
    print("1. Index_IDs 56 and 57 exist in the questions table for Grade and Assessment")
    print("2. But the create_response() method tries to find them in data[56] and data[57]")
    print("3. However, data[] contains column positions (1, 2, 3, etc.), not Index_IDs")
    print("4. So data[56] and data[57] don't exist unless the CSV has 56+ columns")
    
    print("\n=== SOLUTION ===")
    print("We need to determine which CSV COLUMNS contain Grade and Assessment data:")
    print("Option 1: Check the actual CSV file to see which columns have Grade/Assessment")
    print("Option 2: Update the hardcoded mapping to use the correct column positions")
    print("Option 3: Map Index_ID 56 -> correct column position for Grade")
    print("         Map Index_ID 57 -> correct column position for Assessment")

if __name__ == "__main__":
    analyze_column_mapping()
    suggest_fix()
